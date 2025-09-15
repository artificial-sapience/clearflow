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
    """Base message class for all messages in the system.

    All messages are immutable via StrictBaseModel with causality tracking.
    Messages form the foundation of type-safe routing and orchestration.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    triggered_by_id: uuid.UUID | None = None  # None for initial commands, UUID for derived messages
    timestamp: AwareDatetime = Field(default_factory=_utc_now)
    run_id: uuid.UUID  # Required - identifies the flow session

    @property
    def message_type(self) -> type["Message"]:
        """Return the concrete message type for routing."""
        return type(self)


class Event(Message):
    """Abstract base Event extending Message for causality tracking.

    Events capture facts - things that have happened in the system.
    Events MUST have a triggered_by_id (unlike Commands which can be initial).

    This is an abstract base class - users must create concrete event types
    like ProcessedEvent, ValidationFailedEvent, etc.

    Inherits from Message:
        id: Unique identifier for this message
        triggered_by_id: UUID of the message that triggered this event (required for events)
        timestamp: Timezone-aware datetime for unambiguous event ordering
        run_id: UUID identifying the flow session
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
    """Abstract base Command extending Message for causality tracking.

    Commands capture intent - requests for something to happen.
    Commands can have triggered_by_id=None (initial commands that start flows).

    This is an abstract base class - users must create concrete command types
    like ProcessCommand, ValidateCommand, etc.

    Inherits from Message:
        id: Unique identifier for this message
        triggered_by_id: UUID of the message that triggered this command (optional)
        timestamp: Timezone-aware datetime for unambiguous command ordering
        run_id: UUID identifying the flow session
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
