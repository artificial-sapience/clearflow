"""Test message Node abstraction features.

This module tests the Node class for message-driven architecture including
process method and message transformation patterns.

"""

from typing import override

import pytest
from pydantic import ValidationError

from clearflow import Node
from tests.conftest import (
    AnalysisCompleteEvent,
    AnalyzeCommand,
    ErrorEvent,
    ProcessCommand,
    ProcessedEvent,
    ValidateCommand,
    ValidationFailedEvent,
    ValidationPassedEvent,
    create_run_id,
)


# Test node implementations
class ProcessorNode(Node[ProcessCommand, ProcessedEvent]):
    """Node that processes commands into events."""

    @override
    async def process(self, message: ProcessCommand) -> ProcessedEvent:
        # Simple processing logic
        result = f"processed: {message.data}"
        return ProcessedEvent(
            result=result,
            processing_time_ms=100.0,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class ValidatorNode(Node[ValidateCommand, ValidationPassedEvent | ValidationFailedEvent]):
    """Node that validates commands into success or failure events."""

    name: str = "validator"

    @override
    async def process(self, message: ValidateCommand) -> ValidationPassedEvent | ValidationFailedEvent:
        if message.strict and len(message.content) < 5:
            return ValidationFailedEvent(
                reason="Content too short",
                errors=("Length < 5",),
                triggered_by_id=message.id,
                run_id=message.run_id,
            )

        return ValidationPassedEvent(
            validated_content=message.content.upper(),
            validation_score=0.95,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class AnalyzerNode(Node[AnalyzeCommand, AnalysisCompleteEvent | ErrorEvent]):
    """Node that analyzes commands, potentially failing with errors."""

    name: str = "analyzer"
    fail_on_empty: bool = True

    @override
    async def process(self, message: AnalyzeCommand) -> AnalysisCompleteEvent | ErrorEvent:
        if self.fail_on_empty and not message.input_data:
            return ErrorEvent(
                error_message="Empty input data",
                error_type="validation",
                triggered_by_id=message.id,
                run_id=message.run_id,
            )

        findings = f"Analysis of {message.input_data}: {message.analysis_type}"
        return AnalysisCompleteEvent(
            findings=findings,
            confidence=0.85,
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


class ChainNode(Node[ProcessedEvent, AnalyzeCommand]):
    """Node that chains event to command transformation."""

    name: str = "chainer"

    @override
    async def process(self, message: ProcessedEvent) -> AnalyzeCommand:
        return AnalyzeCommand(
            input_data=message.result,
            analysis_type="detailed",
            triggered_by_id=message.id,
            run_id=message.run_id,
        )


def _create_test_command(data: str = "test data") -> ProcessCommand:
    """Create a test command with default run_id.

    Returns:
        ProcessCommand with the specified data.

    """
    return ProcessCommand(data=data, triggered_by_id=None, run_id=create_run_id())


def _assert_processed_event_correct(output: ProcessedEvent, input_msg: ProcessCommand, expected_result: str) -> None:
    """Assert that processed event has expected properties."""
    assert isinstance(output, ProcessedEvent)
    assert output.result == expected_result
    _assert_event_metadata_correct(output, input_msg)


def _assert_event_metadata_correct(output: ProcessedEvent, input_msg: ProcessCommand) -> None:
    """Assert event metadata matches input message."""
    assert output.processing_time_ms == 100.0
    assert output.triggered_by_id == input_msg.id
    assert output.run_id == input_msg.run_id


async def test_node_basic_processing() -> None:
    """Test basic node message processing."""
    node = ProcessorNode(name="processor")
    input_msg = _create_test_command()
    output = await node.process(input_msg)
    _assert_processed_event_correct(output, input_msg, "processed: test data")


def test_node_immutability() -> None:
    """Test that nodes are immutable."""
    node = ProcessorNode(name="immutable_processor")

    # Should not be able to modify node
    with pytest.raises(ValidationError, match="frozen"):
        node.name = "modified"


async def test_node_union_return_types() -> None:
    """Test nodes that return union types."""
    node = ValidatorNode(name="validator")
    run_id = create_run_id()

    # Test validation success
    valid_cmd = ValidateCommand(
        content="valid content",
        strict=True,
        triggered_by_id=None,
        run_id=run_id,
    )
    result = await node.process(valid_cmd)
    assert isinstance(result, ValidationPassedEvent)
    assert result.validated_content == "VALID CONTENT"

    # Test validation failure
    invalid_cmd = ValidateCommand(
        content="bad",
        strict=True,
        triggered_by_id=None,
        run_id=run_id,
    )
    result = await node.process(invalid_cmd)
    assert isinstance(result, ValidationFailedEvent)
    assert result.reason == "Content too short"


async def _process_chain_step1(processor: ProcessorNode, cmd: ProcessCommand) -> ProcessedEvent:
    """Process first step in chain and validate result.

    Returns:
        ProcessedEvent from the processor.

    """
    event1 = await processor.process(cmd)
    assert isinstance(event1, ProcessedEvent)
    return event1


async def _process_chain_step2(chainer: ChainNode, event1: ProcessedEvent) -> AnalyzeCommand:
    """Process second step in chain and validate result.

    Returns:
        AnalyzeCommand from the chainer.

    """
    cmd2 = await chainer.process(event1)
    assert isinstance(cmd2, AnalyzeCommand)
    assert cmd2.input_data == event1.result
    return cmd2


async def _process_chain_step3(analyzer: AnalyzerNode, cmd2: AnalyzeCommand) -> AnalysisCompleteEvent:
    """Process final step in chain and validate result.

    Returns:
        AnalysisCompleteEvent from the analyzer.

    """
    event2 = await analyzer.process(cmd2)
    assert isinstance(event2, AnalysisCompleteEvent)
    assert "processed: important" in event2.findings
    return event2


async def test_node_message_chaining() -> None:
    """Test chaining messages through multiple nodes."""
    processor = ProcessorNode(name="processor")
    chainer = ChainNode(name="chainer")
    analyzer = AnalyzerNode(name="analyzer", fail_on_empty=False)

    cmd = _create_test_command("important")
    event1 = await _process_chain_step1(processor, cmd)
    cmd2 = await _process_chain_step2(chainer, event1)
    await _process_chain_step3(analyzer, cmd2)


async def test_node_error_handling() -> None:
    """Test node error event generation."""
    analyzer = AnalyzerNode(name="analyzer", fail_on_empty=True)
    run_id = create_run_id()

    # Empty input should trigger error
    cmd = AnalyzeCommand(
        input_data="",
        triggered_by_id=None,
        run_id=run_id,
    )

    result = await analyzer.process(cmd)
    assert isinstance(result, ErrorEvent)
    assert result.error_message == "Empty input data"
    assert result.error_type == "validation"


async def test_node_causality_preservation() -> None:
    """Test that nodes preserve message causality."""
    node = ProcessorNode(name="processor")
    run_id = create_run_id()

    cmd = ProcessCommand(
        data="test",
        triggered_by_id=None,
        run_id=run_id,
    )

    output = await node.process(cmd)

    # Output should be triggered by input
    assert output.triggered_by_id == cmd.id
    assert output.run_id == cmd.run_id


def test_node_name_property() -> None:
    """Test node name configuration."""
    # Default name
    node1 = ProcessorNode(name="processor")
    assert node1.name == "processor"

    # Custom name
    node2 = ProcessorNode(name="custom_processor")
    assert node2.name == "custom_processor"


async def test_node_with_configuration() -> None:
    """Test nodes with configuration parameters."""
    # Configurable analyzer
    strict_analyzer = AnalyzerNode(name="strict", fail_on_empty=True)
    lenient_analyzer = AnalyzerNode(name="lenient", fail_on_empty=False)
    run_id = create_run_id()

    empty_cmd = AnalyzeCommand(
        input_data="",
        triggered_by_id=None,
        run_id=run_id,
    )

    # Strict fails on empty
    strict_result = await strict_analyzer.process(empty_cmd)
    assert isinstance(strict_result, ErrorEvent)

    # Lenient processes empty
    lenient_result = await lenient_analyzer.process(empty_cmd)
    assert isinstance(lenient_result, AnalysisCompleteEvent)


async def test_node_type_safety() -> None:
    """Test that nodes maintain type safety."""
    processor = ProcessorNode(name="processor")
    validator = ValidatorNode(name="validator")
    run_id = create_run_id()

    # Processor expects ProcessCommand
    process_cmd = ProcessCommand(data="test", triggered_by_id=None, run_id=run_id)
    process_result = await processor.process(process_cmd)
    assert isinstance(process_result, ProcessedEvent)

    # Validator expects ValidateCommand (different type)
    validate_cmd = ValidateCommand(content="test", triggered_by_id=None, run_id=run_id)
    validate_result = await validator.process(validate_cmd)
    assert isinstance(validate_result, (ValidationPassedEvent, ValidationFailedEvent))


def test_node_name_validation() -> None:
    """Test that nodes validate their names during initialization."""
    # Empty name should raise ValidationError
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ProcessorNode(name="")

    # Whitespace-only name should raise ValidationError (gets stripped then validated)
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        ProcessorNode(name="   ")
