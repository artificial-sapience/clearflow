"""Chat flow construction."""

from nodes import ChatNode, ChatState

from clearflow import Flow, Node


def create_chat_flow() -> Node[ChatState]:
    """Create a chat flow that manages conversations through an LLM.

    The ChatNode handles all conversation management including:
    - Maintaining message history
    - Adding user messages
    - Processing through the LLM
    - Returning responses

    The UI layer (main.py) only handles input/output.
    """
    chat = ChatNode()

    # Since this is a single-node flow that processes one message,
    # we can use a simple pattern without routes
    return (
        Flow[ChatState]("ChatBot")
        .start_with(chat)
        # No routes needed - the flow will return the node's outcome
        .build()
    )
