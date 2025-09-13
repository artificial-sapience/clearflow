"""Message-driven chat flow construction."""

from clearflow import MessageFlow, message_flow
from examples.chat_message_driven.messages import (
    ConversationCompleteEvent,
    DisplayResponseCommand,
    GenerateResponseCommand,
    QuitRequestEvent,
    ResponseGeneratedEvent,
    UserInputCommand,
    UserResponseEvent,
)
from examples.chat_message_driven.nodes import (
    ConversationCompleteNode,
    DisplayResponseNode,
    ResponseGeneratorNode,
    ResponseToDisplayNode,
    UserInputNode,
    UserResponseToGenerateNode,
)


def create_message_driven_chat_flow() -> MessageFlow[UserInputCommand, ConversationCompleteEvent]:
    """Create a message-driven conversation flow.

    This flow demonstrates the message-driven architecture with explicit
    message types and routing. The conversation flows through these states:

    1. UserInputCommand -> UserInputNode -> UserResponseEvent/QuitRequestEvent
    2. UserResponseEvent -> UserResponseToGenerateNode -> GenerateResponseCommand
    3. GenerateResponseCommand -> ResponseGeneratorNode -> ResponseGeneratedEvent
    4. ResponseGeneratedEvent -> ResponseToDisplayNode -> DisplayResponseCommand
    5. DisplayResponseCommand -> DisplayResponseNode -> UserInputCommand (loop)
    6. QuitRequestEvent -> ConversationCompleteNode -> ConversationCompleteEvent

    Returns:
        MessageFlow configured for message-driven conversation.

    """
    # Create nodes
    user_input = UserInputNode()
    user_to_generate = UserResponseToGenerateNode()
    generator = ResponseGeneratorNode()
    response_to_display = ResponseToDisplayNode()
    display = DisplayResponseNode()
    complete = ConversationCompleteNode()

    # Build the flow with explicit message routing
    return (
        message_flow("MessageDrivenChat", user_input)
        .from_node(user_input)
        .route(UserResponseEvent, user_to_generate)
        .from_node(user_input)
        .route(QuitRequestEvent, complete)
        .from_node(user_to_generate)
        .route(GenerateResponseCommand, generator)
        .from_node(generator)
        .route(ResponseGeneratedEvent, response_to_display)
        .from_node(response_to_display)
        .route(DisplayResponseCommand, display)
        .from_node(display)
        .route(UserInputCommand, user_input)  # Loop back
        .from_node(complete)
        .end(ConversationCompleteEvent)
    )