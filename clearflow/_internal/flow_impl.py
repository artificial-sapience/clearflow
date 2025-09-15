"""Message flow implementation for type-safe routing.

Provides an explicit routing API for building message-driven workflows where
messages are routed based on their types. Uses strategic type erasure at
routing boundaries to handle union types while maintaining type safety at
flow input/output boundaries.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast, final, override

from clearflow._internal.callback_handler import CallbackHandler
from clearflow.flow import FlowBuilder
from clearflow.message import Message
from clearflow.node import Node, NodeInterface
from clearflow.observer import Observer

__all__ = [
    "create_flow",
]

RouteKey = tuple[type[Message], str]  # (outcome, node_name)


@final
class _Flow[TStartIn: Message, TEnd: Message](Node[TStartIn, TEnd]):
    """Module private flow that routes messages based on their types.

    Executes flows by routing messages through nodes based on their runtime types.

    The flow uses type erasure internally at routing boundaries to handle complex
    type patterns like union types, while maintaining type safety at the flow's
    external boundaries (input/output).

    """

    starting_node: NodeInterface[Message, Message]
    routes: Mapping[RouteKey, NodeInterface[Message, Message] | None]
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
        # Cast to Node since all our nodes are Node instances with a name field
        node_name = cast("Node[Message, Message]", current_node).name
        route_key = (type(message), node_name)
        if route_key not in self.routes:
            msg = f"No route defined for message type '{message.__class__.__name__}' from node '{node_name}'"
            raise ValueError(msg)
        return self.routes[route_key]

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
    routes: Mapping[RouteKey, NodeInterface[Message, Message] | None]
    reachable_nodes: frozenset[str]  # Node names that are reachable from start
    callbacks: CallbackHandler | None = None  # REQ-009: Optional callbacks

    def _validate_and_create_route(
        self, from_node_name: str, outcome: type[Message], *, is_termination: bool = False
    ) -> RouteKey:
        """Validate that a route can be added.

        Args:
            from_node_name: The name of the node this route originates from
            outcome: The message type that triggers this route
            is_termination: Whether this is a termination route

        Returns:
            The route key for this route

        Raises:
            ValueError: If from_node is not reachable or route already exists

        """
        # Check reachability
        if from_node_name not in self.reachable_nodes:
            action = "end at" if is_termination else "route from"
            msg = f"Cannot {action} node '{from_node_name}' - not reachable from start"
            raise ValueError(msg)

        # Check for duplicate routes
        route_key: RouteKey = (outcome, from_node_name)
        if route_key in self.routes:
            msg = f"Route already defined for message type '{outcome.__name__}' from node '{from_node_name}'"
            raise ValueError(msg)

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
        route_key = self._validate_and_create_route(from_node.name, outcome)

        # Add route and mark to_node as reachable
        new_routes = {**self.routes, route_key: cast("NodeInterface[Message, Message]", to_node)}
        new_reachable = self.reachable_nodes | {to_node.name}

        return _FlowBuilder[TStartIn, TStartOut](
            name=self.name,
            starting_node=self.starting_node,
            routes=new_routes,
            reachable_nodes=new_reachable,
            callbacks=self.callbacks,
        )

    @override
    def end[TFromIn: Message, TFromOut: Message, TEnd: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        outcome: type[TEnd],
    ) -> Node[TStartIn, TEnd]:
        """Mark message type as terminal from source node.

        Args:
            from_node: Source node that emits the terminal message type
            outcome: The message type that completes the flow

        Returns:
            A Node that represents the complete flow

        """
        route_key = self._validate_and_create_route(from_node.name, outcome, is_termination=True)

        # Add termination route
        new_routes = {**self.routes, route_key: None}

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
        routes={},
        reachable_nodes=frozenset({starting_node.name}),
        callbacks=None,  # REQ-016: Zero overhead when no callbacks attached
    )
