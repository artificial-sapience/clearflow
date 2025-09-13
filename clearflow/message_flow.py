"""Message flow implementation for type-safe routing."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast, final, override

from clearflow.message import Message
from clearflow.message_node import Node

__all__ = [
    "message_flow",
]

MessageRouteKey = tuple[type[Message], str]  # (message_type, node_name)


@final
@dataclass(frozen=True, kw_only=True)
class MessageFlow[TStartMessage: Message, TEndMessage: Message](Node[TStartMessage, TEndMessage]):
    """Private message flow that is also a Node for composability.

    Executes flows by routing messages based on their types to appropriate nodes.
    Maintains type safety through compile-time checking of message compatibility.
    Being a Node allows flows to be nested within other flows.
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
class _MessageFlowBuilderContext[TStartMessage: Message, TCurrentMessage: Message]:
    """Context for routing from a specific node in the flow.

    Provides route() and end() methods that know which node they're routing from.
    """

    _builder: "_MessageFlowBuilder[TStartMessage, TCurrentMessage]"
    _from_node: Node[Message, Message]

    def route[TRouteMessage: Message, TNextMessage: Message](
        self,
        message_type: type[TRouteMessage],
        to_node: Node[TRouteMessage, TNextMessage],
    ) -> "_MessageFlowBuilderContext[TStartMessage, TNextMessage]":
        """Route message type from the context node to destination.

        Args:
            message_type: Message type that triggers this route
            to_node: Destination node that will process the message type

        Returns:
            Context for continued route definition from the same node

        """
        # Create new builder with the route
        new_builder = self._builder.add_route(
            self._from_node.name, message_type, cast("Node[Message, TNextMessage]", to_node)
        )

        # Return new context with updated builder
        return _MessageFlowBuilderContext[TStartMessage, TNextMessage](
            _builder=new_builder,
            _from_node=self._from_node,
        )

    def end(self, message_type: type[TCurrentMessage]) -> MessageFlow[TStartMessage, TCurrentMessage]:
        """Mark message type as terminal from the context node.

        Args:
            message_type: The message type that completes the flow

        Returns:
            A MessageFlow that represents the complete flow (for composability)

        """
        result = self._builder.add_termination(self._from_node.name, message_type)
        return cast("MessageFlow[TStartMessage, TCurrentMessage]", result)

    def from_node[TNodeIn: Message, TNodeOut: Message](
        self, node: Node[TNodeIn, TNodeOut]
    ) -> "_MessageFlowBuilderContext[TStartMessage, TNodeOut]":
        """Switch context to route from a different node.

        Args:
            node: The node to route from

        Returns:
            Context for routing from the specified node

        """
        return _MessageFlowBuilderContext[TStartMessage, TNodeOut](
            _builder=cast("_MessageFlowBuilder[TStartMessage, TNodeOut]", self._builder),
            _from_node=cast("Node[Message, Message]", node),
        )


@final
@dataclass(frozen=True, kw_only=True)
class _MessageFlowBuilder[TStartMessage: Message, TCurrentMessage: Message]:
    """Private builder for composing type-safe message routes.

    Type parameters:
        TStartMessage: The input message type the flow accepts
        TCurrentMessage: The current message type in the flow

    Call end() to specify where the flow terminates and get the completed flow as a Node.
    """

    _name: str
    _start_node: Node[TStartMessage, Message]
    _routes: MappingProxyType[MessageRouteKey, Node[Message, Message] | None]
    _reachable_nodes: frozenset[str]  # Node names that are reachable from start

    def _validate_and_create_route(
        self, message_type: type[Message], from_node_name: str, *, is_termination: bool = False
    ) -> MessageRouteKey:
        """Validate that a route can be added.

        Args:
            message_type: The message type that triggers this route
            from_node_name: Name of the node this route originates from
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
        route_key: MessageRouteKey = (message_type, from_node_name)
        if route_key in self._routes:
            msg = f"Route already defined for message type '{message_type.__name__}' from node '{from_node_name}'"
            raise ValueError(msg)

        return route_key

    def add_route[TNextMessage: Message](
        self,
        from_node_name: str,
        message_type: type[Message],
        to_node: Node[Message, TNextMessage],
    ) -> "_MessageFlowBuilder[TStartMessage, TNextMessage]":
        """Add a route from a specific node.

        Args:
            from_node_name: Name of the node this route originates from
            message_type: Message type that triggers this route
            to_node: Destination node

        Returns:
            New builder with the route added

        """
        route_key = self._validate_and_create_route(message_type, from_node_name)

        # Add route and mark to_node as reachable
        new_routes = {**self._routes, route_key: to_node}
        new_reachable = self._reachable_nodes | {to_node.name}

        return _MessageFlowBuilder[TStartMessage, TNextMessage](
            _name=self._name,
            _start_node=self._start_node,
            _routes=cast(
                "MappingProxyType[MessageRouteKey, Node[Message, Message] | None]", MappingProxyType(new_routes)
            ),
            _reachable_nodes=new_reachable,
        )

    def add_termination(
        self,
        from_node_name: str,
        message_type: type[Message],
    ) -> MessageFlow[TStartMessage, Message]:
        """Add a termination route from a specific node.

        Args:
            from_node_name: Name of the node this termination originates from
            message_type: Message type that terminates the flow

        Returns:
            Completed flow as a MessageFlow

        """
        route_key = self._validate_and_create_route(message_type, from_node_name, is_termination=True)

        new_routes = {**self._routes, route_key: None}

        return MessageFlow[TStartMessage, Message](
            name=self._name,
            start_node=cast("Node[Message, Message]", self._start_node),
            routes=cast("Mapping[MessageRouteKey, Node[Message, Message] | None]", MappingProxyType(new_routes)),
        )

    def from_node[TNodeIn: Message, TNodeOut: Message](
        self, node: Node[TNodeIn, TNodeOut]
    ) -> _MessageFlowBuilderContext[TStartMessage, TNodeOut]:
        """Create a context for routing from a specific node.

        Args:
            node: The node to route from

        Returns:
            Context for defining routes from the specified node

        """
        return _MessageFlowBuilderContext[TStartMessage, TNodeOut](
            _builder=cast("_MessageFlowBuilder[TStartMessage, TNodeOut]", self),
            _from_node=cast("Node[Message, Message]", node),
        )

    def route[TRouteMessage: Message, TNextMessage: Message](
        self,
        message_type: type[TRouteMessage],
        to_node: Node[TRouteMessage, TNextMessage],
    ) -> "_MessageFlowBuilder[TStartMessage, TNextMessage]":
        """Route message type from start node to destination.

        This is a convenience method for routing from the start node.
        For routing from other nodes, use from_node().route().

        Args:
            message_type: Message type that triggers this route
            to_node: Destination node that will process the message type

        Returns:
            Builder for continued route definition

        """
        return self.add_route(self._start_node.name, message_type, cast("Node[Message, TNextMessage]", to_node))

    def end(self, message_type: type[TCurrentMessage]) -> MessageFlow[TStartMessage, TCurrentMessage]:
        """Mark message type as terminal from start node.

        This is a convenience method for ending from the start node.
        For ending from other nodes, use from_node().end().

        Args:
            message_type: The message type that completes the flow

        Returns:
            A MessageFlow that represents the complete flow (for composability)

        """
        result = self.add_termination(self._start_node.name, message_type)
        return cast("MessageFlow[TStartMessage, TCurrentMessage]", result)


def message_flow[TStartMessage: Message, TStartOut: Message](
    name: str,
    start_node: Node[TStartMessage, TStartOut],
) -> _MessageFlowBuilder[TStartMessage, TStartOut]:
    """Create a message flow with the given name and starting node.

    Args:
        name: The name of the flow
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
