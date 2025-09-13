"""Message base classes for message-driven architecture."""

import uuid
from abc import ABC, ABCMeta
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import (  # clearflow: ignore[ARCH010]  # Metaclass protocol requires Any (see typeshed type.__call__)
    Any,
    override,
)

__all__ = [
    "Command",
    "Event",
    "Message",
]


class AbstractMessageMeta(ABCMeta):
    """Metaclass that prevents direct instantiation of Event and Command base classes."""

    @override
    def __call__(
        cls, *args: Any, **kwargs: Any
    ) -> Any:  # clearflow: ignore[ARCH010]  # Standard metaclass signature per typeshed
        """Prevent direct instantiation of abstract Event and Command classes.

        Returns:
            Instance of the class if not Event or Command.

        Raises:
            TypeError: If trying to instantiate Event or Command directly.

        """
        # Prevent direct instantiation of abstract base classes
        if cls.__module__ == "clearflow.message" and cls.__name__ in {"Event", "Command"}:
            examples = {
                "Event": "ProcessedEvent, ValidationFailedEvent",
                "Command": "ProcessCommand, ValidateCommand",
            }
            msg = (
                f"Cannot instantiate abstract {cls.__name__} directly. "
                f"Create a concrete {cls.__name__.lower()} class (e.g., {examples[cls.__name__]})."
            )
            raise TypeError(msg)
        return super().__call__(*args, **kwargs)


def _utc_now() -> datetime:
    """Create a timezone-aware datetime in UTC.

    Returns:
        Current UTC time as datetime.

    """
    return datetime.now(UTC)


@dataclass(frozen=True, kw_only=True)
class Message(ABC):
    """Base message class for all messages in the system.

    All messages are immutable frozen dataclasses with causality tracking.
    Messages form the foundation of type-safe routing and orchestration.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    triggered_by_id: uuid.UUID | None = None  # None for initial commands, UUID for derived messages
    timestamp: datetime = field(default_factory=_utc_now)
    flow_id: uuid.UUID  # Required - identifies the flow session

    @property
    def message_type(self) -> type["Message"]:
        """Return the concrete message type for routing."""
        return type(self)


@dataclass(frozen=True, kw_only=True)
class Event(Message, metaclass=AbstractMessageMeta):
    """Abstract base Event extending Message for causality tracking.

    Events capture facts - things that have happened in the system.
    Events MUST have a triggered_by_id (unlike Commands which can be initial).

    This is an abstract base class - users must create concrete event types
    like ProcessedEvent, ValidationFailedEvent, etc.

    Inherits from Message:
        id: Unique identifier for this message
        triggered_by_id: UUID of the message that triggered this event (required for events)
        timestamp: Timezone-aware datetime for unambiguous event ordering
        flow_id: UUID identifying the flow session
    """

    def __post_init__(self) -> None:
        """Validate that triggered_by_id is set for events.

        Raises:
            ValueError: If triggered_by_id is None for an Event.

        """
        if self.triggered_by_id is None:
            msg = "Events must have a triggered_by_id"
            raise ValueError(msg)


@dataclass(frozen=True, kw_only=True)
class Command(Message, metaclass=AbstractMessageMeta):
    """Abstract base Command extending Message for causality tracking.

    Commands capture intent - requests for something to happen.
    Commands can have triggered_by_id=None (initial commands that start flows).

    This is an abstract base class - users must create concrete command types
    like ProcessCommand, ValidateCommand, etc.

    Inherits from Message:
        id: Unique identifier for this message
        triggered_by_id: UUID of the message that triggered this command (optional)
        timestamp: Timezone-aware datetime for unambiguous command ordering
        flow_id: UUID identifying the flow session
    """

    # Uses default triggered_by_id: uuid.UUID | None from Message
