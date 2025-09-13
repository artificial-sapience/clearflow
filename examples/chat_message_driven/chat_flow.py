"""Chat flow - natural back-and-forth conversation between user and assistant."""

from clearflow import MessageFlow, message_flow
from examples.chat_message_driven.messages import (
    AssistantMessageSent,
    ChatEnded,
    StartChat,
    UserMessageReceived,
)
from examples.chat_message_driven.nodes import AssistantNode, UserNode


def create_chat_flow() -> MessageFlow[StartChat, ChatEnded]:
    """Create a natural chat flow between user and assistant.

    This flow demonstrates a simple, familiar chat pattern:
    - User initiates with StartChat
    - User and Assistant alternate messages
    - Continues until user decides to end

    Flow sequence:
    1. StartChat → UserNode
    2. UserMessageReceived → AssistantNode
    3. AssistantMessageSent → UserNode (loop back)
    4. ChatEnded (when user quits)

    Returns:
        MessageFlow for natural chat conversation.

    """
    # Just two participants
    user = UserNode()
    assistant = AssistantNode()

    # Build the natural alternating flow
    return (
        message_flow("Chat", user)
        # User can send a message or end the chat
        .route(user, UserMessageReceived, assistant)  # User message → Assistant processes
        # Assistant always sends back a message
        .route(assistant, AssistantMessageSent, user)  # Assistant response → User sees it
        # Terminal event when user quits
        .end(user, ChatEnded)
    )
