"""Message flow implementation for type-safe routing.

Provides an explicit routing API for building message-driven workflows where
messages are routed based on their types. Uses strategic type erasure at
routing boundaries to handle union types while maintaining type safety at
flow input/output boundaries.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast, final, override

from clearflow.message import Message
from clearflow.message_node import Node

__all__ = [
    "message_flow",
]

MessageRouteKey = tuple[type[Message], str]  # (outcome, node_name)


@final
@dataclass(frozen=True, kw_only=True)
class MessageFlow[TStartMessage: Message, TEndMessage: Message](Node[TStartMessage, TEndMessage]):
    """Message flow that routes messages based on their types.

    Executes flows by routing messages through nodes based on their runtime types.
    Being a Node allows flows to be composed within other flows.

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

    @override
    async def process(self, message: TStartMessage) -> TEndMessage:
        """Process message by routing through the flow.

        Args:
            message: Initial message to start the flow

        Returns:
            Final message when flow reaches termination

        Raises:
            ValueError: If no route is defined for a message type from a node.

        """
        current_node = self.start_node
        current_message: Message = message

        while True:
            # Execute node
            output_message = await current_node.process(current_message)

            # Create route key
            route_key = (type(output_message), current_node.name)

            # Raise error if no route defined - all message types must be explicitly handled
            if route_key not in self.routes:
                msg = (
                    f"No route defined for message type '{output_message.__class__.__name__}' "
                    f"from node '{current_node.name}'"
                )
                raise ValueError(msg)

            # Check next node
            next_node = self.routes[route_key]
            if next_node is None:
                return cast("TEndMessage", output_message)

            # Continue
            current_node = next_node
            current_message = output_message


@final
@dataclass(frozen=True, kw_only=True)
class _MessageFlowBuilder[TStartMessage: Message, TStartOut: Message]:
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

    _name: str
    _start_node: Node[TStartMessage, TStartOut]
    _routes: MappingProxyType[MessageRouteKey, Node[Message, Message] | None]
    _reachable_nodes: frozenset[str]  # Node names that are reachable from start

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

    def route[TFromIn: Message, TFromOut: Message, TToIn: Message, TToOut: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        outcome: type[Message],
        to_node: Node[TToIn, TToOut],
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
        new_routes = {**self._routes, route_key: cast("Node[Message, Message]", to_node)}
        new_reachable = self._reachable_nodes | {to_node.name}

        return _MessageFlowBuilder[TStartMessage, TStartOut](
            _name=self._name,
            _start_node=self._start_node,
            _routes=MappingProxyType(new_routes),
            _reachable_nodes=new_reachable,
        )

    def end[TFromIn: Message, TFromOut: Message, TEndMessage: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
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
            start_node=cast("Node[Message, Message]", self._start_node),
            routes=MappingProxyType(new_routes),
        )


def message_flow[TStartMessage: Message, TStartOut: Message](
    name: str,
    start_node: Node[TStartMessage, TStartOut],
) -> _MessageFlowBuilder[TStartMessage, TStartOut]:
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
    return _MessageFlowBuilder[TStartMessage, TStartOut](
        _name=name,
        _start_node=start_node,
        _routes=MappingProxyType({}),
        _reachable_nodes=frozenset({start_node.name}),
    )
