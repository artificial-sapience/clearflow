"""Chat nodes - just the two participants: User and Assistant."""

import asyncio
from typing import override

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from clearflow import Node
from examples.chat.messages import (
    AssistantMessageReceived,
    ChatCompleted,
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


def _setup_chat_history(message: StartChat | AssistantMessageReceived) -> tuple[ChatMessage, ...]:
    """Set up conversation history and display messages.

    Returns:
        Current conversation history.

    """
    if isinstance(message, StartChat):
        history: tuple[ChatMessage, ...] = (ChatMessage(role="system", content=message.system_prompt),)
        if message.initial_message:
            print(f"Assistant: {message.initial_message}")
            print("-" * 50)
        return history

    # Display assistant's message
    print(f"\nAssistant: {message.message}")
    print("-" * 50)
    return message.conversation_history


def _create_chat_ended(
    message: StartChat | AssistantMessageReceived, history: tuple[ChatMessage, ...]
) -> ChatCompleted:
    """Create ChatCompleted event.

    Returns:
        ChatCompleted event with proper metadata.

    """
    print("\nGoodbye!")
    return ChatCompleted(
        triggered_by_id=message.id,
        run_id=message.run_id,
        final_history=history,
        reason="user_quit",
    )


class UserNode(Node[StartChat | AssistantMessageReceived, UserMessageReceived | ChatCompleted]):
    """Proxy for the user."""

    name: str = "user"

    @override
    async def process(self, message: StartChat | AssistantMessageReceived) -> UserMessageReceived | ChatCompleted:
        """Handle user interaction.

        Returns:
            UserMessageReceived with user's message or ChatCompleted if quitting.

        """
        history = _setup_chat_history(message)

        # Get user input
        try:
            user_input = await asyncio.to_thread(input, "You: ")

            # Check for quit commands
            if user_input.lower() in {"quit", "exit", "bye"}:
                return _create_chat_ended(message, history)

            # Add user message to history
            updated_history = (*history, ChatMessage(role="user", content=user_input))

            return UserMessageReceived(
                triggered_by_id=message.id,
                run_id=message.run_id,
                message=user_input,
                conversation_history=updated_history,
            )

        except (EOFError, KeyboardInterrupt):
            return _create_chat_ended(message, history)


class AssistantNode(Node[UserMessageReceived, AssistantMessageReceived]):
    """Proxy for the LLM assistant."""

    name: str = "assistant"
    model: str = "gpt-5-nano-2025-08-07"

    @override
    async def process(self, message: UserMessageReceived) -> AssistantMessageReceived:
        """Generate assistant response.

        Returns:
            AssistantMessageReceived from the LLM.

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

        return AssistantMessageReceived(
            triggered_by_id=message.id,
            run_id=message.run_id,
            message=ai_response,
            conversation_history=updated_history,
        )
