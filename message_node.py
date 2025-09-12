"""Node implementation for message-driven architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from clearflow.message import Message


@final
@dataclass(frozen=True, kw_only=True)
class Node[TMessageIn: Message, TMessageOut: Message](ABC):
    """Orchestration node that can embody AI intelligence.
    
    Accepts: Commands or Events (triggers for processing)
    Produces: Commands (intent/delegation) or Events (completed facts)
    
    This flexibility allows AI agents to:
    - Orchestrate complex workflows via Commands
    - Record completion via Events  
    - Delegate to specialized agents/tools
    - Dynamically adapt their strategy
    
    Type parameters:
        TMessageIn: Input message type that this node processes
        TMessageOut: Output message type that this node produces
    """

    name: str

    def __post_init__(self) -> None:
        """Validate node configuration after initialization.

        Raises:
            ValueError: If node name is empty or contains only whitespace.

        """
        if not self.name or not self.name.strip():
            msg = f"Node name must be a non-empty string, got: {self.name!r}"
            raise ValueError(msg)

    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Process message, potentially using AI intelligence to decide next action.
        
        Args:
            message: Input message to process
            
        Returns:
            Output message representing the result of processing

        """
        ...
