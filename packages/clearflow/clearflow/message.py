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
    """Abstract base class for Commands and Events in message-driven flows.

    A Message is an immutable data structure that flows between nodes, carrying
    both domain data and metadata for causality tracking and flow isolation.

    Attributes:
        id: Unique identifier for this message instance
        triggered_by_id: ID of the message that caused this one (None for root commands)
        timestamp: UTC time when this message was created
        run_id: Session identifier linking all messages in a single flow execution

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
    """An immutable record of something that has occurred.

    Events represent facts about state changes or completed actions in the system.
    They are named in past tense (e.g., OrderPlaced, DocumentProcessed) and
    must always have a triggered_by_id linking to the message that caused them.

    Events cannot be rejected or modified - they represent what has already happened.
    If an error occurs, emit a new event describing the failure rather than
    trying to undo the original event.

    Constraints:
        - Must have triggered_by_id (cannot be None)
        - Cannot be instantiated directly (create concrete subclasses)
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
    """An imperative request to perform an action that may change state.

    Commands express intent to transform or process data. They are named
    using imperative verbs (e.g., ProcessOrder, ValidateDocument) and are
    processed by a single node that decides how to fulfill the request.

    Commands may result in:
        - One or more events describing what happened
        - Error events if the operation fails

    Root commands (triggered_by_id=None) initiate new flow executions.

    Constraints:
        - Cannot be instantiated directly (create concrete subclasses)
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
