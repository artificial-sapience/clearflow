"""Message flow implementation for type-safe routing.

Provides an explicit routing API for building message-driven workflows where
messages are routed based on their types. Uses strategic type erasure at
routing boundaries to handle union types while maintaining type safety at
flow input/output boundaries.
"""

import types
from dataclasses import dataclass
from typing import TypeVar, cast, final, get_args, get_type_hints, override

from clearflow._internal.callback_handler import CallbackHandler
from clearflow.flow import FlowBuilder
from clearflow.message import Message
from clearflow.node import Node, NodeInterface
from clearflow.observer import Observer

__all__ = [
    "create_flow",
]

RouteKey = tuple[NodeInterface[Message, Message], type[Message]]  # (from_node, outcome)
RouteEntry = tuple[RouteKey, NodeInterface[Message, Message] | None]  # (key, destination)


def _get_node_output_types(node: NodeInterface[Message, Message]) -> tuple[type[Message], ...]:
    """Get valid output types for a node.

    Returns:
        Tuple of valid output message types, empty if not determinable.

    """
    try:
        hints = get_type_hints(node.process)
    except (NameError, AttributeError):
        return ()

    if "return" not in hints:
        return ()

    return_type = hints["return"]

    # Skip validation for TypeVars (generic parameters)
    if isinstance(return_type, TypeVar):
        return ()

    # Python 3.10+ union syntax (X | Y) creates types.UnionType
    if isinstance(return_type, types.UnionType):
        return get_args(return_type)
    return (return_type,)


def _get_node_input_types(node: NodeInterface[Message, Message]) -> tuple[type[Message], ...]:
    """Get expected input types for a node.

    Returns:
        Tuple of valid input message types, empty if not determinable.

    """
    try:
        hints = get_type_hints(node.process)
    except (NameError, AttributeError):
        return ()

    if "message" not in hints:
        return ()

    input_type = hints["message"]

    # Skip validation for TypeVars (generic parameters)
    if isinstance(input_type, TypeVar):
        return ()

    # Python 3.10+ union syntax (X | Y) creates types.UnionType
    if isinstance(input_type, types.UnionType):
        return get_args(input_type)
    return (input_type,)


def _validate_output_type(from_node: NodeInterface[Message, Message], outcome: type[Message]) -> None:
    """Validate that outcome is a valid output from source node.

    Raises:
        TypeError: If outcome is not a valid output type for the node.

    """
    valid_outputs = _get_node_output_types(from_node)
    if valid_outputs and outcome not in valid_outputs:
        valid_names = ", ".join(t.__name__ for t in valid_outputs if hasattr(t, "__name__"))
        from_node_name = type(from_node).__name__
        msg = f"Node '{from_node_name}' cannot output {outcome.__name__}. Valid outputs: {valid_names}"
        raise TypeError(msg)


def _is_type_compatible(outcome: type[Message], valid_inputs: tuple[type[Message], ...]) -> bool:
    """Check if outcome is compatible with any of the valid input types.

    Returns:
        True if outcome is compatible with any valid input type, False otherwise.

    """
    return any(issubclass(outcome, input_t) for input_t in valid_inputs)


def _validate_input_type(to_node: NodeInterface[Message, Message], outcome: type[Message]) -> None:
    """Validate that outcome is acceptable input to destination node.

    Raises:
        TypeError: If outcome is not an acceptable input type for the node.

    """
    valid_inputs = _get_node_input_types(to_node)
    if valid_inputs and not _is_type_compatible(outcome, valid_inputs):
        to_node_name = type(to_node).__name__
        valid_names = ", ".join(t.__name__ for t in valid_inputs if hasattr(t, "__name__"))
        msg = f"Node '{to_node_name}' cannot accept {outcome.__name__} (expects {valid_names})"
        raise TypeError(msg)


def _validate_route_types(
    from_node: NodeInterface[Message, Message],
    outcome: type[Message],
    to_node: NodeInterface[Message, Message],
) -> None:
    """Validate message type compatibility between nodes.

    Args:
        from_node: Source node
        outcome: Message type being routed
        to_node: Destination node

    """
    _validate_output_type(from_node, outcome)
    _validate_input_type(to_node, outcome)


@final
class _Flow[TStartIn: Message, TEnd: Message](Node[TStartIn, TEnd]):
    """Module private flow that routes messages based on their types.

    Executes flows by routing messages through nodes based on their runtime types.

    The flow uses type erasure internally at routing boundaries to handle complex
    type patterns like union types, while maintaining type safety at the flow's
    external boundaries (input/output).

    """

    starting_node: NodeInterface[Message, Message]
    routes: tuple[RouteEntry, ...]
    callbacks: CallbackHandler | None = None  # REQ-009: Optional callbacks parameter

    async def _safe_callback(self, method: str, *args: str | Message | Exception | None) -> None:
        """Execute callback safely without affecting flow.

        REQ-016: Zero overhead when no callbacks
        REQ-017: Async execution (non-blocking)

        CallbackHandler internally handles all errors (REQ-005, REQ-006) so we don't
        need additional error handling here.

        Args:
            method: Name of callback method to invoke
            *args: Arguments to pass to the callback method (flow_name, node_name, message, error)

        """
        if not self.callbacks:  # REQ-016: Zero overhead when no callbacks
            return

        # CallbackHandler already provides error isolation, so we can call directly
        callback_method = getattr(self.callbacks, method)
        await callback_method(*args)

    async def _execute_node(self, node: NodeInterface[Message, Message], message: Message) -> Message:
        """Execute a single node with callback notifications.

        Args:
            node: The node to execute
            message: The message to process

        Returns:
            The output message from the node

        """
        # REQ-010: Invoke on_node_start before node execution
        # Cast to Node since all our nodes are Node instances with a name field
        node_name = cast("Node[Message, Message]", node).name
        await self._safe_callback("on_node_start", node_name, message)

        try:
            output = await node.process(message)
        except Exception as error:
            # REQ-010: Invoke on_node_end with error
            await self._safe_callback("on_node_end", node_name, message, error)
            raise
        else:
            # REQ-010: Invoke on_node_end after successful node execution
            await self._safe_callback("on_node_end", node_name, output, None)
            return output

    def _get_next_node(
        self, message: Message, current_node: NodeInterface[Message, Message]
    ) -> NodeInterface[Message, Message] | None:
        """Get the next node for routing based on message type.

        Args:
            message: The message to route
            current_node: The current node

        Returns:
            The next node or None if terminal

        Raises:
            ValueError: If no route is defined for the message type

        """
        route_key = (current_node, type(message))

        # Linear search is fine for small route tables (typically <10 routes)
        for key, destination in self.routes:
            if key == route_key:
                return destination

        # Route not found
        node_name = type(current_node).__name__
        msg = f"No route defined for message type '{message.__class__.__name__}' from node '{node_name}'"
        raise ValueError(msg)

    @override
    async def process(self, message: TStartIn) -> TEnd:
        """Process message by routing through the flow.

        Args:
            message: Initial message to start the flow

        Returns:
            Final message when flow reaches termination

        """
        # REQ-010: Invoke on_flow_start at beginning
        await self._safe_callback("on_flow_start", self.name, message)

        current_node: NodeInterface[Message, Message] = self.starting_node
        current_message: Message = message

        try:
            while True:
                # Execute node with callbacks
                output_message = await self._execute_node(current_node, current_message)

                # Get next node
                next_node = self._get_next_node(output_message, current_node)

                if next_node is None:
                    # REQ-010: Invoke on_flow_end at termination
                    await self._safe_callback("on_flow_end", self.name, output_message, None)
                    return cast("TEnd", output_message)

                # Continue
                current_node = next_node
                current_message = output_message
        except Exception as error:
            # REQ-010: Invoke on_flow_end with error
            await self._safe_callback("on_flow_end", self.name, current_message, error)
            raise


@final
@dataclass(frozen=True)
class _FlowBuilder[TStartIn: Message, TStartOut: Message](FlowBuilder[TStartIn, TStartOut]):
    """Module private builder for composing message routes with explicit source nodes.

    Uses the pattern from the original flow API where each route explicitly
    specifies: from_node -> outcome -> to_node. This enables sequential thinking
    about workflow construction.

    Type parameters:
        TStartIn: The input message type the flow accepts
        TStartOut: The output type of the start node (remains constant throughout builder chain)

    The builder maintains stable type parameters throughout the chain, unlike tracking
    current message types, because type erasure makes intermediate types meaningless.

    Call end() to specify where the flow terminates and get the completed flow.
    """

    name: str
    starting_node: Node[TStartIn, TStartOut]
    routes: tuple[RouteEntry, ...]
    reachable_nodes: frozenset[str]  # Node names that are reachable from start
    callbacks: CallbackHandler | None = None  # REQ-009: Optional callbacks

    def _check_node_reachability[TIn: Message, TOut: Message](
        self, from_node: Node[TIn, TOut], *, is_termination: bool
    ) -> None:
        """Check if a node is reachable from the start node.

        Raises:
            ValueError: If the node is not reachable from the start node.

        """
        from_node_name = getattr(from_node, "name", type(from_node).__name__)
        if from_node_name not in self.reachable_nodes:
            action = "end at" if is_termination else "route from"
            msg = f"Cannot {action} node '{from_node_name}' - not reachable from start"
            raise ValueError(msg)

    def _check_duplicate_route[TIn: Message, TOut: Message](
        self, route_key: RouteKey, from_node: Node[TIn, TOut], outcome: type[Message]
    ) -> None:
        """Check if a route already exists.

        Raises:
            ValueError: If the route already exists.

        """
        for existing_key, _ in self.routes:
            if existing_key == route_key:
                from_node_name = type(from_node).__name__
                msg = f"Route already defined for message type '{outcome.__name__}' from node '{from_node_name}'"
                raise ValueError(msg)

    def _validate_and_create_route[TFromIn: Message, TFromOut: Message, TToIn: Message, TToOut: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        outcome: type[Message],
        to_node: Node[TToIn, TToOut] | None = None,
        *,
        is_termination: bool = False,
    ) -> RouteKey:
        """Validate that a route can be added with type checking.

        Args:
            from_node: The node this route originates from
            outcome: The message type that triggers this route
            to_node: The destination node (None for termination)
            is_termination: Whether this is a termination route

        Returns:
            The route key for this route

        """
        # Check reachability
        self._check_node_reachability(from_node, is_termination=is_termination)

        # Create route key
        route_key: RouteKey = (cast("NodeInterface[Message, Message]", from_node), outcome)

        # Check for duplicate routes
        self._check_duplicate_route(route_key, from_node, outcome)

        # Type validation for non-termination routes
        if not is_termination and to_node:
            _validate_route_types(
                cast("NodeInterface[Message, Message]", from_node),
                outcome,
                cast("NodeInterface[Message, Message]", to_node),
            )

        return route_key

    @override
    def observe(self, *observers: Observer) -> "_FlowBuilder[TStartIn, TStartOut]":
        """Attach observers to the flow.

        REQ-009: MessageFlow accepts optional observers
        REQ-016: Zero overhead when no observers

        Args:
            *observers: Observer instances to monitor flow execution

        Returns:
            Builder for continued configuration

        """
        # Create internal handler with observers
        handler = CallbackHandler(observers) if observers else self.callbacks
        return _FlowBuilder[TStartIn, TStartOut](
            name=self.name,
            starting_node=self.starting_node,
            routes=self.routes,
            reachable_nodes=self.reachable_nodes,
            callbacks=handler,
        )

    @override
    def route[TFromIn: Message, TFromOut: Message, TToIn: Message, TToOut: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        outcome: type[Message],
        to_node: Node[TToIn, TToOut],
    ) -> "_FlowBuilder[TStartIn, TStartOut]":
        """Route specific message type from source node to destination.

        Explicitly specifies that when `from_node` produces a message of type `outcome`,
        route it to `to_node`. This matches the original flow API pattern for clarity.

        Type Erasure Rationale:
            Python's type system cannot express "route only this specific type from
            a union to the next node." For example, if a node outputs
            UserMessage | SystemMessage, we cannot type-check at compile time that
            only UserMessage goes to a specific handler. We use type erasure
            (outcome: type[Message]) to allow this flexibility while maintaining
            runtime validation.

        Args:
            from_node: Source node that may emit the outcome message type
            outcome: Specific message type that triggers this route
            to_node: Destination node that accepts this message type

        Returns:
            Builder for continued route definition

        """
        route_key = self._validate_and_create_route(from_node, outcome, to_node)

        # Add route and mark to_node as reachable
        new_route_entry: RouteEntry = (route_key, cast("NodeInterface[Message, Message]", to_node))
        new_routes = (*self.routes, new_route_entry)
        # For flows used as nodes, use their name property
        to_node_name = getattr(to_node, "name", type(to_node).__name__)
        new_reachable = self.reachable_nodes | {to_node_name}

        return _FlowBuilder[TStartIn, TStartOut](
            name=self.name,
            starting_node=self.starting_node,
            routes=new_routes,
            reachable_nodes=new_reachable,
            callbacks=self.callbacks,
        )

    @override
    def complete_flow[TFromIn: Message, TFromOut: Message, TEnd: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        final_outcome: type[TEnd],
    ) -> Node[TStartIn, TEnd]:
        """Mark message type as terminal from source node.

        Args:
            from_node: Source node that emits the terminal message type
            final_outcome: The message type that completes the flow

        Returns:
            A Node that represents the complete flow

        """
        route_key = self._validate_and_create_route(from_node, final_outcome, is_termination=True)

        # Add termination route
        new_route_entry: RouteEntry = (route_key, None)
        new_routes = (*self.routes, new_route_entry)

        return _Flow[TStartIn, TEnd](
            name=self.name,
            starting_node=cast("NodeInterface[Message, Message]", self.starting_node),
            routes=new_routes,
            callbacks=self.callbacks,  # REQ-009: Pass callbacks to MessageFlow
        )


def create_flow[TStartIn: Message, TStartOut: Message](
    name: str,
    starting_node: Node[TStartIn, TStartOut],
) -> FlowBuilder[TStartIn, TStartOut]:
    """Create a flow with type-safe routing.

    This is the entry point for building message-driven workflows. The flow
    starts at the given node and routes messages based on their types.

    Args:
        name: The name of the flow for identification and debugging
        starting_node: The starting node that processes TStartIn

    Returns:
        Builder for defining a flow

    """
    return _FlowBuilder[TStartIn, TStartOut](
        name=name,
        starting_node=starting_node,
        routes=(),  # Empty tuple of routes
        reachable_nodes=frozenset({starting_node.name}),
        callbacks=None,  # REQ-016: Zero overhead when no callbacks attached
    )
