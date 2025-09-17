"""Message base classes for message-driven architecture."""

import uuid
from abc import ABC
from datetime import UTC, datetime

from pydantic import AwareDatetime, Field, model_validator

from clearflow.strict_base_model import StrictBaseModel

__all__ = [
    "Command",
    "Event",
    "Message",
]


def _utc_now() -> AwareDatetime:
    """Create a timezone-aware datetime in UTC.

    Returns:
        Current UTC time as AwareDatetime.

    """
    return datetime.now(UTC)


class Message(StrictBaseModel, ABC):
    """Base message class for message-driven AI orchestration.

    Messages enable type-safe, immutable data flow between nodes with full causality tracking.
    Each message carries metadata for tracing, debugging, and understanding AI decision chains.

    Why use Message:
    - Type-safe routing: Route on message types, not strings
    - Causality tracking: Trace AI decisions through triggered_by chains
    - Immutable state: Prevent unintended mutations in complex flows
    - Session isolation: run_id ensures messages stay within their flow

    Perfect for:
    - LLM orchestration with traceable decision chains
    - Multi-agent workflows requiring audit trails
    - RAG pipelines with clear data lineage
    - Any AI system requiring reproducible execution paths
    """

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this message instance, enabling precise tracking and correlation",
    )
    triggered_by_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the message that caused this message to be created, forming a causality chain. None indicates a root command that initiates a flow, non-None links to the triggering message",
    )
    timestamp: AwareDatetime = Field(
        default_factory=_utc_now,
        description="UTC timestamp when this message was created, ensuring global time consistency",
    )
    run_id: uuid.UUID = Field(
        description="Session identifier linking all messages in a single flow execution. Set once when creating the root command (e.g., uuid.uuid4()) and propagated unchanged to all downstream messages in the flow for isolation and tracing"
    )


class Event(Message):
    """Immutable fact representing something that has occurred in the AI workflow.

    Events capture completed actions, state transitions, and outcomes from AI operations.
    Every event MUST be triggered by another message, ensuring complete causality chains.

    Why use Event:
    - Past-tense facts: Events describe what HAS happened, not what should happen
    - Required causality: triggered_by_id is mandatory, ensuring traceable AI decisions
    - Immutable history: Once created, events form an unchangeable audit trail
    - Type-based routing: Different event types trigger different downstream actions

    Example event types for AI systems:
    - LLMResponseGenerated: Captures model output with metadata
    - DocumentIndexed: Records successful vector storage operation
    - ValidationFailed: Documents why an AI output was rejected
    - ThresholdExceeded: Signals when metrics cross boundaries

    This is an abstract base - create domain-specific events for your AI workflow.
    """

    @model_validator(mode="after")
    def _validate_event(self) -> "Event":
        """Validate Event constraints.

        Returns:
            Self after validation.

        Raises:
            TypeError: If trying to instantiate Event directly.
            ValueError: If triggered_by_id is None for an Event.

        """
        # Prevent direct instantiation of abstract base class
        if type(self) is Event:
            msg = (
                "Cannot instantiate abstract Event directly. "
                "Create a concrete event class (e.g., ProcessedEvent, ValidationFailedEvent)."
            )
            raise TypeError(msg)

        # Validate that triggered_by_id is set for events
        if self.triggered_by_id is None:
            msg = "Events must have a triggered_by_id"
            raise ValueError(msg)

        return self


class Command(Message):
    """Imperative request for an action to be performed in the AI workflow.

    Commands express intent and trigger operations like LLM calls, data retrieval, or analysis.
    Initial commands (triggered_by_id=None) start new flow executions.

    Why use Command:
    - Clear intent: Commands use imperative language (ProcessDocument, GenerateResponse)
    - Flow initiation: Commands with triggered_by_id=None start new workflows
    - Decoupled execution: Nodes decide HOW to fulfill commands independently
    - Request/response pattern: Commands trigger events upon completion

    Example command types for AI systems:
    - AnalyzeDocument: Request document understanding via LLM
    - RetrieveContext: Fetch relevant vectors from embedding store
    - GenerateSummary: Produce condensed output from source material
    - ValidateOutput: Check AI response against quality criteria

    This is an abstract base - create domain-specific commands for your AI operations.
    """

    @model_validator(mode="after")
    def _validate_command(self) -> "Command":
        """Validate Command constraints.

        Returns:
            Self after validation.

        Raises:
            TypeError: If trying to instantiate Command directly.

        """
        # Prevent direct instantiation of abstract base class
        if type(self) is Command:
            msg = (
                "Cannot instantiate abstract Command directly. "
                "Create a concrete command class (e.g., ProcessCommand, ValidateCommand)."
            )
            raise TypeError(msg)

        return self
