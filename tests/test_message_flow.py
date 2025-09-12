"""Test message flow routing and composition.

This module tests the message flow builder, routing logic, and flow composability
for mission-critical AI orchestration with type-safe message routing.

"""

from dataclasses import dataclass
from typing import override

import pytest

from clearflow.message_flow import message_flow
from clearflow.message_node import Node
from tests.conftest_message import (
    AnalysisCompleteEvent,
    AnalyzeCommand,
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
    async def process(
        self, message: ValidateCommand
    ) -> ValidationPassedEvent | ValidationFailedEvent:
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


class TestMessageFlow:
    """Test message flow construction and execution."""

    async def test_simple_flow(self) -> None:
        """Test a simple linear flow."""
        start = StartNode()

        flow = message_flow("simple", start).end(ProcessedEvent)

        # Execute flow
        flow_id = create_flow_id()
        input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

        result = await flow.process(input_msg)

        assert isinstance(result, ProcessedEvent)
        assert result.result == "started: test"

    async def test_flow_with_routing(self) -> None:
        """Test flow with multiple routes."""
        start = StartNode()
        transform = TransformNode()
        validate = ValidateNode()
        finalize = FinalizeNode()

        flow = (
            message_flow("pipeline", start)
            .from_node(start)
            .route(ProcessedEvent, transform)
            .from_node(transform)
            # Transform produces ValidateCommand, route it to validate
            .route(ValidateCommand, validate)
            .from_node(validate)
            # Validate produces ValidationPassedEvent, route it to finalize
            .route(ValidationPassedEvent, finalize)
            .from_node(finalize)
            # Finalize produces AnalysisCompleteEvent, end there
            .end(AnalysisCompleteEvent)
        )

        # Execute successful path
        flow_id = create_flow_id()
        input_msg = ProcessCommand(
            data="valid data", triggered_by_id=None, flow_id=flow_id
        )

        result = await flow.process(input_msg)

        assert isinstance(result, AnalysisCompleteEvent)
        assert "started: valid data" in result.findings

    async def test_flow_with_error_handling(self) -> None:
        """Test flow with error route."""
        start = StartNode(should_fail=True)
        transform = TransformNode()

        flow = (
            message_flow("error_handling", start)
            .from_node(start)
            .route(ProcessedEvent, transform)
            .end(ErrorEvent)  # Error also from start - branching
        )

        flow_id = create_flow_id()
        input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

        result = await flow.process(input_msg)

        assert isinstance(result, ErrorEvent)
        assert result.error_message == "Start failed"

    async def test_flow_with_branching(self) -> None:
        """Test flow with conditional branching."""
        start = StartNode()
        transform = TransformNode()
        validate = ValidateNode(min_length=10)  # Strict validation

        flow = (
            message_flow("branching", start)
            .from_node(start)
            .route(ProcessedEvent, transform)
            .from_node(transform)
            .route(ValidateCommand, validate)
            .from_node(validate)
            .end(ValidationFailedEvent)  # Only test failure path
        )

        flow_id = create_flow_id()

        # Test failure branch - make input that results in short content after "started: "
        short_input = ProcessCommand(data="", triggered_by_id=None, flow_id=flow_id)  # "started: " = 9 chars < 10
        result = await flow.process(short_input)
        assert isinstance(result, ValidationFailedEvent)

    async def test_flow_missing_route_error(self) -> None:
        """Test that missing route raises error."""
        start = StartNode()
        transform = TransformNode()

        # Build flow missing route for ValidateCommand
        flow = message_flow("incomplete", start).route(ProcessedEvent, transform).end(
            ValidationFailedEvent  # Wrong termination
        )

        flow_id = create_flow_id()
        input_msg = ProcessCommand(data="test", triggered_by_id=None, flow_id=flow_id)

        # Should raise ValueError for missing route
        with pytest.raises(ValueError) as exc_info:
            await flow.process(input_msg)

        assert "No route defined for message type" in str(exc_info.value)
        assert "ValidateCommand" in str(exc_info.value)

    async def test_flow_composability(self) -> None:
        """Test that flows can be composed as nodes."""
        # Create inner flow
        validate = ValidateNode()
        finalize = FinalizeNode()

        inner_flow = (
            message_flow("inner", validate)
            .from_node(validate)
            .route(ValidationPassedEvent, finalize)
            .from_node(finalize)
            .end(AnalysisCompleteEvent)
        )

        # Create outer flow using inner flow as a node
        start = StartNode()
        transform = TransformNode()

        outer_flow = (
            message_flow("outer", start)
            .from_node(start)
            .route(ProcessedEvent, transform)
            .from_node(transform)
            .route(ValidateCommand, inner_flow)  # Inner flow as node!
            .from_node(inner_flow)
            .end(AnalysisCompleteEvent)
        )

        flow_id = create_flow_id()
        input_msg = ProcessCommand(
            data="composite test", triggered_by_id=None, flow_id=flow_id
        )

        result = await outer_flow.process(input_msg)

        assert isinstance(result, AnalysisCompleteEvent)
        assert "started: composite test" in result.findings

    async def test_flow_reachability_validation(self) -> None:
        """Test that flow builder validates node reachability."""
        start = StartNode()
        unreachable = ValidateNode()

        builder = message_flow("test", start)

        # Try to route from unreachable node
        with pytest.raises(ValueError) as exc_info:
            builder.from_node(unreachable).route(ValidationPassedEvent, start)

        assert "not reachable from start" in str(exc_info.value)

    async def test_flow_duplicate_route_error(self) -> None:
        """Test that duplicate routes are rejected."""
        start = StartNode()
        node1 = TransformNode(name="transform1")
        node2 = TransformNode(name="transform2")

        builder = message_flow("test", start).from_node(start)
        builder = builder.route(ProcessedEvent, node1)

        # Try to add duplicate route for same message type from same node
        with pytest.raises(ValueError) as exc_info:
            builder.route(ProcessedEvent, node2)

        assert "Route already defined" in str(exc_info.value)

    async def test_flow_name_property(self) -> None:
        """Test flow name is preserved."""
        start = StartNode()
        flow = message_flow("my_flow", start).end(ProcessedEvent)

        assert flow.name == "my_flow"

    async def test_flow_immutability(self) -> None:
        """Test that flows are immutable."""
        start = StartNode()
        flow = message_flow("immutable", start).end(ProcessedEvent)

        # Should not be able to modify flow
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            flow.name = "modified"  # type: ignore[misc]

        with pytest.raises(Exception):
            flow.start_node = StartNode(name="new")  # type: ignore[misc]

    async def test_flow_builder_chaining(self) -> None:
        """Test flow builder method chaining."""
        start = StartNode()
        transform = TransformNode()
        validate = ValidateNode()

        # Each route returns a new builder/context
        builder1 = message_flow("test", start)
        context1 = builder1.from_node(start)
        context2 = context1.route(ProcessedEvent, transform)
        context3 = context2.from_node(transform)
        context4 = context3.route(ValidateCommand, validate)

        # Builders/contexts are different instances
        assert builder1 is not context1
        assert context2 is not context3
        assert context3 is not context4

        # But can chain fluently
        flow = (
            message_flow("fluent", start)
            .from_node(start)
            .route(ProcessedEvent, transform)
            .from_node(transform)
            .route(ValidateCommand, validate)
            .from_node(validate)
            .end(ValidationPassedEvent)
        )

        assert flow.name == "fluent"
