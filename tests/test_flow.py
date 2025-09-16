"""Test flow routing and composition.

This module tests the flow builder, routing logic, and flow composability
for mission-critical AI orchestration with type-safe message routing.

"""

from typing import override

import pytest
from pydantic import ValidationError

from clearflow import Node, create_flow
from tests.conftest import (
    AnalysisCompleteEvent,
    ErrorEvent,
    ProcessCommand,
    ProcessedEvent,
    SecurityAlertEvent,
    ValidateCommand,
    ValidationFailedEvent,
    ValidationPassedEvent,
    create_run_id,
)


# Reusable test nodes
class StartNode(Node[ProcessCommand, ProcessedEvent | ErrorEvent]):
    """Initial processing node that succeeds."""

    @override
    async def process(self, message: ProcessCommand) -> ProcessedEvent | ErrorEvent:
        return ProcessedEvent(
            result=f"started: {message.data}",
            processing_time_ms=50.0,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class FailingStartNode(Node[ProcessCommand, ProcessedEvent | ErrorEvent]):
    """Initial processing node that always fails."""

    @override
    async def process(self, message: ProcessCommand) -> ProcessedEvent | ErrorEvent:
        return ErrorEvent(
            error_message="Start failed",
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class TransformNode(Node[ProcessedEvent, ValidateCommand]):
    """Transform event to command."""

    @override
    async def process(self, message: ProcessedEvent) -> ValidateCommand:
        return ValidateCommand(
            content=message.result,
            strict=True,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class ValidateNode(Node[ValidateCommand, ValidationPassedEvent | ValidationFailedEvent]):
    """Validation node with default minimum length of 5."""

    @override
    async def process(self, message: ValidateCommand) -> ValidationPassedEvent | ValidationFailedEvent:
        if len(message.content) < 5:
            return ValidationFailedEvent(
                reason="Too short",
                triggered_by_id=message.id,
                run_id=message.run_id,
            )
        return ValidationPassedEvent(
            validated_content=message.content,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class StrictValidateNode(Node[ValidateCommand, ValidationPassedEvent | ValidationFailedEvent]):
    """Validation node with strict minimum length of 10."""

    @override
    async def process(self, message: ValidateCommand) -> ValidationPassedEvent | ValidationFailedEvent:
        if len(message.content) < 10:
            return ValidationFailedEvent(
                reason="Too short",
                triggered_by_id=message.id,
                run_id=message.run_id,
            )
        return ValidationPassedEvent(
            validated_content=message.content,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class FinalizeNode(Node[ValidationPassedEvent, AnalysisCompleteEvent]):
    """Final processing node."""

    @override
    async def process(self, message: ValidationPassedEvent) -> AnalysisCompleteEvent:
        return AnalysisCompleteEvent(
            findings=f"Final: {message.validated_content}",
            confidence=0.99,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


async def test_simple_flow() -> None:
    """Test a simple linear flow."""
    start = StartNode(name="start")

    test_flow = create_flow("simple", start).end_flow(ProcessedEvent)

    # Execute flow
    run_id = create_run_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, run_id=run_id)

    result = await test_flow.process(input_msg)

    assert isinstance(result, ProcessedEvent)
    assert result.result == "started: test"


async def test_flow_with_routing() -> None:
    """Test flow with multiple routes."""
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = ValidateNode(name="validate")
    finalize = FinalizeNode(name="finalize")

    test_flow = (
        create_flow("pipeline", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .route(validate, ValidationPassedEvent, finalize)
        .end_flow(AnalysisCompleteEvent)
    )

    # Execute successful path
    run_id = create_run_id()
    input_msg = ProcessCommand(data="valid data", triggered_by_id=None, run_id=run_id)

    result = await test_flow.process(input_msg)

    assert isinstance(result, AnalysisCompleteEvent)
    assert "started: valid data" in result.findings


async def test_flow_with_error_handling() -> None:
    """Test flow with error route - demonstrates single responsibility.

    This flow's goal: produce an ErrorEvent when failure occurs.
    """
    start = FailingStartNode(name="start")
    transform = TransformNode(name="transform")

    # Simple flow - goal is to detect and report errors
    test_flow = (
        create_flow("error_detection", start)
        .route(start, ProcessedEvent, transform)  # Won't be taken since start fails
        .end_flow(ErrorEvent)  # Goal: detect error condition
    )

    run_id = create_run_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, run_id=run_id)

    result = await test_flow.process(input_msg)

    assert isinstance(result, ErrorEvent)
    assert result.error_message == "Start failed"


async def test_flow_with_branching() -> None:
    """Test flow with conditional branching - failure path."""
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = StrictValidateNode(name="validate")  # Strict validation

    test_flow = (
        create_flow("branching", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .end_flow(ValidationFailedEvent)  # Single terminal type for failure
    )

    run_id = create_run_id()

    # Test failure branch - make input that results in short content after "started: "
    short_input = ProcessCommand(data="", triggered_by_id=None, run_id=run_id)  # "started: " = 9 chars < 10
    result = await test_flow.process(short_input)
    assert isinstance(result, ValidationFailedEvent)


async def test_flow_with_branching_success() -> None:
    """Test flow with conditional branching - success path."""
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = StrictValidateNode(name="validate")  # Strict validation

    test_flow = (
        create_flow("branching", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .end_flow(ValidationPassedEvent)  # Single terminal type for success
    )

    run_id = create_run_id()

    # Test success branch - make input that results in long enough content
    long_input = ProcessCommand(data="long data", triggered_by_id=None, run_id=run_id)  # "started: long data" > 10
    result = await test_flow.process(long_input)
    assert isinstance(result, ValidationPassedEvent)
    assert result.validated_content == "started: long data"


async def test_flow_missing_route_error() -> None:
    """Test that missing route raises error when message can't be routed."""
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = ValidateNode(name="validate")

    # Build flow with incomplete routing - validate outputs ValidationPassedEvent
    # but no route defined for it
    test_flow = (
        create_flow("incomplete", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        # Missing route for ValidationPassedEvent from validate
        .end_flow(ValidationFailedEvent)  # Terminal is ValidationFailedEvent (not reached on success)
    )

    run_id = create_run_id()
    # Use data that will pass validation
    input_msg = ProcessCommand(data="test data", triggered_by_id=None, run_id=run_id)

    # Should raise ValueError for missing route
    with pytest.raises(ValueError, match="No route defined") as exc_info:
        await test_flow.process(input_msg)

    assert "No route defined for message type" in str(exc_info.value)
    assert "ValidationPassedEvent" in str(exc_info.value)


async def test_flow_composability() -> None:
    """Test that flows can be composed as nodes."""
    # Create inner flow
    validate = ValidateNode(name="validate")
    finalize = FinalizeNode(name="finalize")

    inner_flow = (
        create_flow("inner", validate).route(validate, ValidationPassedEvent, finalize).end_flow(AnalysisCompleteEvent)
    )

    # Create outer flow using inner flow as a node
    start = StartNode(name="start")
    transform = TransformNode(name="transform")

    outer_flow = (
        create_flow("outer", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, inner_flow)  # Inner flow as node!
        .end_flow(AnalysisCompleteEvent)  # Terminal type
    )

    run_id = create_run_id()
    input_msg = ProcessCommand(data="composite test", triggered_by_id=None, run_id=run_id)

    result = await outer_flow.process(input_msg)

    assert isinstance(result, AnalysisCompleteEvent)
    assert "started: composite test" in result.findings


def test_flow_invalid_output_type_validation() -> None:
    """Test that flow builder validates output types match node signatures."""
    # Create a node that outputs ProcessedEvent | ErrorEvent
    start = StartNode(name="start")
    # Create a node that expects ValidateCommand
    validate = ValidateNode(name="validate")

    # Try to route ValidationPassedEvent from start (which can't output that type)
    builder = create_flow("test", start)

    # This should raise TypeError because StartNode can't output ValidationPassedEvent
    with pytest.raises(TypeError, match="cannot output ValidationPassedEvent"):
        builder.route(start, ValidationPassedEvent, validate)


def test_flow_invalid_input_type_validation() -> None:
    """Test that flow builder validates input types match node signatures."""
    # StartNode outputs ProcessedEvent | ErrorEvent
    start = StartNode(name="start")
    # ValidateNode expects ValidateCommand, not ProcessedEvent
    validate = ValidateNode(name="validate")

    builder = create_flow("test", start)

    # This should raise TypeError because ValidateNode can't accept ProcessedEvent
    with pytest.raises(TypeError, match="cannot accept ProcessedEvent"):
        builder.route(start, ProcessedEvent, validate)


def test_flow_union_type_compatibility() -> None:
    """Test flow validation handles union types correctly."""

    # Node that outputs union of multiple event types
    class MultiOutputNode(Node[ProcessCommand, ProcessedEvent | ValidationPassedEvent | ErrorEvent]):
        @override
        async def process(self, message: ProcessCommand) -> ProcessedEvent | ValidationPassedEvent | ErrorEvent:
            return ProcessedEvent(
                result="test", processing_time_ms=10.0, triggered_by_id=message.id, run_id=message.run_id
            )

    # Node that accepts one of the union members
    class ProcessedOnlyNode(Node[ProcessedEvent, AnalysisCompleteEvent]):
        @override
        async def process(self, message: ProcessedEvent) -> AnalysisCompleteEvent:
            return AnalysisCompleteEvent(
                findings=message.result, confidence=0.9, triggered_by_id=message.id, run_id=message.run_id
            )

    multi = MultiOutputNode(name="multi")
    single = ProcessedOnlyNode(name="single")

    # This should work - ProcessedEvent is in the union output and matches input
    flow = create_flow("union_test", multi).route(multi, ProcessedEvent, single)

    # Ensure it works (no exception)
    assert flow is not None

    # Now test incompatible types
    class SecurityNode(Node[SecurityAlertEvent, AnalysisCompleteEvent]):
        @override
        async def process(self, message: SecurityAlertEvent) -> AnalysisCompleteEvent:
            return AnalysisCompleteEvent(
                findings="security", confidence=0.9, triggered_by_id=message.id, run_id=message.run_id
            )

    security_node = SecurityNode(name="security")

    # This should fail - SecurityAlertEvent is not in the union
    with pytest.raises(TypeError, match="cannot output SecurityAlertEvent"):
        create_flow("bad_union", multi).route(multi, SecurityAlertEvent, security_node)


def test_flow_reachability_validation() -> None:
    """Test that flow builder validates node reachability."""
    start = StartNode(name="start")
    unreachable = ValidateNode(name="unreachable")

    builder = create_flow("test", start)

    # Try to route from unreachable node
    with pytest.raises(ValueError, match="not reachable from start") as exc_info:
        builder.route(unreachable, ValidationPassedEvent, start)

    assert "not reachable from start" in str(exc_info.value)


def test_flow_duplicate_route_error() -> None:
    """Test that duplicate routes are rejected."""
    start = StartNode(name="start")
    node1 = TransformNode(name="transform1")
    node2 = TransformNode(name="transform2")

    builder = create_flow("test", start)
    builder = builder.route(start, ProcessedEvent, node1)

    # Try to add duplicate route for same message type from same node
    with pytest.raises(ValueError, match="Route already defined") as exc_info:
        builder.route(start, ProcessedEvent, node2)

    assert "Route already defined" in str(exc_info.value)


def test_flow_name_property() -> None:
    """Test flow name is preserved."""
    start = StartNode(name="start")
    test_flow = create_flow("my_flow", start).end_flow(ProcessedEvent)

    assert test_flow.name == "my_flow"


def test_flow_immutability() -> None:
    """Test that flows are immutable."""
    start = StartNode(name="start")
    test_flow = create_flow("immutable", start).end_flow(ProcessedEvent)

    # Should not be able to modify flow
    with pytest.raises(ValidationError, match="frozen"):
        test_flow.name = "modified"


def test_flow_builder_chaining() -> None:
    """Test flow builder method chaining."""
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = ValidateNode(name="validate")

    # Each route returns a new builder
    builder1 = create_flow("test", start)
    builder2 = builder1.route(start, ProcessedEvent, transform)
    builder3 = builder2.route(transform, ValidateCommand, validate)

    # Builders are different instances
    assert builder1 is not builder2
    assert builder2 is not builder3

    # But can chain fluently
    flow = (
        create_flow("fluent", start)
        .route(start, ProcessedEvent, transform)
        .route(transform, ValidateCommand, validate)
        .end_flow(ValidationPassedEvent)
    )

    assert flow.name == "fluent"


async def test_single_terminal_type() -> None:
    """Test that flow terminates on specified terminal type only."""

    # Node with multiple output types - use message content to determine output
    class MultiOutputNode(Node[ProcessCommand, ProcessedEvent | ErrorEvent]):
        @override
        async def process(self, message: ProcessCommand) -> ProcessedEvent | ErrorEvent:
            if message.data == "error":
                return ErrorEvent(
                    error_message="Terminal error",
                    triggered_by_id=message.id,
                    run_id=message.run_id,
                )
            return ProcessedEvent(
                result="terminal success",
                processing_time_ms=10.0,
                triggered_by_id=message.id,
                run_id=message.run_id,
            )

    # Create flow with ProcessedEvent as terminal
    multi = MultiOutputNode(name="multi")
    test_flow = create_flow("single_terminal", multi).end_flow(ProcessedEvent)

    run_id = create_run_id()

    # Test ProcessedEvent path - should terminate
    result = await test_flow.process(ProcessCommand(data="success", triggered_by_id=None, run_id=run_id))
    assert isinstance(result, ProcessedEvent)
    assert result.result == "terminal success"

    # For ErrorEvent terminal flow
    error_flow = create_flow("error_terminal", multi).end_flow(ErrorEvent)

    # Test ErrorEvent path - should terminate
    result = await error_flow.process(ProcessCommand(data="error", triggered_by_id=None, run_id=run_id))
    assert isinstance(result, ErrorEvent)
    assert result.error_message == "Terminal error"


def test_terminal_type_validation() -> None:
    """Test that terminal type cannot be routed between nodes."""
    start = StartNode(name="start")

    # Create an error handler that outputs ErrorEvent
    class ErrorHandler(Node[ErrorEvent, ErrorEvent]):
        @override
        async def process(self, message: ErrorEvent) -> ErrorEvent:
            return message

    error_handler = ErrorHandler(name="error_handler")

    # This should work - ProcessedEvent not routed, can be terminal
    builder = create_flow("test", start)
    flow = builder.end_flow(ProcessedEvent)
    assert flow is not None

    # But this should fail - trying to use ErrorEvent as terminal after routing it
    builder2 = (
        create_flow("test2", start).route(start, ErrorEvent, error_handler)  # ErrorEvent is routed here
    )

    with pytest.raises(ValueError, match=r"Cannot use.*as terminal type.*already routed"):
        builder2.end_flow(ErrorEvent)  # Can't use as terminal after routing


async def test_terminal_type_immediately_ends_flow() -> None:
    """Test that ANY node producing terminal type ends the flow immediately."""
    start = StartNode(name="start")

    # Flow where ProcessedEvent is terminal (no routes for it)
    flow = create_flow("early_termination", start).end_flow(ProcessedEvent)

    # ProcessedEvent terminates immediately when produced
    run_id = create_run_id()
    result = await flow.process(ProcessCommand(data="test", triggered_by_id=None, run_id=run_id))

    # The flow should terminate at start node's ProcessedEvent output
    assert isinstance(result, ProcessedEvent)
    assert result.result == "started: test"


async def test_terminal_type_mismatch_error() -> None:
    """Test error when node output doesn't match terminal type and no route exists."""

    # Node that transforms but outputs wrong type for terminal
    class TransformToWrongType(Node[ProcessCommand, ValidateCommand]):
        @override
        async def process(self, message: ProcessCommand) -> ValidateCommand:
            return ValidateCommand(
                content=message.data,
                strict=True,
                triggered_by_id=message.id,
                run_id=message.run_id,
            )

    wrong_transform = TransformToWrongType(name="wrong_transform")

    # Flow expects ProcessedEvent as terminal but node outputs ValidateCommand
    flow = create_flow("mismatch", wrong_transform).end_flow(ProcessedEvent)

    run_id = create_run_id()
    input_msg = ProcessCommand(data="test", triggered_by_id=None, run_id=run_id)

    # Should raise error about missing route (ValidateCommand has no route)
    with pytest.raises(ValueError, match="No route defined"):
        await flow.process(input_msg)


def test_single_responsibility_principle() -> None:
    """Test that flows enforce single responsibility through terminal type.

    Each flow has ONE goal defined by its terminal type.
    This encourages clear thinking: What is the purpose of this flow?
    """
    start = StartNode(name="start")
    transform = TransformNode(name="transform")
    validate = ValidateNode(name="validate")

    # Flow 1: Goal is to produce ValidateCommand (preparation flow)
    preparation_flow = (
        create_flow("prepare_validation", start)
        .route(start, ProcessedEvent, transform)
        .end_flow(ValidateCommand)  # Clear goal: prepare for validation
    )

    # Flow 2: Goal is to produce ValidationPassedEvent (validation success flow)
    validation_success_flow = (
        create_flow("ensure_valid", validate).end_flow(ValidationPassedEvent)  # Clear goal: ensure validation passes
    )

    # Flow 3: Goal is to handle errors (error recovery flow)
    error_flow = (
        create_flow("handle_error", start).end_flow(ErrorEvent)  # Clear goal: handle error cases
    )

    # Each flow has a single, clear purpose
    assert preparation_flow.name == "prepare_validation"
    assert validation_success_flow.name == "ensure_valid"
    assert error_flow.name == "handle_error"
