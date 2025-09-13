"""Shared test fixtures and types for message-driven architecture tests.

This module provides immutable message types used across message test modules,
demonstrating mission-critical AI orchestration patterns with message-driven flow.

"""

import uuid
from dataclasses import dataclass

from clearflow import Command, Event


@dataclass(frozen=True, kw_only=True)
class ProcessCommand(Command):
    """Command to initiate processing."""

    data: str
    priority: int = 1


@dataclass(frozen=True, kw_only=True)
class ValidateCommand(Command):
    """Command to validate input."""

    content: str
    strict: bool = True


@dataclass(frozen=True, kw_only=True)
class AnalyzeCommand(Command):
    """Command to analyze data."""

    input_data: str
    analysis_type: str = "basic"


@dataclass(frozen=True, kw_only=True)
class ProcessedEvent(Event):
    """Event indicating processing completed."""

    result: str
    processing_time_ms: float


@dataclass(frozen=True, kw_only=True)
class ValidationPassedEvent(Event):
    """Event indicating validation succeeded."""

    validated_content: str
    validation_score: float = 1.0


@dataclass(frozen=True, kw_only=True)
class ValidationFailedEvent(Event):
    """Event indicating validation failed."""

    reason: str
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class AnalysisCompleteEvent(Event):
    """Event indicating analysis completed."""

    findings: str
    confidence: float = 0.95


@dataclass(frozen=True, kw_only=True)
class ErrorEvent(Event):
    """Event indicating an error occurred."""

    error_message: str
    error_type: str = "general"


@dataclass(frozen=True, kw_only=True)
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


def create_flow_id() -> uuid.UUID:
    """Create a new flow ID for testing.

    Returns:
        A new UUID for flow identification.

    """
    return uuid.uuid4()
