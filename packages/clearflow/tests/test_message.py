"""Test Message, Command, and Event base classes.

This module tests the message hierarchy including automatic field generation,
causality tracking, and immutability guarantees for mission-critical AI.

"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from clearflow import Command, Event, Message
from tests.conftest import (
    ProcessCommand,
    ProcessedEvent,
    ValidationFailedEvent,
    create_run_id,
    create_test_command,
    create_test_event,
)


def test_message_auto_generated_fields() -> None:
    """Test that id and timestamp are auto-generated."""
    run_id = create_run_id()
    cmd = ProcessCommand(
        data="test",
        triggered_by_id=None,
        run_id=run_id,
    )

    # Verify auto-generated fields
    assert isinstance(cmd.id, uuid.UUID)
    assert isinstance(cmd.timestamp, datetime)
    assert cmd.timestamp.tzinfo == UTC

    # Verify each instance gets unique ID
    cmd2 = ProcessCommand(
        data="test2",
        triggered_by_id=None,
        run_id=run_id,
    )
    assert cmd.id != cmd2.id


def test_message_immutability() -> None:
    """Test that messages are deeply immutable."""
    cmd = create_test_command()

    # Should not be able to modify fields
    with pytest.raises(ValidationError, match="frozen"):
        cmd.data = "modified"

    with pytest.raises(ValidationError, match="frozen"):
        cmd.id = uuid.uuid4()


def test_message_causality_tracking() -> None:
    """Test message causality chain tracking."""
    run_id = create_run_id()

    # Initial command has no trigger
    cmd = ProcessCommand(
        data="start",
        triggered_by_id=None,
        run_id=run_id,
    )
    assert cmd.triggered_by_id is None

    # Event must have trigger
    evt = ProcessedEvent(
        result="done",
        processing_time_ms=100.0,
        triggered_by_id=cmd.id,
        run_id=run_id,
    )
    assert evt.triggered_by_id == cmd.id

    # Chain continues
    next_evt = ValidationFailedEvent(
        reason="invalid",
        triggered_by_id=evt.id,
        run_id=run_id,
    )
    assert next_evt.triggered_by_id == evt.id


def test_flow_tracking() -> None:
    """Test that messages track their flow session."""
    flow1 = create_run_id()
    flow2 = create_run_id()

    cmd1 = ProcessCommand(data="flow1", triggered_by_id=None, run_id=flow1)
    cmd2 = ProcessCommand(data="flow2", triggered_by_id=None, run_id=flow2)

    assert cmd1.run_id == flow1
    assert cmd2.run_id == flow2
    assert cmd1.run_id != cmd2.run_id


def test_command_optional_trigger() -> None:
    """Test that commands can have optional triggered_by_id."""
    run_id = create_run_id()

    # Command without trigger (initial command)
    cmd1 = ProcessCommand(
        data="initial",
        triggered_by_id=None,
        run_id=run_id,
    )
    assert cmd1.triggered_by_id is None

    # Command with trigger (chained command)
    cmd2 = ProcessCommand(
        data="chained",
        triggered_by_id=cmd1.id,
        run_id=run_id,
    )
    assert cmd2.triggered_by_id == cmd1.id


def _assert_has_message_fields(obj: Message) -> None:
    """Assert object has all required Message fields."""
    assert hasattr(obj, "id")
    assert hasattr(obj, "timestamp")
    assert hasattr(obj, "run_id")
    assert hasattr(obj, "triggered_by_id")


def test_command_inheritance() -> None:
    """Test that Command properly inherits from Message."""
    cmd = create_test_command()
    _assert_has_message_fields(cmd)
    assert isinstance(cmd, Message)
    assert isinstance(cmd, Command)


def test_command_concrete_implementation() -> None:
    """Test concrete command implementation with custom fields."""
    run_id = create_run_id()
    cmd = ProcessCommand(
        data="important data",
        priority=5,
        triggered_by_id=None,
        run_id=run_id,
    )

    assert cmd.data == "important data"
    assert cmd.priority == 5
    assert cmd.run_id == run_id


def test_event_required_trigger() -> None:
    """Test that events MUST have triggered_by_id."""
    run_id = create_run_id()
    trigger_id = uuid.uuid4()

    # Event with trigger works
    evt = ProcessedEvent(
        result="success",
        processing_time_ms=50.0,
        triggered_by_id=trigger_id,
        run_id=run_id,
    )
    assert evt.triggered_by_id == trigger_id

    # Event without trigger should fail - ValueError from __post_init__
    with pytest.raises(ValueError, match="Events must have a triggered_by_id") as exc_info:
        ProcessedEvent(
            result="success",
            processing_time_ms=50.0,
            triggered_by_id=None,
            run_id=run_id,
        )
    assert "Events must have a triggered_by_id" in str(exc_info.value)


def test_event_inheritance() -> None:
    """Test that Event properly inherits from Message."""
    evt = create_test_event()
    _assert_has_message_fields(evt)
    assert isinstance(evt, Message)
    assert isinstance(evt, Event)


def test_event_concrete_implementation() -> None:
    """Test concrete event implementation with custom fields."""
    run_id = create_run_id()
    trigger_id = uuid.uuid4()

    evt = ValidationFailedEvent(
        reason="Invalid format",
        errors=("Missing field X", "Invalid type for Y"),
        triggered_by_id=trigger_id,
        run_id=run_id,
    )

    assert evt.reason == "Invalid format"
    assert evt.errors == ("Missing field X", "Invalid type for Y")
    assert evt.triggered_by_id == trigger_id
    assert evt.run_id == run_id


def test_event_immutable_collections() -> None:
    """Test that event collections are immutable."""
    evt = ValidationFailedEvent(
        reason="test",
        errors=("error1", "error2"),
        triggered_by_id=uuid.uuid4(),
        run_id=create_run_id(),
    )

    # Tuple is immutable
    assert isinstance(evt.errors, tuple)
    with pytest.raises(AttributeError):
        evt.errors.append("error3")  # type: ignore[attr-defined]


def test_message_equality() -> None:
    """Test that messages with same fields are equal."""
    run_id = create_run_id()
    trigger_id = uuid.uuid4()

    # Commands should not be equal even with same data (different IDs)
    cmd1 = ProcessCommand(data="same", triggered_by_id=None, run_id=run_id)
    cmd2 = ProcessCommand(data="same", triggered_by_id=None, run_id=run_id)
    assert cmd1 != cmd2  # Different auto-generated IDs

    # Events should not be equal even with same data
    evt1 = ProcessedEvent(
        result="same",
        processing_time_ms=100.0,
        triggered_by_id=trigger_id,
        run_id=run_id,
    )
    evt2 = ProcessedEvent(
        result="same",
        processing_time_ms=100.0,
        triggered_by_id=trigger_id,
        run_id=run_id,
    )
    assert evt1 != evt2  # Different auto-generated IDs


def test_message_hashability() -> None:
    """Test that messages have unique IDs for identification."""
    cmd = create_test_command()
    evt = create_test_event()

    # BaseModel instances are not hashable by default in Pydantic
    # This is expected behavior - we use IDs for uniqueness instead
    _assert_unique_ids(cmd, evt)
    _assert_same_data_different_ids(cmd)


def _assert_unique_ids(cmd: ProcessCommand, evt: ProcessedEvent) -> None:
    """Assert that commands and events have unique UUIDs."""
    assert cmd.id != evt.id
    assert isinstance(cmd.id, uuid.UUID)
    assert isinstance(evt.id, uuid.UUID)


def _assert_same_data_different_ids(cmd: ProcessCommand) -> None:
    """Assert that messages with same data have different IDs."""
    cmd2 = create_test_command()
    assert cmd.id != cmd2.id
    assert cmd.data == cmd2.data


def _assert_polymorphic_message_properties(msg: Message) -> None:
    """Assert message has polymorphic properties."""
    assert isinstance(msg, Message)
    assert hasattr(msg, "id")
    assert hasattr(msg, "timestamp")
    assert hasattr(msg, "run_id")


def test_message_polymorphism() -> None:
    """Test that messages can be used polymorphically."""
    messages: tuple[Message, ...] = (
        create_test_command(),
        create_test_event(),
    )

    for msg in messages:
        _assert_polymorphic_message_properties(msg)


def _assert_command_type_checks(cmd: Message) -> None:
    """Assert command is Command but not Event."""
    assert isinstance(cmd, Command)
    assert not isinstance(cmd, Event)


def _assert_event_type_checks(evt: Message) -> None:
    """Assert event is Event but not Command."""
    assert isinstance(evt, Event)
    assert not isinstance(evt, Command)


def test_command_event_distinction() -> None:
    """Test that Commands and Events are distinct types."""
    cmd = create_test_command()
    evt = create_test_event()

    _assert_command_type_checks(cmd)
    _assert_event_type_checks(evt)

    # Both are Messages
    assert isinstance(cmd, Message)
    assert isinstance(evt, Message)


def test_cannot_instantiate_event_directly() -> None:
    """Test that Event cannot be instantiated directly."""
    run_id = create_run_id()

    with pytest.raises(TypeError, match="Cannot instantiate abstract Event directly"):
        Event(
            triggered_by_id=uuid.uuid4(),
            run_id=run_id,
        )


def test_cannot_instantiate_command_directly() -> None:
    """Test that Command cannot be instantiated directly."""
    run_id = create_run_id()

    with pytest.raises(TypeError, match="Cannot instantiate abstract Command directly"):
        Command(
            triggered_by_id=None,
            run_id=run_id,
        )
