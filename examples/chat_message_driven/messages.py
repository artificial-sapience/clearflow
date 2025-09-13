"""Message definitions for chat application."""

from dataclasses import dataclass
from typing import Literal

from clearflow import Command, Event


@dataclass(frozen=True, kw_only=True)
class ChatMessage:
    """Immutable chat message structure."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True, kw_only=True)
class UserInputCommand(Command):
    """Command to get user input."""

    messages: tuple[ChatMessage, ...] = ()


@dataclass(frozen=True, kw_only=True)
class UserResponseEvent(Event):
    """Event when user provides input."""

    input_text: str
    messages: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class QuitRequestEvent(Event):
    """Event when user wants to quit."""

    messages: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class GenerateResponseCommand(Command):
    """Command to generate AI response."""

    messages: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class ResponseGeneratedEvent(Event):
    """Event when AI response is generated."""

    response: str
    messages: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class DisplayResponseCommand(Command):
    """Command to display AI response and get next user input."""

    response: str
    messages: tuple[ChatMessage, ...]


@dataclass(frozen=True, kw_only=True)
class ConversationCompleteEvent(Event):
    """Event when conversation is complete."""

    final_messages: tuple[ChatMessage, ...]
