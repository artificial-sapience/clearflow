"""Chat flow - natural back-and-forth conversation between user and assistant."""

from clearflow import Node, create_flow
from examples.chat.messages import (
    AssistantMessageReceived,
    ChatCompleted,
    StartChat,
    UserMessageReceived,
)
from examples.chat.nodes import AssistantNode, UserNode


def create_chat_flow() -> Node[StartChat, UserMessageReceived | ChatCompleted]:
    """Create a natural chat flow between user and assistant.

    Returns:
        MessageFlow for natural chat conversation.

    """
    # Just two participants
    user = UserNode()
    assistant = AssistantNode()

    # Build the natural alternating flow
    return (
        create_flow("Chat", user)
        .route(user, UserMessageReceived, assistant)
        .route(assistant, AssistantMessageReceived, user)
        .end_flow(ChatCompleted)
    )
