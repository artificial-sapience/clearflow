"""Chat flow - natural back-and-forth conversation between user and assistant."""

from clearflow import Node, create_flow
from examples.chat.messages import (
    AssistantMessageReceived,
    ChatEnded,
    StartChat,
    UserMessageReceived,
)
from examples.chat.nodes import AssistantNode, UserNode


def create_chat_flow() -> Node[StartChat, ChatEnded]:
    """Create a natural chat flow between user and assistant.

    This flow demonstrates a simple, familiar chat pattern:
    - User initiates with StartChat
    - User and Assistant alternate messages
    - Continues until user decides to end

    Flow sequence:
    1. StartChat → UserNode
    2. UserMessageReceived → AssistantNode
    3. AssistantMessageReceived → UserNode (loop back)
    4. ChatEnded (when user quits)

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
        .complete_flow(user, ChatEnded)
    )
