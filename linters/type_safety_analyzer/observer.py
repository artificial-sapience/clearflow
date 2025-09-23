"""Observer for type safety analyzer to show progress and results.

This observer provides real-time feedback during analysis, showing:
- File parsing progress
- LLM analysis status
- Issues found in real-time
- Fix generation progress
"""

import sys
from typing import override

from clearflow import Message, Observer
from linters.type_safety_analyzer.messages import AnalysisCompleteEvent, StartAnalysisCommand
from linters.type_safety_analyzer.type_models import TypeSafetyFix, TypeSafetyIssue


# Utility functions for colored terminal output
def colorize(text: str, color: str) -> str:
    """Add ANSI color codes to text.

    Args:
        text: Text to colorize
        color: Color name

    Returns:
        Text with ANSI color codes

    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "dim": "\033[90m",
    }
    reset = "\033[0m"

    if color in colors:
        return f"{colors[color]}{text}{reset}"
    return text


def print_header(text: str, color: str) -> None:
    """Print a section header."""
    border = "=" * 70
    colored_text = colorize(text, color)
    sys.stderr.write(f"\n{border}\n{colored_text}\n{border}\n")


def print_status(text: str, color: str) -> None:
    """Print a status message."""
    sys.stderr.write(f"\n{colorize(text, color)}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    sys.stderr.write(f"{colorize(text, 'green')}\n")


def print_warning(text: str) -> None:
    """Print a warning message."""
    sys.stderr.write(f"{colorize(text, 'yellow')}\n")


def print_error(text: str) -> None:
    """Print an error message."""
    sys.stderr.write(f"{colorize(text, 'red')}\n")


def print_info(text: str, *, dim: bool = False) -> None:
    """Print an info message.

    Args:
        text: Text to print
        dim: Whether to print in dim color (keyword-only)

    """
    color = "dim" if dim else "white"
    sys.stderr.write(f"{colorize(text, color)}\n")


def print_detail(text: str) -> None:
    """Print a detail line (indented)."""
    sys.stderr.write(f"{colorize(text, 'dim')}\n")


def print_issue(issue: TypeSafetyIssue) -> None:
    """Print issue details."""
    severity_color = {"error": "red", "warning": "yellow", "suggestion": "cyan"}.get(issue.severity, "white")
    sys.stderr.write(f"\n  {colorize(f'Line {issue.line}:', severity_color)} {issue.description}\n")
    sys.stderr.write(f"    {colorize(f'Code: {issue.code_snippet}', 'dim')}\n")


def print_fix(fix: TypeSafetyFix) -> None:
    """Print fix details."""
    sys.stderr.write(f"\n  {colorize(f'Line {fix.line}:', 'cyan')}\n")
    sys.stderr.write(f"    {colorize(f'- {fix.old_code}', 'red')}\n")
    sys.stderr.write(f"    {colorize(f'+ {fix.new_code}', 'green')}\n")


class TypeSafetyAnalyzerObserver(Observer):
    """Observer that shows type safety analysis progress to the user.

    Provides colored, structured output showing:
    - Parsing progress with string literal counts
    - LLM analysis status (with waiting indicators)
    - Issues found with severity
    - Fix generation progress
    - Final summary with actionable insights
    """

    # Constants for display limits
    MAX_LITERAL_SAMPLES = 3
    MAX_ISSUE_SAMPLES = 3
    MAX_FIX_SAMPLES = 2

    def __init__(self) -> None:
        """Initialize the analyzer observer."""
        self.file_path: str | None = None
        self.issue_count: int = 0
        self.spinner_index: int = 0
        self.spinner_chars: tuple[str, ...] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Handle flow start - show initial analysis info.

        Args:
            flow_name: Name of the flow (TypeSafetyAnalysis)
            message: StartAnalysisCommand with file info

        """
        _ = flow_name  # Unused but required by Observer interface
        if isinstance(message, StartAnalysisCommand):
            self.file_path = message.file_path
            print_header("🔍 Type Safety Analysis", "blue")
            print_info(f"📁 File: {message.file_path}")
            print_info(f"📏 Code size: {len(message.code_content)} bytes")
            print_info("🤖 Using DSPy Predict for fast analysis")
            print_info("🎯 Analyzing complete file for type safety patterns")
            sys.stderr.write("\n")

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Handle node start - show what stage we're in.

        Args:
            node_name: Name of the node starting
            message: Input message to the node

        """
        if node_name == "code_parser":
            print_status("📝 Parsing Python code...", "yellow")
        elif node_name == "issue_detector":
            print_status("🤖 Analyzing for type safety issues...", "yellow")
            print_info("   (This may take 10-30 seconds depending on file size)", dim=True)
        elif node_name == "fix_generator":
            print_status("🔧 Generating fixes...", "yellow")
        elif node_name == "fix_applier":
            print_status("📝 Preparing fix report...", "yellow")

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Handle node end - show results from each stage.

        Args:
            node_name: Name of the node that finished
            message: Output message from the node
            error: Any error that occurred

        """
        if error:
            print_error(f"❌ {node_name} failed: {error}")
            return

        # Only handle AnalysisCompleteEvent in our simplified design
        if isinstance(message, AnalysisCompleteEvent):
            # Show immediate feedback about analysis results
            issues_count = len(message.issues)
            fixes_count = len(message.fixes)
            print_success(f"✓ Analysis complete: {issues_count} issues, {fixes_count} fixes found")

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Handle flow end - show final summary.

        Args:
            flow_name: Name of the flow
            message: Final message (AnalysisCompleteEvent)
            error: Any error that occurred

        """
        _ = flow_name  # Unused but required by Observer interface
        sys.stderr.write("\n")

        if error:
            print_header("❌ Analysis Failed", "red")
            print_error(str(error))
        elif isinstance(message, AnalysisCompleteEvent):
            issues_count = len(message.issues)
            fixes_count = len(message.fixes)

            if issues_count == 0:
                print_header("✅ Analysis Complete - No Issues!", "green")
                print_info("🎉 Your code looks great! No type safety issues detected.")
            else:
                print_header("📋 Analysis Results", "yellow")

                # Show LLM reasoning
                if message.reasoning:
                    print_info("🧠 Analysis Reasoning:")
                    print_detail(message.reasoning)
                    sys.stderr.write("\n")

                # Show all issues in detail
                print_info(f"⚠️  Found {issues_count} type safety issues:")
                for i, issue in enumerate(message.issues, 1):
                    sys.stderr.write(f"\n  {i}. ")
                    print_issue(issue)

                # Show all fixes in detail
                if fixes_count > 0:
                    print_info(f"\n🔧 Generated {fixes_count} fixes:")
                    for i, fix in enumerate(message.fixes, 1):
                        sys.stderr.write(f"\n  {i}. ")
                        print_fix(fix)
                        sys.stderr.write(f"    {colorize(fix.description, 'cyan')}\n")
                else:
                    print_warning("\n⚠️  No automatic fixes available for these issues")

            # Final summary
            print_header("📊 Summary", "blue")
            print_info(f"📁 File: {message.file_path}")
            print_info(f"🔍 Issues: {issues_count}")
            print_info(f"🔧 Fixes: {fixes_count}")

            if issues_count > 0:
                success_rate = (fixes_count / issues_count) * 100 if issues_count > 0 else 0
                print_info(f"✨ Fix coverage: {success_rate:.1f}%")

        sys.stderr.write("\n")
