"""Chat nodes - just the two participants: User and Assistant."""

from dataclasses import dataclass
from typing import override

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from clearflow import MessageNode
from examples.chat_message_driven.messages import (
    AssistantMessageSent,
    ChatEnded,
    ChatMessage,
    StartChat,
    UserMessageReceived,
)


def _to_openai_messages(history: tuple[ChatMessage, ...]) -> tuple[ChatCompletionMessageParam, ...]:
    """Convert chat history to OpenAI API format.

    Returns:
        Tuple of OpenAI-compatible message dictionaries.

    """
    result: tuple[ChatCompletionMessageParam, ...] = ()
    for msg in history:
        param: ChatCompletionMessageParam
        if msg.role == "user":
            param = {"role": "user", "content": msg.content}
        elif msg.role == "assistant":
            param = {"role": "assistant", "content": msg.content}
        else:  # system
            param = {"role": "system", "content": msg.content}
        result = (*result, param)
    return result


@dataclass(frozen=True, kw_only=True)
class UserNode(MessageNode[StartChat | AssistantMessageSent, UserMessageReceived | ChatEnded]):
    """The human participant in the chat.

    Handles user interaction:
    - Shows assistant messages (if any)
    - Gets user input
    - Detects when user wants to quit
    """

    name: str = "user"

    @override
    async def process(self, message: StartChat | AssistantMessageSent) -> UserMessageReceived | ChatEnded:
        """Handle user interaction.

        Returns:
            UserMessageReceived with user's message or ChatEnded if quitting.

        """
        # Initialize conversation history for new chat
        if isinstance(message, StartChat):
            history: tuple[ChatMessage, ...] = (ChatMessage(role="system", content=message.system_prompt),)
            # Display initial message if provided
            if message.initial_message:
                print(f"Assistant: {message.initial_message}")
                print("-" * 50)
        else:
            # Display the assistant's message
            print(f"\nAssistant: {message.message}")
            print("-" * 50)
            history = message.conversation_history

        # Get user input
        try:
            user_input = input("You: ")

            # Check for quit commands
            if user_input.lower() in {"quit", "exit", "bye"}:
                print("\nGoodbye!")
                return ChatEnded(
                    triggered_by_id=message.id,
                    flow_id=message.flow_id,
                    final_history=history,
                    reason="user_quit",
                )

            # Add user message to history
            updated_history = (*history, ChatMessage(role="user", content=user_input))

            return UserMessageReceived(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                message=user_input,
                conversation_history=updated_history,
            )

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return ChatEnded(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                final_history=history,
                reason="user_quit",
            )


@dataclass(frozen=True, kw_only=True)
class AssistantNode(MessageNode[UserMessageReceived, AssistantMessageSent]):
    """The AI assistant participant in the chat.

    Generates responses using OpenAI API.
    """

    name: str = "assistant"
    model: str = "gpt-5-nano-2025-08-07"

    @override
    async def process(self, message: UserMessageReceived) -> AssistantMessageSent:
        """Generate assistant response.

        Returns:
            AssistantMessageSent with AI-generated response.

        """
        # Convert history to OpenAI format
        api_messages = _to_openai_messages(message.conversation_history)

        # Call OpenAI API
        client = AsyncOpenAI()
        # OpenAI API requires a mutable sequence, not a tuple - convert at the last moment
        messages_for_api = [*api_messages]  # clearflow: ignore[IMM006] # OpenAI requires mutable
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages_for_api,
        )

        ai_response = response.choices[0].message.content or ""

        # Add assistant message to history
        updated_history = (
            *message.conversation_history,
            ChatMessage(role="assistant", content=ai_response),
        )

        return AssistantMessageSent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            message=ai_response,
            conversation_history=updated_history,
        )
