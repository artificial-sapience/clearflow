"""Test Message, Command, and Event base classes.

This module tests the message hierarchy including automatic field generation,
causality tracking, and immutability guarantees for mission-critical AI.

"""

import uuid
from dataclasses import FrozenInstanceError, dataclass
from datetime import UTC, datetime

import pytest

from clearflow.message import Command, Event, Message
from tests.conftest_message import (
    ProcessCommand,
    ProcessedEvent,
    ValidationFailedEvent,
    create_flow_id,
    create_test_command,
    create_test_event,
)


class TestMessage:
    """Test the abstract Message base class."""

    async def test_message_type_property(self) -> None:
        """Test that message_type returns the concrete class type."""
        # Create a command instance
        cmd = create_test_command()
        assert cmd.message_type == ProcessCommand

        # Create an event instance
        evt = create_test_event()
        assert evt.message_type == ProcessedEvent

    async def test_message_auto_generated_fields(self) -> None:
        """Test that id and timestamp are auto-generated."""
        flow_id = create_flow_id()
        cmd = ProcessCommand(
            data="test",
            triggered_by_id=None,
            flow_id=flow_id,
        )

        # Verify auto-generated fields
        assert isinstance(cmd.id, uuid.UUID)
        assert isinstance(cmd.timestamp, datetime)
        assert cmd.timestamp.tzinfo == UTC

        # Verify each instance gets unique ID
        cmd2 = ProcessCommand(
            data="test2",
            triggered_by_id=None,
            flow_id=flow_id,
        )
        assert cmd.id != cmd2.id

    async def test_message_immutability(self) -> None:
        """Test that messages are deeply immutable."""
        cmd = create_test_command()

        # Should not be able to modify fields
        with pytest.raises(FrozenInstanceError):
            cmd.data = "modified"  # type: ignore[misc]

        with pytest.raises(FrozenInstanceError):
            cmd.id = uuid.uuid4()  # type: ignore[misc]

    async def test_message_causality_tracking(self) -> None:
        """Test message causality chain tracking."""
        flow_id = create_flow_id()

        # Initial command has no trigger
        cmd = ProcessCommand(
            data="start",
            triggered_by_id=None,
            flow_id=flow_id,
        )
        assert cmd.triggered_by_id is None

        # Event must have trigger
        evt = ProcessedEvent(
            result="done",
            processing_time_ms=100.0,
            triggered_by_id=cmd.id,
            flow_id=flow_id,
        )
        assert evt.triggered_by_id == cmd.id

        # Chain continues
        next_evt = ValidationFailedEvent(
            reason="invalid",
            triggered_by_id=evt.id,
            flow_id=flow_id,
        )
        assert next_evt.triggered_by_id == evt.id

    async def test_message_flow_tracking(self) -> None:
        """Test that messages track their flow session."""
        flow1 = create_flow_id()
        flow2 = create_flow_id()

        cmd1 = ProcessCommand(data="flow1", triggered_by_id=None, flow_id=flow1)
        cmd2 = ProcessCommand(data="flow2", triggered_by_id=None, flow_id=flow2)

        assert cmd1.flow_id == flow1
        assert cmd2.flow_id == flow2
        assert cmd1.flow_id != cmd2.flow_id


class TestCommand:
    """Test the Command base class."""

    async def test_command_optional_trigger(self) -> None:
        """Test that commands can have optional triggered_by_id."""
        flow_id = create_flow_id()

        # Command without trigger (initial command)
        cmd1 = ProcessCommand(
            data="initial",
            triggered_by_id=None,
            flow_id=flow_id,
        )
        assert cmd1.triggered_by_id is None

        # Command with trigger (chained command)
        cmd2 = ProcessCommand(
            data="chained",
            triggered_by_id=cmd1.id,
            flow_id=flow_id,
        )
        assert cmd2.triggered_by_id == cmd1.id

    async def test_command_inheritance(self) -> None:
        """Test that Command properly inherits from Message."""
        cmd = create_test_command()

        # Should have all Message fields
        assert hasattr(cmd, "id")
        assert hasattr(cmd, "timestamp")
        assert hasattr(cmd, "flow_id")
        assert hasattr(cmd, "triggered_by_id")

        # Should be a Message
        assert isinstance(cmd, Message)
        assert isinstance(cmd, Command)

    async def test_command_concrete_implementation(self) -> None:
        """Test concrete command implementation with custom fields."""
        flow_id = create_flow_id()
        cmd = ProcessCommand(
            data="important data",
            priority=5,
            triggered_by_id=None,
            flow_id=flow_id,
        )

        assert cmd.data == "important data"
        assert cmd.priority == 5
        assert cmd.flow_id == flow_id


class TestEvent:
    """Test the Event base class."""

    async def test_event_required_trigger(self) -> None:
        """Test that events MUST have triggered_by_id."""
        flow_id = create_flow_id()
        trigger_id = uuid.uuid4()

        # Event with trigger works
        evt = ProcessedEvent(
            result="success",
            processing_time_ms=50.0,
            triggered_by_id=trigger_id,
            flow_id=flow_id,
        )
        assert evt.triggered_by_id == trigger_id

        # Event without trigger should fail - ValueError from __post_init__
        with pytest.raises(ValueError) as exc_info:
            ProcessedEvent(
                result="success",
                processing_time_ms=50.0,
                triggered_by_id=None,  # type: ignore[arg-type]
                flow_id=flow_id,
            )
        assert "Events must have a triggered_by_id" in str(exc_info.value)

    async def test_event_inheritance(self) -> None:
        """Test that Event properly inherits from Message."""
        evt = create_test_event()

        # Should have all Message fields
        assert hasattr(evt, "id")
        assert hasattr(evt, "timestamp")
        assert hasattr(evt, "flow_id")
        assert hasattr(evt, "triggered_by_id")

        # Should be a Message
        assert isinstance(evt, Message)
        assert isinstance(evt, Event)

    async def test_event_concrete_implementation(self) -> None:
        """Test concrete event implementation with custom fields."""
        flow_id = create_flow_id()
        trigger_id = uuid.uuid4()

        evt = ValidationFailedEvent(
            reason="Invalid format",
            errors=("Missing field X", "Invalid type for Y"),
            triggered_by_id=trigger_id,
            flow_id=flow_id,
        )

        assert evt.reason == "Invalid format"
        assert evt.errors == ("Missing field X", "Invalid type for Y")
        assert evt.triggered_by_id == trigger_id
        assert evt.flow_id == flow_id

    async def test_event_immutable_collections(self) -> None:
        """Test that event collections are immutable."""
        evt = ValidationFailedEvent(
            reason="test",
            errors=("error1", "error2"),
            triggered_by_id=uuid.uuid4(),
            flow_id=create_flow_id(),
        )

        # Tuple is immutable
        assert isinstance(evt.errors, tuple)
        with pytest.raises(AttributeError):
            evt.errors.append("error3")  # type: ignore[attr-defined]


class TestMessageComparison:
    """Test message equality and hashing."""

    async def test_message_equality(self) -> None:
        """Test that messages with same fields are equal."""
        flow_id = create_flow_id()
        trigger_id = uuid.uuid4()

        # Commands should not be equal even with same data (different IDs)
        cmd1 = ProcessCommand(data="same", triggered_by_id=None, flow_id=flow_id)
        cmd2 = ProcessCommand(data="same", triggered_by_id=None, flow_id=flow_id)
        assert cmd1 != cmd2  # Different auto-generated IDs

        # Events should not be equal even with same data
        evt1 = ProcessedEvent(
            result="same",
            processing_time_ms=100.0,
            triggered_by_id=trigger_id,
            flow_id=flow_id,
        )
        evt2 = ProcessedEvent(
            result="same",
            processing_time_ms=100.0,
            triggered_by_id=trigger_id,
            flow_id=flow_id,
        )
        assert evt1 != evt2  # Different auto-generated IDs

    async def test_message_hashability(self) -> None:
        """Test that messages are hashable (for use in sets/dicts)."""
        cmd = create_test_command()
        evt = create_test_event()

        # Should be hashable
        cmd_hash = hash(cmd)
        evt_hash = hash(evt)

        # Can be used in sets
        message_set = {cmd, evt}
        assert len(message_set) == 2

        # Can be used as dict keys
        message_dict = {cmd: "command", evt: "event"}
        assert message_dict[cmd] == "command"
        assert message_dict[evt] == "event"


class TestMessageTypeHierarchy:
    """Test the message type hierarchy and polymorphism."""

    async def test_message_polymorphism(self) -> None:
        """Test that messages can be used polymorphically."""
        messages: tuple[Message, ...] = (
            create_test_command(),
            create_test_event(),
        )

        for msg in messages:
            assert isinstance(msg, Message)
            assert hasattr(msg, "id")
            assert hasattr(msg, "timestamp")
            assert hasattr(msg, "flow_id")

    async def test_command_event_distinction(self) -> None:
        """Test that Commands and Events are distinct types."""
        cmd = create_test_command()
        evt = create_test_event()

        # Type checks
        assert isinstance(cmd, Command)
        assert not isinstance(cmd, Event)

        assert isinstance(evt, Event)
        assert not isinstance(evt, Command)

        # Both are Messages
        assert isinstance(cmd, Message)
        assert isinstance(evt, Message)
