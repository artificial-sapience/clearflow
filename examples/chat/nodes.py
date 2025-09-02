"""Chat node implementation - pure business logic."""

from dataclasses import dataclass
from typing import Literal, TypedDict, override

from openai import AsyncOpenAI

from clearflow import Node, NodeResult


class ChatMessage(TypedDict):
    """OpenAI chat message structure."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatState(TypedDict, total=False):
    """Chat application state with proper types.

    total=False means all fields are optional, which matches
    our usage pattern where state builds up over time.
    """

    messages: tuple[ChatMessage, ...]
    last_response: str
    user_input: str | None


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

    model: str = "gpt-4o-2024-08-06"
    system_prompt: str = "You are a helpful assistant."

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        """Process user input and generate language model response."""
        # Get conversation history and current user input
        messages = state.get("messages", ())
        user_input: str | None = state.get("user_input")

        # Initialize with system message if needed
        if not messages:
            system_msg: ChatMessage = {"role": "system", "content": self.system_prompt}
            messages = (system_msg,)

        # If no user input provided, this is just initialization
        if user_input is None:
            init_state: ChatState = {**state, "messages": messages}
            return NodeResult(init_state, outcome="awaiting_input")

        # Add user message to conversation
        user_msg: ChatMessage = {"role": "user", "content": user_input}
        messages = (*messages, user_msg)

        # Call OpenAI API - messages type matches what OpenAI expects
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,  # Type matches OpenAI's expected structure
        )

        # Extract assistant's response
        assistant_response = response.choices[0].message.content
        if not assistant_response:
            assistant_response = ""

        # Add assistant message to conversation
        assistant_msg: ChatMessage = {
            "role": "assistant",
            "content": assistant_response,
        }
        messages = (*messages, assistant_msg)

        # Return updated state with full conversation
        new_state: ChatState = {
            **state,
            "messages": messages,
            "last_response": assistant_response,
            "user_input": None,  # Clear user input after processing
        }

        return NodeResult(new_state, outcome="responded")
