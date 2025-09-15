"""Node implementation for message-driven architecture."""

from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import StringConstraints

from clearflow.message import Message
from clearflow.strict_base_model import StrictBaseModel

__all__ = [
    "Node",
    "NodeInterface",
]


class NodeInterface[TMessageIn: Message, TMessageOut: Message](ABC):
    """Behavioral contract for message processing nodes.

    Defines the core processing behavior that all nodes must implement.
    Nodes transform input messages into output messages, enabling
    type-safe message flow orchestration.

    Type parameters:
        TMessageIn: Input message type that this node processes
        TMessageOut: Output message type that this node produces
    """

    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Process message, potentially using AI intelligence to decide next action.

        Args:
            message: Input message to process

        Returns:
            Output message representing the result of processing

        """
        ...


class Node[TMessageIn: Message, TMessageOut: Message](StrictBaseModel, NodeInterface[TMessageIn, TMessageOut]):
    """Message processing node with state and behavior.

    Combines the NodeInterface behavioral contract with data validation
    and a required name attribute. Nodes process input messages and
    produce output messages, forming the building blocks of message flows.

    Attributes:
        name: Unique identifier for this node (non-empty string)

    Type parameters:
        TMessageIn: Input message type that this node processes
        TMessageOut: Output message type that this node produces

    """

    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
