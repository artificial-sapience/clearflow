"""Message definitions for chat application using message-driven semantics."""

from typing import Literal

from pydantic import Field

from clearflow import Command, Event, StrictBaseModel


class ChatMessage(StrictBaseModel):
    """Structured message in a conversation between user and AI assistant.

    Represents a single turn in the conversation with role-based attribution.
    Immutable to preserve conversation history integrity.

    Perfect for:
    - Building conversation context for LLMs
    - Maintaining chat history for multi-turn interactions
    - Analyzing conversation patterns and user intent
    """

    role: Literal["system", "user", "assistant"] = Field(
        description="Speaker role: system for instructions, user for human input, assistant for AI responses"
    )
    content: str = Field(description="Message text content to be processed or displayed in the conversation")


# ============================================================================
# SINGLE INITIATING COMMAND
# ============================================================================


class StartChat(Command):
    """Command to initialize a new chat session with an AI assistant.

    Establishes the AI's behavior through system prompting and optionally
    displays an initial message. This is the only command - all subsequent
    interactions are events, reflecting the natural flow of conversation.

    Why this pattern:
    - Single entry point for session initialization
    - System prompt defines AI personality and constraints
    - Events model the back-and-forth nature of chat
    """

    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="Initial instructions defining the AI assistant's behavior, knowledge, and constraints",
    )
    initial_message: str | None = Field(
        default=None, description="Optional welcome message to display before user interaction begins"
    )


# ============================================================================
# EVENTS - Natural chat flow
# ============================================================================


class UserMessageReceived(Event):
    """Event capturing user input in the ongoing chat conversation.

    Triggered when the user submits a message, carrying both the new input
    and the complete conversation history for context-aware AI responses.

    Used for:
    - Providing full context to LLM for response generation
    - Maintaining conversation continuity across turns
    - Enabling context-aware AI responses
    """

    message: str = Field(description="User's input text to be processed by the AI assistant")
    conversation_history: tuple[ChatMessage, ...] = Field(
        description="Complete conversation history including system, user, and assistant messages for context"
    )


class AssistantMessageReceived(Event):
    """Event containing the AI assistant's generated response.

    Produced after the LLM processes user input with conversation context,
    containing both the response and updated conversation history.

    Enables:
    - Response display to the user
    - Conversation history updates
    - Response validation or filtering
    """

    message: str = Field(description="AI-generated response text to be displayed to the user")
    conversation_history: tuple[ChatMessage, ...] = Field(
        description="Updated conversation history including the new assistant response"
    )


class ChatCompleted(Event):
    """Terminal event marking the end of a chat session.

    Captures the complete conversation history and termination reason,
    serving as the flow's terminal type for clean session closure.

    Terminal reasons:
    - user_quit: User explicitly ended the conversation
    - error: Unrecoverable error occurred during processing
    - complete: Natural conversation conclusion reached
    """

    final_history: tuple[ChatMessage, ...] = Field(
        description="Complete conversation transcript from session start to termination"
    )
    reason: Literal["user_quit", "error", "complete"] = Field(
        description="Termination cause: user_quit for explicit exit, error for failures, complete for natural end"
    )
