"""Type safety analysis flow.

Direct file analysis using DSPy for comprehensive type safety checking.
"""

from clearflow import Node, create_flow
from linters.type_safety_analyzer.messages import AnalysisCompleteEvent, StartAnalysisCommand
from linters.type_safety_analyzer.nodes import SimplifiedAnalyzerNode
from linters.type_safety_analyzer.observer import TypeSafetyAnalyzerObserver


def create_simple_analyzer_flow() -> Node[StartAnalysisCommand, AnalysisCompleteEvent]:
    """Create type safety analyzer flow with rich observer output.

    Returns:
        Configured flow with observer for detailed progress and results.

    """
    analyzer = SimplifiedAnalyzerNode()

    # Build flow with observer always attached for rich output
    return (
        create_flow("TypeSafetyAnalyzer", analyzer)
        .observe(TypeSafetyAnalyzerObserver())
        .end_flow(AnalysisCompleteEvent)
    )
