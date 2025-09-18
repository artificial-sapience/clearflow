"""Messages for the type safety analysis flow.

This module defines the command and event types used in the type safety
analysis workflow, following ClearFlow's message-driven architecture.
"""

from collections.abc import Mapping, Sequence

from pydantic import Field

from clearflow import Command, Event
from linters.type_safety_analyzer.type_models import TypeSafetyFix, TypeSafetyIssue


class StartAnalysisCommand(Command):
    """Command to start type safety analysis on code.

    Initiates the analysis flow with file content and context about
    available types and patterns in the codebase.
    """

    file_path: str = Field(description="Path to the file being analyzed")
    code_content: str = Field(description="The Python code to analyze")
    project_context: str = Field(
        default="", description="Additional context about the project's conventions and patterns"
    )


class AnalysisCompleteEvent(Event):
    """Terminal event indicating analysis is complete.

    Final result of the type safety analysis with all findings and recommendations.
    Uses the same models as DSPy output for consistency.
    """

    file_path: str = Field(description="Path to the analyzed file")
    reasoning: str = Field(description="Step-by-step analysis reasoning from the LLM")
    issues: Sequence[TypeSafetyIssue] = Field(default=[], description="Sequence of identified issues")
    fixes: Sequence[TypeSafetyFix] = Field(default=[], description="Sequence of generated fixes")


class AnalysisErrorEvent(Event):
    """Terminal event when analysis fails.

    Indicates the analysis could not be completed due to an error.
    """

    file_path: str = Field(description="Path to the file that failed analysis")
    error_stage: str = Field(description="Stage where the error occurred")
    error_message: str = Field(description="Description of the error")
    partial_results: Mapping[str, str | int] | None = Field(
        default=None, description="Any partial results before failure"
    )
