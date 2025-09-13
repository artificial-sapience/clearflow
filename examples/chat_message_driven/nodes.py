"""Message-driven chat node implementations."""

from dataclasses import dataclass
from typing import override

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from clearflow import MessageNode
from examples.chat_message_driven.messages import (
    ChatMessage,
    ConversationCompleteEvent,
    DisplayResponseCommand,
    GenerateResponseCommand,
    QuitRequestEvent,
    ResponseGeneratedEvent,
    UserInputCommand,
    UserResponseEvent,
)


def _to_openai_message(msg: ChatMessage) -> ChatCompletionMessageParam:
    """Convert ChatMessage to OpenAI format with type narrowing.

    Returns:
        OpenAI-compatible message dictionary with correct role literal.

    """
    if msg.role == "user":
        return {"role": "user", "content": msg.content}
    if msg.role == "assistant":
        return {"role": "assistant", "content": msg.content}
    # system
    return {"role": "system", "content": msg.content}


def _ensure_system_message(messages: tuple[ChatMessage, ...], system_prompt: str) -> tuple[ChatMessage, ...]:
    """Ensure conversation has a system message.

    Returns:
        Messages tuple with system message prepended if missing.

    """
    if not messages:
        return (ChatMessage(role="system", content=system_prompt),)
    return messages


async def _get_ai_response(messages: tuple[ChatMessage, ...], model: str) -> str:
    """Call OpenAI API and get response.

    Returns:
        AI-generated response content string.

    """
    client = AsyncOpenAI()
    # OpenAI API requires a list, not a tuple - this is outside our control
    api_messages = [  # clearflow: ignore[IMM006] # OpenAI requires list
        _to_openai_message(msg) for msg in messages
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=api_messages,
    )

    content = response.choices[0].message.content
    return content or ""


@dataclass(frozen=True, kw_only=True)
class UserInputNode(MessageNode[UserInputCommand, UserResponseEvent | QuitRequestEvent]):
    """Node that handles user input collection."""

    name: str = "user_input"

    @override
    async def process(self, message: UserInputCommand) -> UserResponseEvent | QuitRequestEvent:
        """Get user input and determine if they want to quit.

        Returns:
            UserResponseEvent with input or QuitRequestEvent if quitting.

        """
        try:
            user_input = input("You: ")

            # Check for quit commands
            if user_input.lower() in {"quit", "exit", "bye"}:
                print("\\nGoodbye!")
                return QuitRequestEvent(
                    triggered_by_id=message.id,
                    flow_id=message.flow_id,
                    messages=message.messages,
                )

            # Add user message to conversation
            new_message = ChatMessage(role="user", content=user_input)
            updated_messages = (*message.messages, new_message)

            return UserResponseEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                input_text=user_input,
                messages=updated_messages,
            )

        except (EOFError, KeyboardInterrupt):
            print("\\nGoodbye!")
            return QuitRequestEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                messages=message.messages,
            )


@dataclass(frozen=True, kw_only=True)
class ResponseGeneratorNode(MessageNode[GenerateResponseCommand, ResponseGeneratedEvent]):
    """Node that generates AI responses using OpenAI API."""

    name: str = "response_generator"
    model: str = "gpt-5-nano-2025-08-07"
    system_prompt: str = "You are a helpful assistant."

    @override
    async def process(self, message: GenerateResponseCommand) -> ResponseGeneratedEvent:
        """Generate AI response from conversation messages.

        Returns:
            ResponseGeneratedEvent with AI-generated response.

        """
        # Ensure system message exists
        messages = _ensure_system_message(message.messages, self.system_prompt)

        # Generate response
        response = await _get_ai_response(messages, self.model)

        # Add AI message to conversation
        ai_message = ChatMessage(role="assistant", content=response)
        updated_messages = (*messages, ai_message)

        return ResponseGeneratedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            response=response,
            messages=updated_messages,
        )


@dataclass(frozen=True, kw_only=True)
class DisplayResponseNode(MessageNode[DisplayResponseCommand, UserInputCommand]):
    """Node that displays AI response and prompts for next user input."""

    name: str = "display_response"

    @override
    async def process(self, message: DisplayResponseCommand) -> UserInputCommand:
        """Display AI response and prepare for next user input.

        Returns:
            UserInputCommand to continue conversation loop.

        """
        # Display the AI response
        print(f"\\nAssistant: {message.response}")
        print("-" * 50)

        # Return command for next user input
        return UserInputCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            messages=message.messages,
        )


@dataclass(frozen=True, kw_only=True)
class ConversationCompleteNode(MessageNode[QuitRequestEvent, ConversationCompleteEvent]):
    """Node that handles conversation completion."""

    name: str = "conversation_complete"

    @override
    async def process(self, message: QuitRequestEvent) -> ConversationCompleteEvent:
        """Complete the conversation.

        Returns:
            ConversationCompleteEvent marking end of conversation.

        """
        return ConversationCompleteEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            final_messages=message.messages,
        )


@dataclass(frozen=True, kw_only=True)
class ResponseToDisplayNode(MessageNode[ResponseGeneratedEvent, DisplayResponseCommand]):
    """Node that transforms response event to display command."""

    name: str = "response_to_display"

    @override
    async def process(self, message: ResponseGeneratedEvent) -> DisplayResponseCommand:
        """Convert response event to display command.

        Returns:
            DisplayResponseCommand to show the response.

        """
        return DisplayResponseCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            response=message.response,
            messages=message.messages,
        )


@dataclass(frozen=True, kw_only=True)
class UserResponseToGenerateNode(MessageNode[UserResponseEvent, GenerateResponseCommand]):
    """Node that transforms user response to generate command."""

    name: str = "user_response_to_generate"

    @override
    async def process(self, message: UserResponseEvent) -> GenerateResponseCommand:
        """Convert user response to generate command.

        Returns:
            GenerateResponseCommand to create AI response.

        """
        return GenerateResponseCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            messages=message.messages,
        )
