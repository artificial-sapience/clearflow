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
    """Behavioral contract for AI-powered message processing nodes.

    Defines the interface for nodes that transform messages in AI workflows.
    Each node encapsulates a specific capability: LLM calls, vector search, validation, etc.

    Why use NodeInterface:
    - Type safety: Compile-time guarantees about message compatibility
    - Async-first: Built for concurrent AI operations
    - Single responsibility: Each node does one thing well
    - Testable: Mock implementations for deterministic testing

    Type parameters:
        TMessageIn: Type of message this node can process
        TMessageOut: Type of message this node produces
    """

    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Transform input message into output message through AI operations.

        This method contains the node's core logic: calling LLMs, querying vectors,
        validating outputs, or orchestrating other AI operations.

        Args:
            message: Typed input message containing request data and metadata

        Returns:
            Typed output message with results and preserved causality chain

        """
        ...


class Node[TMessageIn: Message, TMessageOut: Message](StrictBaseModel, NodeInterface[TMessageIn, TMessageOut]):
    """Concrete message processing node for AI workflows.

    Nodes are the building blocks of AI orchestration, each performing a specific
    operation: generating with LLMs, retrieving from vectors, validating outputs,
    or transforming data between AI services.

    Why use Node:
    - Named operations: Each node has a unique identifier for tracing
    - Immutable configuration: Node parameters are frozen after creation
    - Pydantic validation: Automatic validation of node configuration
    - Composable: Nodes chain together to form complex AI pipelines

    Example node types for AI systems:
    - LLMGenerator: Wraps language model API calls
    - VectorRetriever: Queries embedding databases
    - OutputValidator: Checks AI responses against criteria
    - ResultAggregator: Combines outputs from multiple AI agents

    Type parameters:
        TMessageIn: Type of message this node can process
        TMessageOut: Type of message this node produces

    """

    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = Field(
        description="Unique identifier for this node instance, used in routing and debugging AI workflows"
    )
