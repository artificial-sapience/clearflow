"""Shared type definitions for the type safety analyzer.

This module contains the core Pydantic models used throughout the analyzer,
both for DSPy signatures and message formats.
"""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from clearflow import StrictBaseModel


class TypeSafetyIssue(StrictBaseModel):
    """A type safety issue found in the code."""

    line: int = Field(description="Line number where the issue occurs")
    severity: Literal["warning", "suggestion"] = Field(description="Severity level of the issue")
    description: str = Field(description="Clear description of the type safety issue")
    code_snippet: str = Field(description="The specific code that has the issue")


class TypeSafetyFix(StrictBaseModel):
    """A proposed fix for a type safety issue."""

    line: int = Field(description="Line number where the fix should be applied")
    old_code: str = Field(description="The current code that needs to be replaced")
    new_code: str = Field(description="The new code that fixes the issue")
    description: str = Field(description="Explanation of what the fix does and why it's needed")


class TypeSafetyAnalysisResult(StrictBaseModel):
    """Complete result of type safety analysis."""

    reasoning: str = Field(description="Step-by-step analysis of type safety issues found in the code")
    issues: Sequence[TypeSafetyIssue] = Field(
        description="All type safety issues found in the code, focusing on magic strings that should be Literal types"
    )
    fixes: Sequence[TypeSafetyFix] = Field(
        description="Proposed fixes for the identified issues. Empty sequence if no fixes needed."
    )
