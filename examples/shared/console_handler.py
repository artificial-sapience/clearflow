"""Console handler for pretty-printing message events during flow execution.

This module provides a callback handler that displays flow progress to the console
with colored output and structured formatting for better visibility.
"""

import sys
from datetime import datetime, timezone
from types import TracebackType
from typing import override

from clearflow import CallbackHandler, Command, Event, Message


class ConsoleHandler(CallbackHandler):
    """Callback handler that pretty-prints flow execution to console.

    Provides colored, structured output showing:
    - Flow lifecycle (start/end)
    - Node execution progress
    - Message types and content
    - Timing information
    - Error states
    """

    def __init__(self, verbose: bool = False) -> None:
        """Initialize console handler.

        Args:
            verbose: If True, show detailed message content

        """
        self.verbose = verbose
        # Internal mutable state for tracking timing
        self._start_times: dict[str, datetime] = {}

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Handle flow start event.

        Args:
            flow_name: Name of the flow starting
            message: Initial message being processed

        """
        self._start_times[flow_name] = datetime.now(timezone.utc)
        self._print_header(f"🚀 Flow Started: {flow_name}")
        self._print_message("Input", message)

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Handle flow end event.

        Args:
            flow_name: Name of the flow ending
            message: Final message from flow
            error: Exception if flow failed

        """
        elapsed = self._get_elapsed(flow_name)

        if error:
            self._print_header(f"❌ Flow Failed: {flow_name}", color="red")
            self._print_error(error)
        else:
            self._print_header(f"✅ Flow Completed: {flow_name}", color="green")
            self._print_message("Output", message)

        self._print_timing(elapsed)
        sys.stderr.write("\n")

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Handle node start event.

        Args:
            node_name: Name of node starting execution
            message: Message being passed to node

        """
        self._start_times[node_name] = datetime.now(timezone.utc)
        self._print_node_status(f"⚙️  {node_name}", "processing", color="yellow")
        if self.verbose:
            self._print_message("Input", message, indent=2)

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Handle node end event.

        Args:
            node_name: Name of node that executed
            message: Message returned by node
            error: Exception if node failed

        """
        elapsed = self._get_elapsed(node_name)

        if error:
            self._print_node_status(f"❌ {node_name}", f"failed ({elapsed:.2f}s)", color="red")
            self._print_error(error, indent=2)
        else:
            self._print_node_status(f"✓  {node_name}", f"completed ({elapsed:.2f}s)", color="green")
            if self.verbose:
                self._print_message("Output", message, indent=2)

    def _print_header(self, text: str, color: str = "blue") -> None:
        """Print a section header."""
        border = "=" * 60
        colored_text = self._colorize(text, color)
        sys.stderr.write(f"\n{border}\n{colored_text}\n{border}\n")

    def _print_node_status(self, node: str, status: str, color: str = "white") -> None:
        """Print node execution status."""
        colored_status = self._colorize(status, color)
        sys.stderr.write(f"  {node}: {colored_status}\n")

    def _print_message(self, label: str, message: Message, indent: int = 1) -> None:
        """Print message details."""
        spaces = "  " * indent
        msg_type = message.__class__.__name__

        # Determine message category
        if isinstance(message, Command):
            type_color = "cyan"
            type_symbol = "→"
        elif isinstance(message, Event):
            type_color = "magenta"
            type_symbol = "←"
        else:
            type_color = "white"
            type_symbol = "•"

        colored_type = self._colorize(f"{type_symbol} {msg_type}", type_color)
        sys.stderr.write(f"{spaces}{label}: {colored_type}\n")

        if self.verbose:
            # Show key fields (excluding internal metadata)
            for key, value in message.__dict__.items():
                if not key.startswith("_") and key not in ("id", "timestamp", "triggered_by_id", "run_id"):
                    sys.stderr.write(f"{spaces}  {key}: {value}\n")

    def _print_error(self, error: Exception, indent: int = 1) -> None:
        """Print error details."""
        spaces = "  " * indent
        error_text = self._colorize(f"Error: {error.__class__.__name__}: {error}", "red")
        sys.stderr.write(f"{spaces}{error_text}\n")

    def _print_timing(self, elapsed: float) -> None:
        """Print timing information."""
        timing_text = self._colorize(f"⏱️  Time: {elapsed:.3f}s", "dim")
        sys.stderr.write(f"  {timing_text}\n")

    def _get_elapsed(self, key: str) -> float:
        """Get elapsed time for a flow or node."""
        if key in self._start_times:
            start = self._start_times.pop(key)
            return (datetime.now(timezone.utc) - start).total_seconds()
        return 0.0

    def _colorize(self, text: str, color: str) -> str:
        """Add ANSI color codes to text."""
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


class LoadingIndicator:
    """Context manager for showing loading indicators during async operations."""

    def __init__(self, message: str = "Processing") -> None:
        """Initialize loading indicator.

        Args:
            message: Message to display while loading

        """
        self.message = message
        self.running = False

    async def __aenter__(self) -> "LoadingIndicator":
        """Start showing loading indicator."""
        self.running = True
        sys.stderr.write(f"\r{self.message}... ")
        sys.stderr.flush()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Stop showing loading indicator."""
        self.running = False
        if exc_val:
            sys.stderr.write("❌\n")
        else:
            sys.stderr.write("✓\n")
        sys.stderr.flush()