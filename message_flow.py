"""Message flow implementation for type-safe routing."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast, final

from clearflow.message import Message
from clearflow.message_node import Node

MessageRouteKey = tuple[type[Message], str]  # (message_type, node_name)


@final
@dataclass(frozen=True, kw_only=True)
class MessageFlow[TStartMessage: Message, TEndMessage: Message]:
    """Core message flow that routes messages between nodes.
    
    Executes flows by routing messages based on their types to appropriate nodes.
    Maintains type safety through compile-time checking of message compatibility.
    """

    name: str
    start_node: Node
    routes: Mapping[MessageRouteKey, Node | None]

    async def execute(self, start_message: TStartMessage) -> TEndMessage:
        """Execute the flow by routing messages through nodes.

        Args:
            start_message: Initial message to start the flow

        Returns:
            Final message when flow reaches termination

        Raises:
            ValueError: If no route is defined for a message type from a node.

        """
        current_node = self.start_node
        current_message: Message = start_message

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
class MessageFlowBuilder[TStartMessage: Message, TCurrentMessage: Message]:
    """Builder for composing type-safe message routes.
    
    Type parameters:
        TStartMessage: The input message type the flow accepts
        TCurrentMessage: The current message type in the flow
        
    Call end() to specify where the flow terminates and get the completed flow.
    """

    _name: str
    _start_node: Node[TStartMessage, Message]
    _routes: MappingProxyType[MessageRouteKey, Node | None]
    _reachable_nodes: frozenset[str]  # Node names that are reachable from start

    def _validate_and_create_route(
        self,
        message_type: type[Message],
        from_node_name: str,
        *,
        is_termination: bool = False
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
            msg = (
                f"Route already defined for message type '{message_type.__name__}' "
                f"from node '{from_node_name}'"
            )
            raise ValueError(msg)

        return route_key

    def route[TNextMessage: Message](
        self,
        message_type: type[TCurrentMessage],
        to_node: Node[TCurrentMessage, TNextMessage],
    ) -> "MessageFlowBuilder[TStartMessage, TNextMessage]":
        """Route message type to next node.

        Args:
            message_type: Message type that triggers this route
            to_node: Destination node that will process the message type

        Returns:
            Builder for continued route definition

        Raises:
            ValueError: If route validation fails

        """
        # Find the node that produces this message type
        producing_node_name = None
        for (msg_type, node_name), _ in self._routes.items():
            if msg_type == message_type:
                producing_node_name = node_name
                break

        # If not found in routes, check if it's the start node's output
        if producing_node_name is None:
            # Assume it's from start node for now - real validation happens at runtime
            producing_node_name = self._start_node.name

        route_key = self._validate_and_create_route(message_type, producing_node_name)

        # Add route and mark to_node as reachable
        new_routes = {**self._routes, route_key: to_node}
        new_reachable = self._reachable_nodes | {to_node.name}

        return MessageFlowBuilder[TStartMessage, TNextMessage](
            _name=self._name,
            _start_node=self._start_node,
            _routes=MappingProxyType(new_routes),
            _reachable_nodes=new_reachable,
        )

    def end(self, message_type: type[TCurrentMessage]) -> MessageFlow[TStartMessage, TCurrentMessage]:
        """Mark message type as terminal, completing the flow.

        Args:
            message_type: The message type that completes the flow

        Returns:
            A complete message flow

        Raises:
            ValueError: If message type route validation fails

        """
        # Find the node that produces this message type
        producing_node_name = None
        for (msg_type, node_name), _ in self._routes.items():
            if msg_type == message_type:
                producing_node_name = node_name
                break

        # If not found in routes, check if it's from start node
        if producing_node_name is None:
            producing_node_name = self._start_node.name

        route_key = self._validate_and_create_route(
            message_type, producing_node_name, is_termination=True
        )

        new_routes = {**self._routes, route_key: None}

        return MessageFlow[TStartMessage, TCurrentMessage](
            name=self._name,
            start_node=self._start_node,
            routes=MappingProxyType(new_routes),
        )


def message_flow[TStartMessage: Message, TStartOut: Message](
    name: str,
    start_node: Node[TStartMessage, TStartOut],
) -> MessageFlowBuilder[TStartMessage, TStartOut]:
    """Create a message flow with the given name and starting node.

    Args:
        name: The name of the flow
        start_node: The starting node that processes TStartMessage

    Returns:
        Builder for route definition and flow completion

    """
    return MessageFlowBuilder[TStartMessage, TStartOut](
        _name=name,
        _start_node=start_node,
        _routes=MappingProxyType({}),
        _reachable_nodes=frozenset({start_node.name}),
    )
