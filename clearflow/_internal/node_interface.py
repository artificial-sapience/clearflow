"""Pure behavioral interface for nodes.

This module provides the abstract interface for nodes without any data validation.
It separates the behavioral contract from the data schema to avoid Pydantic
validation issues with self-referential abstract types.

This is an internal implementation detail - users should continue using Node.
"""

from abc import ABC, abstractmethod

from clearflow.message import Message

__all__: list[str] = []  # Empty - this is an internal module


class _NodeInterface[TMessageIn: Message, TMessageOut: Message](ABC):
    """Pure behavioral interface for nodes.

    Defines the contract that all nodes must implement without
    inheriting from BaseModel. This prevents Pydantic validation
    issues when nodes contain fields of the same abstract type.

    This is an internal interface - users should use Node which
    combines this interface with Pydantic data validation.

    Type parameters:
        TMessageIn: Input message type that this node processes
        TMessageOut: Output message type that this node produces
    """

    # Note: name is defined as a field in Node, not as a property here
    # to avoid conflicts with Pydantic's field definition

    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Process message, potentially using AI intelligence to decide next action.

        Args:
            message: Input message to process

        Returns:
            Output message representing the result of processing

        """
        ...
