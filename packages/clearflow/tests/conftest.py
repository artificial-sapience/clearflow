"""Shared test fixtures and types for message-driven architecture tests.

This module provides immutable message types used across message test modules,
demonstrating mission-critical AI orchestration patterns with message-driven flow.

"""

import uuid

from clearflow import Command, Event


class ProcessCommand(Command):
    """Command to initiate processing."""

    data: str
    priority: int = 1


class ValidateCommand(Command):
    """Command to validate input."""

    content: str
    strict: bool = True


class AnalyzeCommand(Command):
    """Command to analyze data."""

    input_data: str
    analysis_type: str = "basic"


class ProcessedEvent(Event):
    """Event indicating processing completed."""

    result: str
    processing_time_ms: float


class ValidationPassedEvent(Event):
    """Event indicating validation succeeded."""

    validated_content: str
    validation_score: float = 1.0


class ValidationFailedEvent(Event):
    """Event indicating validation failed."""

    reason: str
    errors: tuple[str, ...] = ()


class AnalysisCompleteEvent(Event):
    """Event indicating analysis completed."""

    findings: str
    confidence: float = 0.95


class ErrorEvent(Event):
    """Event indicating an error occurred."""

    error_message: str
    error_type: str = "general"


class SecurityAlertEvent(Event):
    """Event indicating a security issue detected."""

    threat_level: str  # "low", "medium", "high", "critical"
    description: str


# Test utilities for creating valid messages with required fields
def create_test_command(
    *,
    triggered_by_id: uuid.UUID | None = None,
    run_id: uuid.UUID | None = None,
) -> ProcessCommand:
    """Create a test command with valid fields.

    Returns:
        A ProcessCommand with test data.

    """
    return ProcessCommand(
        data="test data",
        triggered_by_id=triggered_by_id,
        run_id=run_id or uuid.uuid4(),
    )


def create_test_event(
    *,
    triggered_by_id: uuid.UUID | None = None,
    run_id: uuid.UUID | None = None,
) -> ProcessedEvent:
    """Create a test event with valid fields.

    Returns:
        A ProcessedEvent with test data.

    """
    if triggered_by_id is None:
        triggered_by_id = uuid.uuid4()

    return ProcessedEvent(
        result="processed",
        processing_time_ms=123.45,
        triggered_by_id=triggered_by_id,
        run_id=run_id or uuid.uuid4(),
    )


def create_run_id() -> uuid.UUID:
    """Create a new flow ID for testing.

    Returns:
        A new UUID for flow identification.

    """
    return uuid.uuid4()
