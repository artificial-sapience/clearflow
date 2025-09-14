"""Message flow implementation for type-safe routing.

Provides an explicit routing API for building message-driven workflows where
messages are routed based on their types. Uses strategic type erasure at
routing boundaries to handle union types while maintaining type safety at
flow input/output boundaries.
"""

import sys
from collections.abc import Mapping
from typing import cast, final

from pydantic import ConfigDict, Field

from clearflow.callbacks import CallbackHandler
from clearflow.message import Message
from clearflow.message_node import Node
from clearflow.strict_base_model import StrictBaseModel

__all__ = [
    "MessageFlow",
    "message_flow",
]

MessageRouteKey = tuple[type[Message], str]  # (outcome, node_name)


@final
class MessageFlow[TStartMessage: Message, TEndMessage: Message](StrictBaseModel):
    """Message flow that routes messages based on their types.

    Executes flows by routing messages through nodes based on their runtime types.

    The flow uses type erasure internally at routing boundaries to handle complex
    type patterns like union types, while maintaining type safety at the flow's
    external boundaries (input/output).

    Attributes:
        name: Unique identifier for this flow
        start_node: The entry point node that processes initial messages
        routes: Mapping from (message_type, node_name) to next node or None for termination

    """

    name: str
    start_node: Node[Message, Message]
    routes: Mapping[MessageRouteKey, Node[Message, Message] | None]
    callbacks: CallbackHandler | None = None  # REQ-009: Optional callbacks parameter

    async def _safe_callback(self, method: str, *args: str | Message | Exception | None) -> None:
        """Execute callback safely without affecting flow.

        REQ-005: Wrap callback execution in try-except
        REQ-006: Log errors to stderr but don't propagate
        REQ-017: Async execution (non-blocking)

        Args:
            method: Name of callback method to invoke
            *args: Arguments to pass to the callback method (flow_name, node_name, message, error)

        """
        if not self.callbacks:  # REQ-016: Zero overhead when no callbacks
            return

        try:
            callback_method = getattr(self.callbacks, method)
            await callback_method(*args)
        except Exception as e:  # noqa: BLE001  # REQ-005: Must catch all exceptions to prevent flow disruption
            # REQ-006: Log but don't propagate
            sys.stderr.write(f"Callback {method} failed: {e}\n")

    async def _execute_node(self, node: Node[Message, Message], message: Message) -> Message:
        """Execute a single node with callback notifications.

        Args:
            node: The node to execute
            message: The message to process

        Returns:
            The output message from the node

        """
        # REQ-010: Invoke on_node_start before node execution
        await self._safe_callback("on_node_start", node.name, message)

        try:
            output = await node.process(message)
        except Exception as error:
            # REQ-010: Invoke on_node_end with error
            await self._safe_callback("on_node_end", node.name, message, error)
            raise
        else:
            # REQ-010: Invoke on_node_end after successful node execution
            await self._safe_callback("on_node_end", node.name, output, None)
            return output

    def _get_next_node(self, message: Message, current_node: Node[Message, Message]) -> Node[Message, Message] | None:
        """Get the next node for routing based on message type.

        Args:
            message: The message to route
            current_node: The current node

        Returns:
            The next node or None if terminal

        Raises:
            ValueError: If no route is defined for the message type

        """
        route_key = (type(message), current_node.name)
        if route_key not in self.routes:
            msg = f"No route defined for message type '{message.__class__.__name__}' from node '{current_node.name}'"
            raise ValueError(msg)
        return self.routes[route_key]

    async def process(self, message: TStartMessage) -> TEndMessage:
        """Process message by routing through the flow.

        Args:
            message: Initial message to start the flow

        Returns:
            Final message when flow reaches termination

        """
        # REQ-010: Invoke on_flow_start at beginning
        await self._safe_callback("on_flow_start", self.name, message)

        current_node = self.start_node
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
                    return cast("TEndMessage", output_message)

                # Continue
                current_node = next_node
                current_message = output_message
        except Exception as error:
            # REQ-010: Invoke on_flow_end with error
            await self._safe_callback("on_flow_end", self.name, current_message, error)
            raise


@final
class _MessageFlowBuilder[TStartMessage: Message, TStartOut: Message](StrictBaseModel):
    """Builder for composing message routes with explicit source nodes.

    Uses the pattern from the original flow API where each route explicitly
    specifies: from_node -> outcome -> to_node. This enables sequential thinking
    about workflow construction.

    Type parameters:
        TStartMessage: The input message type the flow accepts
        TStartOut: The output type of the start node (remains constant throughout builder chain)

    The builder maintains stable type parameters throughout the chain, unlike tracking
    current message types, because type erasure makes intermediate types meaningless.

    Call end() to specify where the flow terminates and get the completed flow.
    """

    _name: str = Field(alias="name")
    _start_node: Node[Message, Message] = Field(alias="start_node")  # At runtime, this is type-erased
    _routes: Mapping[MessageRouteKey, Node[Message, Message] | None] = Field(alias="routes")
    _reachable_nodes: frozenset[str] = Field(alias="reachable_nodes")  # Node names that are reachable from start
    _callbacks: CallbackHandler | None = Field(default=None, alias="callbacks")  # REQ-009: Optional callbacks

    def _validate_and_create_route(
        self, from_node_name: str, outcome: type[Message], *, is_termination: bool = False
    ) -> MessageRouteKey:
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
        if from_node_name not in self._reachable_nodes:
            action = "end at" if is_termination else "route from"
            msg = f"Cannot {action} node '{from_node_name}' - not reachable from start"
            raise ValueError(msg)

        # Check for duplicate routes
        route_key: MessageRouteKey = (outcome, from_node_name)
        if route_key in self._routes:
            msg = f"Route already defined for message type '{outcome.__name__}' from node '{from_node_name}'"
            raise ValueError(msg)

        return route_key

    def with_callbacks(self, handler: CallbackHandler) -> "_MessageFlowBuilder[TStartMessage, TStartOut]":
        """Attach callback handler to the flow.

        REQ-009: MessageFlow accepts optional callbacks parameter
        REQ-016: Zero overhead when callbacks is None

        Args:
            handler: Callback handler to observe flow execution

        Returns:
            Builder for continued configuration

        """
        return _MessageFlowBuilder[TStartMessage, TStartOut](
            name=self._name,
            start_node=self._start_node,
            routes=self._routes,
            reachable_nodes=self._reachable_nodes,
            callbacks=handler,
        )

    def route(
        self,
        from_node: Node[Message, Message],
        outcome: type[Message],
        to_node: Node[Message, Message],
    ) -> "_MessageFlowBuilder[TStartMessage, TStartOut]":
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
        new_routes = {**self._routes, route_key: to_node}
        new_reachable = self._reachable_nodes | {to_node.name}

        return _MessageFlowBuilder[TStartMessage, TStartOut](
            name=self._name,
            start_node=self._start_node,
            routes=new_routes,
            reachable_nodes=new_reachable,
            callbacks=self._callbacks,
        )

    def end[TEndMessage: Message](
        self,
        from_node: Node[Message, Message],
        outcome: type[TEndMessage],
    ) -> MessageFlow[TStartMessage, TEndMessage]:
        """Mark message type as terminal from source node.

        Args:
            from_node: Source node that emits the terminal message type
            outcome: The message type that completes the flow

        Returns:
            A MessageFlow that represents the complete flow (for composability)

        """
        route_key = self._validate_and_create_route(from_node.name, outcome, is_termination=True)

        # Add termination route
        new_routes = {**self._routes, route_key: None}

        return MessageFlow[TStartMessage, TEndMessage](
            name=self._name,
            start_node=self._start_node,
            routes=new_routes,
            callbacks=self._callbacks,  # REQ-009: Pass callbacks to MessageFlow
        )


def message_flow(
    name: str,
    start_node: Node[Message, Message],  # At runtime, accepts any node
) -> _MessageFlowBuilder[Message, Message]:
    """Create a message flow with explicit routing.

    This is the entry point for building message-driven workflows. The flow
    starts at the given node and routes messages based on their types.

    Design Decision - Explicit Source Nodes:
        Following the original flow API pattern, we use explicit source nodes
        in routing (from_node, outcome, to_node) rather than grouping routes
        by source. This enables more natural, sequential thinking about workflows.

    Args:
        name: The name of the flow for identification and debugging
        start_node: The starting node that processes TStartMessage

    Returns:
        Builder for route definition and flow completion

    """
    return _MessageFlowBuilder[Message, Message](
        name=name,
        start_node=start_node,
        routes={},
        reachable_nodes=frozenset({start_node.name}),
        callbacks=None,  # REQ-016: Zero overhead when no callbacks attached
    )
