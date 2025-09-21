"""Chat flow - natural back-and-forth conversation between user and assistant."""

from clearflow import Node, create_flow
from examples.chat.messages import (
    AssistantMessageReceived,
    ChatCompleted,
    StartChat,
    UserMessageReceived,
)
from examples.chat.nodes import AssistantNode, UserNode
from examples.shared import AsyncSpinnerObserver


def create_chat_flow() -> Node[StartChat, UserMessageReceived | ChatCompleted]:
    """Create a natural chat flow between user and assistant.

    Returns:
        MessageFlow for natural chat conversation.

    """
    # Just two participants
    user = UserNode()
    assistant = AssistantNode()

    # Build the natural alternating flow with spinner for LLM calls
    return (
        create_flow("Chat", user)
        .observe(AsyncSpinnerObserver(spinner_nodes=("assistant",)))
        .route(user, UserMessageReceived, assistant)
        .route(assistant, AssistantMessageReceived, user)
        .end_flow(ChatCompleted)
    )
