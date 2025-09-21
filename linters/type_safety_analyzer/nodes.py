"""Type safety analyzer node.

Direct file analysis using DSPy for comprehensive type safety checking.
The LLM analyzes complete files naturally for optimal pattern recognition.
"""

from typing import cast, override

import dspy

from clearflow import Node
from linters.type_safety_analyzer.messages import AnalysisCompleteEvent, StartAnalysisCommand
from linters.type_safety_analyzer.type_models import TypeSafetyAnalysisResult


class TypeSafetyAnalysisSignature(dspy.Signature):
    """Analyze Python code for type safety issues and generate fixes.

    Focus on identifying magic strings that should be Literal types.
    Look for hardcoded strings used in conditionals, assignments, or comparisons
    that would benefit from being defined as Literal types for better type safety.
    """

    file_path: str = dspy.InputField(desc="Path to the Python file being analyzed")
    code_content: str = dspy.InputField(desc="Full Python source code to analyze for type safety issues")

    analysis_result: TypeSafetyAnalysisResult = dspy.OutputField(
        desc=(
            "Complete analysis result with reasoning, issues, and fixes. "
            "Focus on magic strings that should be Literal types, hardcoded values in enums, "
            "state machines, configuration values, and validation patterns."
        )
    )


class SimplifiedAnalyzerNode(Node[StartAnalysisCommand, AnalysisCompleteEvent]):
    """Type safety analyzer that processes entire files using DSPy.

    Analyzes complete files for type safety patterns using AI reasoning
    for comprehensive and context-aware detection.
    """

    name: str = "simplified_analyzer"

    @override
    async def process(self, message: StartAnalysisCommand) -> AnalysisCompleteEvent:
        """Analyze entire file for type safety issues in one pass.

        Args:
            message: Command with file path and content to analyze.

        Returns:
            AnalysisCompleteEvent with all issues and fixes.

        """
        # Create analyzer for this call
        analyzer = dspy.Predict(TypeSafetyAnalysisSignature)

        # Single LLM call to analyze everything
        result = cast(
            "TypeSafetyAnalysisSignature", analyzer(file_path=message.file_path, code_content=message.code_content)
        )

        # Use DSPy output directly - no transformation needed!
        return AnalysisCompleteEvent(
            file_path=message.file_path,
            reasoning=result.analysis_result.reasoning,
            issues=result.analysis_result.issues,
            fixes=result.analysis_result.fixes,
            run_id=message.run_id,
            triggered_by_id=message.id,
        )
