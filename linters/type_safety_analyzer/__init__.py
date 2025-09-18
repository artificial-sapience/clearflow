"""Type safety analyzer using ClearFlow and LLM intelligence.

This package implements a type safety analyzer that uses ClearFlow's
message-driven architecture combined with DSPy-powered LLM analysis
to detect and fix magic strings and type safety issues in Python code.
"""

from linters.type_safety_analyzer.flow import create_simple_analyzer_flow
from linters.type_safety_analyzer.messages import (
    AnalysisCompleteEvent,
    StartAnalysisCommand,
)

__all__ = [
    "AnalysisCompleteEvent",
    "StartAnalysisCommand",
    "create_simple_analyzer_flow",
]
