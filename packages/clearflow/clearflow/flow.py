"""Flow construction for ClearFlow."""

from abc import ABC, abstractmethod

from clearflow.message import Message
from clearflow.node import Node
from clearflow.observer import Observer

__all__ = ["FlowBuilder"]


class FlowBuilder[TStartIn: Message, TStartOut: Message](ABC):
    """Builder for composing message-driven flows.

    Type parameters:
        TStartIn: The input message type the flow accepts
        TStartOut: The output type of the start node
    """

    @abstractmethod
    def observe(self, *observers: Observer) -> "FlowBuilder[TStartIn, TStartOut]":
        """Attach observers to the flow.

        Args:
            *observers: Observer instances to monitor flow execution

        Returns:
            Builder for continued configuration

        """
        ...

    @abstractmethod
    def route[TFromIn: Message, TFromOut: Message, TToIn: Message, TToOut: Message](
        self,
        from_node: Node[TFromIn, TFromOut],
        outcome: type[Message],
        to_node: Node[TToIn, TToOut],
    ) -> "FlowBuilder[TStartIn, TStartOut]":
        """Route specific message type from source node to destination.

        Args:
            from_node: Source node that may emit the outcome message type
            outcome: Specific message type that triggers this route
            to_node: Destination node that accepts this message type

        Returns:
            Builder for continued route definition

        """
        ...

    @abstractmethod
    def end_flow[TEnd: Message](
        self,
        terminal_type: type[TEnd],
    ) -> Node[TStartIn, TEnd]:
        """Declare the message type that completes this flow.

        When any node produces an instance of the terminal type, the flow
        immediately terminates and returns that message.

        Args:
            terminal_type: The message type that completes the flow

        Returns:
            A Node that represents the complete flow

        """
        ...
