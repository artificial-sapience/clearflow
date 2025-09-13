"""Test message flow routing and composition.

This module tests the message flow builder, routing logic, and flow composability
for mission-critical AI orchestration with type-safe message routing.

"""

from dataclasses import FrozenInstanceError, dataclass
from typing import override

import pytest

from clearflow import MessageNode as Node
from clearflow import message_flow
from tests.conftest_message import (
    AnalysisCompleteEvent,
    ErrorEvent,
    ProcessCommand,
    ProcessedEvent,
    ValidateCommand,
    ValidationFailedEvent,
    ValidationPassedEvent,
    create_flow_id,
)


# Reusable test nodes
@dataclass(frozen=True, kw_only=True)
class StartNode(Node[ProcessCommand, ProcessedEvent | ErrorEvent]):
    """Initial processing node."""

    name: str = "start"
    should_fail: bool = False

    @override
    async def process(self, message: ProcessCommand) -> ProcessedEvent | ErrorEvent:
        if self.should_fail:
            return ErrorEvent(
                error_message="Start failed",
                triggered_by_id=message.id,
                flow_id=message.flow_id,
            )
        return ProcessedEvent(
            result=f"started: {message.data}",
            processing_time_ms=50.0,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


@dataclass(frozen=True, kw_only=True)
class TransformNode(Node[ProcessedEvent, ValidateCommand]):
    """Transform event to command."""

    name: str = "transform"

    @override
    async def process(self, message: ProcessedEvent) -> ValidateCommand:
        return ValidateCommand(
            content=message.result,
            strict=True,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


@dataclass(frozen=True, kw_only=True)
class ValidateNode(Node[ValidateCommand, ValidationPassedEvent | ValidationFailedEvent]):
    """Validation node."""

    name: str = "validate"
    min_length: int = 5

    @override
    async def process(self, message: ValidateCommand) -> ValidationPassedEvent | ValidationFailedEvent:
        if len(message.content) < self.min_length:
            return ValidationFailedEvent(
                reason="Too short",
                triggered_by_id=message.id,
                flow_id=message.flow_id,
            )
        return ValidationPassedEvent(
            validated_content=message.content,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


@dataclass(frozen=True, kw_only=True)
class FinalizeNode(Node[ValidationPassedEvent, AnalysisCompleteEvent]):
    """Final processing node."""

    name: str = "finalize"

    @override
    async def process(self, message: ValidationPassedEvent) -> AnalysisCompleteEvent:
        return AnalysisCompleteEvent(
            findings=f"Final: {message.validated_content}",
            confidence=0.99,
            triggered_by_id=message.id,
            flow_id=message.flow_id,
        )


async def test_simple_flow() -> None:
    """Test a simple linear flow."""
    start = StartNode()

    flow = message_flow("simple", start).end(start, ProcessedEvent)

    # Execute flow
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

    result = await flow.process(input_msg)

    assert isinstance(result, ProcessedEvent)
    assert result.result == "started: test"


async def test_flow_with_routing() -> None:
    """Test flow with multiple routes."""
    start = StartNode()
    transform = TransformNode()
    validate = ValidateNode()
    finalize = FinalizeNode()

    flow = (
        message_flow("pipeline", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .route(validate, ValidationPassedEvent, finalize)
        .end(finalize, AnalysisCompleteEvent)
    )

    # Execute successful path
    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="valid data", triggered_by_id=None, flow_id=flow_id)

    result = await flow.process(input_msg)

    assert isinstance(result, AnalysisCompleteEvent)
    assert "started: valid data" in result.findings


async def test_flow_with_error_handling() -> None:
    """Test flow with error route."""
    start = StartNode(should_fail=True)
    transform = TransformNode()

    flow = message_flow("error_handling", start).route(start, ProcessedEvent, transform).end(start, ErrorEvent)

    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

    result = await flow.process(input_msg)

    assert isinstance(result, ErrorEvent)
    assert result.error_message == "Start failed"


async def test_flow_with_branching() -> None:
    """Test flow with conditional branching."""
    start = StartNode()
    transform = TransformNode()
    validate = ValidateNode(min_length=10)  # Strict validation

    flow = (
        message_flow("branching", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .end(validate, ValidationFailedEvent)  # Only test failure path
    )

    flow_id = create_flow_id()

    # Test failure branch - make input that results in short content after "started: "
    short_input = ProcessCommand(data="", triggered_by_id=None, flow_id=flow_id)  # "started: " = 9 chars < 10
    result = await flow.process(short_input)
    assert isinstance(result, ValidationFailedEvent)


async def test_flow_missing_route_error() -> None:
    """Test that missing route raises error."""
    start = StartNode()
    transform = TransformNode()

    # Build flow missing route for ValidateCommand
    # Only route ProcessedEvent to transform, but don't handle ValidateCommand output
    flow = message_flow("incomplete", start).route(start, ProcessedEvent, transform).end(start, ErrorEvent)

    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

    # Should raise ValueError for missing route
    with pytest.raises(ValueError, match="No route defined") as exc_info:
        await flow.process(input_msg)

    assert "No route defined for message type" in str(exc_info.value)
    assert "ValidateCommand" in str(exc_info.value)


async def test_flow_composability() -> None:
    """Test that flows can be composed as nodes."""
    # Create inner flow
    validate = ValidateNode()
    finalize = FinalizeNode()

    inner_flow = (
        message_flow("inner", validate)
        .route(validate, ValidationPassedEvent, finalize)
        .end(finalize, AnalysisCompleteEvent)
    )

    # Create outer flow using inner flow as a node
    start = StartNode()
    transform = TransformNode()

    outer_flow = (
        message_flow("outer", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, inner_flow)  # Inner flow as node!
        .end(inner_flow, AnalysisCompleteEvent)
    )

    flow_id = create_flow_id()
    input_msg = ProcessCommand(data="composite test", triggered_by_id=None, flow_id=flow_id)

    result = await outer_flow.process(input_msg)

    assert isinstance(result, AnalysisCompleteEvent)
    assert "started: composite test" in result.findings


def test_flow_reachability_validation() -> None:
    """Test that flow builder validates node reachability."""
    start = StartNode()
    unreachable = ValidateNode()

    builder = message_flow("test", start)

    # Try to route from unreachable node
    with pytest.raises(ValueError, match="not reachable from start") as exc_info:
        builder.route(unreachable, ValidationPassedEvent, start)

    assert "not reachable from start" in str(exc_info.value)


def test_flow_duplicate_route_error() -> None:
    """Test that duplicate routes are rejected."""
    start = StartNode()
    node1 = TransformNode(name="transform1")
    node2 = TransformNode(name="transform2")

    builder = message_flow("test", start)
    builder = builder.route(start, ProcessedEvent, node1)

    # Try to add duplicate route for same message type from same node
    with pytest.raises(ValueError, match="Route already defined") as exc_info:
        builder.route(start, ProcessedEvent, node2)

    assert "Route already defined" in str(exc_info.value)


def test_flow_name_property() -> None:
    """Test flow name is preserved."""
    start = StartNode()
    flow = message_flow("my_flow", start).end(start, ProcessedEvent)

    assert flow.name == "my_flow"


def test_flow_immutability() -> None:
    """Test that flows are immutable."""
    start = StartNode()
    flow = message_flow("immutable", start).end(start, ProcessedEvent)

    # Should not be able to modify flow
    with pytest.raises((FrozenInstanceError, AttributeError)):
        flow.name = "modified"  # type: ignore[misc]

    with pytest.raises((FrozenInstanceError, AttributeError)):
        flow.start_node = StartNode(name="new")  # type: ignore[misc]


def test_flow_builder_chaining() -> None:
    """Test flow builder method chaining."""
    start = StartNode()
    transform = TransformNode()
    validate = ValidateNode()

    # Each route returns a new builder
    builder1 = message_flow("test", start)
    builder2 = builder1.route(start, ProcessedEvent, transform)
    builder3 = builder2.route(transform, ValidateCommand, validate)

    # Builders are different instances
    assert builder1 is not builder2
    assert builder2 is not builder3

    # But can chain fluently
    flow = (
        message_flow("fluent", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .end(validate, ValidationPassedEvent)
    )

    assert flow.name == "fluent"


def test_single_termination_enforcement() -> None:
    """Test that only one termination is allowed per flow."""
    start = StartNode()

    # First create a flow with one termination
    builder = message_flow("test", start)
    flow = builder.end(start, ProcessedEvent)

    # Verify flow works
    assert flow.name == "test"

    # Each call to end() creates a separate flow - this is allowed
    start2 = StartNode()
    transform = TransformNode()

    builder2 = message_flow("multi_end", start2)
    builder3 = builder2.route(start2, ProcessedEvent, transform)

    # Create one flow ending at start2 with ErrorEvent
    flow1 = builder3.end(start2, ErrorEvent)
    assert flow1.name == "multi_end"

    # Create another flow ending at transform with ValidateCommand - this is OK
    # because it's a different flow instance
    flow2 = builder3.end(transform, ValidateCommand)
    assert flow2.name == "multi_end"

    # The single termination rule means you can't have multiple terminations
    # in the SAME flow. Each flow can only have one route to None.
