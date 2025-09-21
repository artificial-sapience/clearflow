"""Chat flow - natural back-and-forth conversation between user and assistant."""

from typing import override

from rich.console import Console

from clearflow import Message, Node, Observer, create_flow
from examples.chat.messages import (
    AssistantMessageReceived,
    ChatCompleted,
    StartChat,
    UserMessageReceived,
)
from examples.chat.nodes import AssistantNode, UserNode


class SimpleSpinnerObserver(Observer):
    """Simple spinner for async operations - shows while waiting for LLM."""

    def __init__(self) -> None:
        """Initialize the spinner observer."""
        self._console = Console()
        self._spinner = None

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Start spinner when assistant node starts processing."""
        if node_name == "assistant":
            self._spinner = self._console.status("[cyan]Thinking...[/cyan]", spinner="dots")
            self._spinner.start()

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Stop spinner when assistant completes."""
        if self._spinner:
            self._spinner.stop()
            self._spinner = None


def create_chat_flow() -> Node[StartChat, UserMessageReceived | ChatCompleted]:
    """Create a natural chat flow between user and assistant.

    Returns:
        MessageFlow for natural chat conversation.

    """
    # Just two participants
    user = UserNode()
    assistant = AssistantNode()

    # Build the natural alternating flow with simple spinner for LLM calls
    return (
        create_flow("Chat", user)
        .observe(SimpleSpinnerObserver())
        .route(user, UserMessageReceived, assistant)
        .route(assistant, AssistantMessageReceived, user)
        .end_flow(ChatCompleted)
    )
