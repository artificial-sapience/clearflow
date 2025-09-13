"""Message definitions for chat application using natural event-driven semantics."""

from dataclasses import dataclass
from typing import Literal

from clearflow import Command, Event


@dataclass(frozen=True, kw_only=True)
class ChatMessage:
    """Immutable chat message structure."""

    role: Literal["system", "user", "assistant"]
    content: str


# ============================================================================
# SINGLE INITIATING COMMAND
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class StartChat(Command):
    """Initiate a chat conversation.

    This is the only command in the system. All subsequent messages are events.
    """

    system_prompt: str = "You are a helpful assistant."
    initial_message: str | None = None  # Optional initial message to show user


# ============================================================================
# EVENTS - Natural chat flow
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class UserMessageReceived(Event):
    """User sent a message."""

    message: str
    conversation_history: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class AssistantMessageReceived(Event):
    """Assistant received a message from the LLM."""

    message: str
    conversation_history: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class ChatEnded(Event):
    """Chat conversation ended."""

    final_history: tuple[ChatMessage, ...]
    reason: Literal["user_quit", "error", "complete"]
