"""Node implementation for message-driven architecture."""

from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import Field, StringConstraints

from clearflow.message import Message
from clearflow.strict_base_model import StrictBaseModel

__all__ = [
    "Node",
    "NodeInterface",
]


class NodeInterface[TMessageIn: Message, TMessageOut: Message](ABC):
    """Abstract interface for message processing nodes.

    Defines the contract for nodes that transform messages in workflows.
    Each node encapsulates a specific operation: LLM calls, vector search,
    validation, data transformation, etc.

    Type parameters:
        TMessageIn: Type of message this node can process
        TMessageOut: Type of message this node produces
    """

    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Transform input message into output message.

        Args:
            message: Input message to process

        Returns:
            Output message with results and metadata

        """
        ...


class Node[TMessageIn: Message, TMessageOut: Message](StrictBaseModel, NodeInterface[TMessageIn, TMessageOut]):
    """Concrete message processing node.

    A named, immutable processing unit that transforms one message type into another.
    Nodes chain together in flows to form message processing pipelines.

    Type parameters:
        TMessageIn: Type of message this node can process
        TMessageOut: Type of message this node produces

    Attributes:
        name: Unique identifier for this node instance

    """

    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = Field(
        description="Unique identifier for this node instance"
    )
