"""Chat node implementation - pure business logic with immutable state."""

import dataclasses
from dataclasses import dataclass
from typing import Literal, override

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from clearflow import Node, NodeResult


@dataclass(frozen=True)
class ChatMessage:
    """Immutable chat message structure."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ChatState:
    """Immutable chat application state.

    All fields are required - we use dataclasses.replace() to update.
    Empty defaults make initialization clean.
    """

    messages: tuple[ChatMessage, ...] = ()
    last_response: str = ""
    user_input: str = ""


def _to_openai_message(msg: ChatMessage) -> ChatCompletionMessageParam:
    """Convert ChatMessage to OpenAI format with type narrowing.

    OpenAI expects specific role literals for each message type,
    not a union. This helper provides the type narrowing.
    """
    if msg.role == "user":
        return {"role": "user", "content": msg.content}
    if msg.role == "assistant":
        return {"role": "assistant", "content": msg.content}
    # system
    return {"role": "system", "content": msg.content}


def _ensure_system_message(
    messages: tuple[ChatMessage, ...], system_prompt: str
) -> tuple[ChatMessage, ...]:
    """Ensure conversation has a system message."""
    if not messages:
        return (ChatMessage(role="system", content=system_prompt),)
    return messages


async def _get_ai_response(messages: tuple[ChatMessage, ...], model: str) -> str:
    """Call OpenAI API and get response."""
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


@dataclass(frozen=True)
class ChatNode(Node[ChatState]):
    """Node that processes chat messages through a language model.

    This node handles the complete conversation management:
    1. Maintains conversation history
    2. Adds user messages when provided
    3. Ensures system prompt is present
    4. Processes through language model
    5. Returns updated conversation state
    """

    model: str = "gpt-5-nano-2025-08-07"
    system_prompt: str = "You are a helpful assistant."

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        """Process user input and generate language model response."""
        # Ensure system message exists
        messages = _ensure_system_message(state.messages, self.system_prompt)

        # Handle initialization without user input
        if not state.user_input:
            init_state = dataclasses.replace(state, messages=messages)
            return NodeResult(init_state, outcome="awaiting_input")

        # Add user message and get AI response
        messages = (*messages, ChatMessage(role="user", content=state.user_input))
        assistant_response = await _get_ai_response(messages, self.model)
        messages = (
            *messages,
            ChatMessage(role="assistant", content=assistant_response),
        )

        # Return updated state
        new_state = dataclasses.replace(
            state,
            messages=messages,
            last_response=assistant_response,
            user_input="",  # Clear user input after processing
        )
        return NodeResult(new_state, outcome="responded")
