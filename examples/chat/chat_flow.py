"""Chat flow construction."""

from clearflow import Node, flow
from examples.chat.nodes import ChatNode, ChatState


def create_chat_flow() -> Node[ChatState]:
    """Create a chat flow that manages conversations through a language model.

    The ChatNode handles all conversation management including:
    - Maintaining message history
    - Adding user messages
    - Processing through the language model
    - Returning responses

    The UI layer (main.py) only handles input/output.
    
    Returns:
        Chat node configured for conversation management.
    """
    chat = ChatNode(name="chat")

    # Single-node flow that processes one message and ends
    # The chat node returns "awaiting_input" or "responded" outcomes
    return flow("ChatBot", chat).end(chat, "responded")
