"""Test observer pattern for message flows.

This module tests the observer pattern including fail-fast behavior,
concurrent execution, and decorator-based flow observation.

"""

from dataclasses import FrozenInstanceError, dataclass
from typing import override

import pytest

from clearflow import Event, Message, MessageFlow, ObservableFlow, Observer, message_flow
from clearflow import MessageNode as Node
from tests.conftest_message import (
    ProcessCommand,
    ProcessedEvent,
    ValidateCommand,
    ValidationFailedEvent,
    ValidationPassedEvent,
    create_flow_id,
)


# Test observers
@dataclass(frozen=True, kw_only=True)
class LoggingObserver(Observer[Message]):
    """Observer that logs all messages."""

    name: str = "logger"
    logged_messages: list[Message]  # Mutable for testing

    @override
    async def observe(self, message: Message) -> None:
        self.logged_messages.append(message)


@dataclass(frozen=True, kw_only=True)
class EventCountObserver(Observer[Event]):
    """Observer that counts events."""

    name: str = "event_counter"
    event_count: list[int]  # Mutable list to track count

    @override
    async def observe(self, message: Event) -> None:
        self.event_count[0] += 1


@dataclass(frozen=True, kw_only=True)
class SecurityObserver(Observer[ProcessedEvent]):
    """Observer that checks for security issues."""

    name: str = "security"
    forbidden_words: tuple[str, ...] = ("danger", "hack", "exploit")

    @override
    async def observe(self, message: ProcessedEvent) -> None:
        for word in self.forbidden_words:
            if word in message.result.lower():
                # Fail-fast: exception stops flow
                error_msg = f"Security violation: forbidden word '{word}'"
                raise SecurityError(error_msg)


@dataclass(frozen=True, kw_only=True)
class ValidationObserver(Observer[ValidationFailedEvent]):
    """Observer for validation failures."""

    name: str = "validation_observer"
    failure_log: list[str]  # Mutable for testing

    @override
    async def observe(self, message: ValidationFailedEvent) -> None:
        self.failure_log.append(message.reason)


# Test exception
class SecurityError(Exception):
    """Error raised by security observer."""


# Test nodes for flows
@dataclass(frozen=True, kw_only=True)
class SimpleProcessorNode(Node[ProcessCommand, ProcessedEvent]):
    """Simple processor for testing."""

    name: str = "processor"

    @override
    async def process(self, message: ProcessCommand) -> ProcessedEvent:
        return ProcessedEvent(
            result=f"processed: {message.data}",
            processing_time_ms=10.0,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


@dataclass(frozen=True, kw_only=True)
class TransformerNode(Node[ProcessedEvent, ValidateCommand]):
    """Transform processor output to validation input."""

    name: str = "transformer"

    @override
    async def process(self, message: ProcessedEvent) -> ValidateCommand:
        return ValidateCommand(
            content=message.result,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


@dataclass(frozen=True, kw_only=True)
class ValidatorNode(Node[ValidateCommand, ValidationPassedEvent | ValidationFailedEvent]):
    """Validator node."""

    name: str = "validator"

    @override
    async def process(self, message: ValidateCommand) -> ValidationPassedEvent | ValidationFailedEvent:
        if "fail" in message.content:
            return ValidationFailedEvent(
                reason="Contains 'fail'",
                triggered_by_id=message.id,
                flow_id=message.flow_id,
            )
        return ValidationPassedEvent(
            validated_content=message.content,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


async def test_observer_basic_functionality() -> None:
    """Test basic observer functionality."""
    logged: list[Message] = []
    observer = LoggingObserver(logged_messages=logged)

    flow_id = create_flow_id()
    msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

    await observer.observe(msg)

    assert len(logged) == 1
    assert logged[0] == msg


async def test_observer_type_filtering() -> None:
    """Test that observers can be typed to specific messages."""
    event_count = [0]
    event_observer = EventCountObserver(event_count=event_count)

    flow_id = create_flow_id()

    # Observer handles Event
    event = ProcessedEvent(
        result="test",
        processing_time_ms=1.0,
        triggered_by_id=create_flow_id(),
        flow_id=flow_id,
    )
    await event_observer.observe(event)
    assert event_count[0] == 1


def _create_basic_observable_flow() -> tuple[ObservableFlow[ProcessCommand, ProcessedEvent], list[Message]]:
    """Create a basic observable flow with logger.

    Returns:
        Tuple of observable flow and logged messages list.

    """
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)
    logged: list[Message] = []
    logger = LoggingObserver(logged_messages=logged)
    observable = ObservableFlow(name="observable_test", flow=core_flow, observers={}).observe(Message, logger)
    return observable, logged


def _assert_basic_observations(logged: list[Message]) -> None:
    """Assert basic observations are correct."""
    assert len(logged) == 2  # Input and output
    assert isinstance(logged[0], ProcessCommand)
    assert isinstance(logged[1], ProcessedEvent)


async def test_observable_flow_basic() -> None:
    """Test basic observable flow functionality."""
    observable, logged = _create_basic_observable_flow()

    # Execute flow
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)
    result = await observable.process(input_msg)

    # Check result
    assert isinstance(result, ProcessedEvent)
    assert result.result == "processed: test"
    _assert_basic_observations(logged)


async def test_observable_flow_multiple_observers() -> None:
    """Test flow with multiple observers."""
    # Create flow
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)

    # Create observers
    logged: list[Message] = []
    logger = LoggingObserver(logged_messages=logged)

    event_count = [0]
    event_counter = EventCountObserver(event_count=event_count)

    # Add multiple observers
    observable = (
        ObservableFlow(name="multi_observer", flow=core_flow, observers={})
        .observe(Message, logger)
        .observe(Event, event_counter)
    )

    # Execute
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)
    await observable.process(input_msg)

    # Both observers should have been called
    assert len(logged) == 2  # Input and output
    assert event_count[0] == 1  # Only the output event


async def test_observable_flow_fail_fast() -> None:
    """Test that observer exceptions stop the flow immediately."""
    # Create flow
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)

    # Add security observer that will throw
    security = SecurityObserver(forbidden_words=("danger",))
    observable = ObservableFlow(name="security_test", flow=core_flow, observers={}).observe(ProcessedEvent, security)

    # Execute with forbidden word
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="danger", triggered_by_id=None, flow_id=flow_id)

    # Should raise SecurityError
    with pytest.raises(SecurityError) as exc_info:
        await observable.process(input_msg)

    assert "Security violation" in str(exc_info.value)
    assert "danger" in str(exc_info.value)


def _create_routing_pipeline() -> tuple[SimpleProcessorNode, TransformerNode, ValidatorNode]:
    """Create the nodes for the routing pipeline.

    Returns:
        Tuple of processor, transformer, and validator nodes.

    """
    return SimpleProcessorNode(), TransformerNode(), ValidatorNode()


def _build_core_routing_flow(
    processor: SimpleProcessorNode, transformer: TransformerNode, validator: ValidatorNode
) -> MessageFlow[ProcessCommand, ValidationPassedEvent]:
    """Build the core flow with routing between nodes.

    Returns:
        MessageFlow with routing configured.

    """
    return (
        message_flow("pipeline", processor)
        .route(processor, ProcessedEvent, transformer)
        .route(transformer, ValidateCommand, validator)
        .end(validator, ValidationPassedEvent)
    )


def _assert_routing_messages_logged(logged: list[Message]) -> None:
    """Assert correct messages were logged in routing test."""
    assert len(logged) == 4  # Input + 3 intermediate outputs
    _assert_message_types_correct(logged)


def _assert_message_types_correct(logged: list[Message]) -> None:
    """Assert message types in logged sequence are correct."""
    assert isinstance(logged[0], ProcessCommand)
    assert isinstance(logged[1], ProcessedEvent)
    assert isinstance(logged[2], ValidateCommand)
    assert isinstance(logged[3], ValidationPassedEvent)


async def test_observable_flow_with_routing() -> None:
    """Test observable flow with multiple nodes and routing."""
    processor, transformer, validator = _create_routing_pipeline()
    core_flow = _build_core_routing_flow(processor, transformer, validator)

    # Add observer for all messages
    logged: list[Message] = []
    logger = LoggingObserver(logged_messages=logged)
    observable = ObservableFlow(name="observable_pipeline", flow=core_flow, observers={}).observe(Message, logger)

    # Execute
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="valid", triggered_by_id=None, flow_id=flow_id)
    result = await observable.process(input_msg)

    assert isinstance(result, ValidationPassedEvent)
    _assert_routing_messages_logged(logged)


async def test_observable_flow_inheritance_matching() -> None:
    """Test that observers match on inheritance hierarchy."""
    # Create flow
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)

    # Observer for base Event type
    event_count = [0]
    event_observer = EventCountObserver(event_count=event_count)

    observable = ObservableFlow(name="inheritance_test", flow=core_flow, observers={}).observe(Event, event_observer)

    # Execute
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)
    await observable.process(input_msg)

    # Should match ProcessedEvent as it's an Event
    assert event_count[0] == 1


async def test_observable_flow_specific_message_observation() -> None:
    """Test observing specific message types."""
    # Create flow with failure path
    processor = SimpleProcessorNode()
    transformer = TransformerNode()
    validator = ValidatorNode()

    core_flow = (
        message_flow("pipeline", processor)
        .route(processor, ProcessedEvent, transformer)
        .route(transformer, ValidateCommand, validator)
        .end(validator, ValidationFailedEvent)
    )

    # Observer only for failures
    failure_log: list[str] = []
    failure_observer = ValidationObserver(failure_log=failure_log)

    observable = ObservableFlow(name="failure_test", flow=core_flow, observers={}).observe(
        ValidationFailedEvent, failure_observer
    )

    # Execute with failure input
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="fail", triggered_by_id=None, flow_id=flow_id)
    result = await observable.process(input_msg)

    assert isinstance(result, ValidationFailedEvent)
    assert len(failure_log) == 1
    assert failure_log[0] == "Contains 'fail'"


def test_observable_flow_immutability() -> None:
    """Test that observable flows are immutable."""
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)

    observable = ObservableFlow(name="immutable", flow=core_flow, observers={})

    # Should not be able to modify
    with pytest.raises((FrozenInstanceError, AttributeError)):
        observable.name = "modified"  # type: ignore[misc]


async def test_observable_flow_composability() -> None:
    """Test that observable flows can be composed."""
    # Create inner observable flow
    processor = SimpleProcessorNode()
    inner_flow = message_flow("inner", processor).end(processor, ProcessedEvent)

    logged_inner: list[Message] = []
    inner_logger = LoggingObserver(name="inner_log", logged_messages=logged_inner)

    observable_inner = ObservableFlow(name="observable_inner", flow=inner_flow, observers={}).observe(
        Message, inner_logger
    )

    # Create outer flow using observable inner as a node
    transformer = TransformerNode()
    outer_flow = (
        message_flow("outer", observable_inner)  # Observable as node!
        .route(observable_inner, ProcessedEvent, transformer)
        .end(transformer, ValidateCommand)
    )

    logged_outer: list[Message] = []
    outer_logger = LoggingObserver(name="outer_log", logged_messages=logged_outer)

    observable_outer = ObservableFlow(name="observable_outer", flow=outer_flow, observers={}).observe(
        Message, outer_logger
    )

    # Execute
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="nested", triggered_by_id=None, flow_id=flow_id)
    result = await observable_outer.process(input_msg)

    assert isinstance(result, ValidateCommand)

    # Inner observer saw inner messages
    assert len(logged_inner) == 2  # Input and output of inner flow

    # Outer observer saw all messages in outer flow
    assert len(logged_outer) == 3  # Input, ProcessedEvent, ValidateCommand


async def test_observer_concurrent_execution() -> None:
    """Test that multiple observers execute concurrently."""
    # Create flow
    processor = SimpleProcessorNode()
    core_flow = message_flow("test", processor).end(processor, ProcessedEvent)

    # Create multiple observers
    logged1: list[Message] = []
    logger1 = LoggingObserver(name="log1", logged_messages=logged1)

    logged2: list[Message] = []
    logger2 = LoggingObserver(name="log2", logged_messages=logged2)

    event_count = [0]
    counter = EventCountObserver(event_count=event_count)

    # Add all observers
    observable = (
        ObservableFlow(name="concurrent", flow=core_flow, observers={})
        .observe(Message, logger1)
        .observe(Message, logger2)
        .observe(Event, counter)
    )

    # Execute
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)
    await observable.process(input_msg)

    # All observers should have been called
    assert len(logged1) == 2
    assert len(logged2) == 2
    assert event_count[0] == 1
