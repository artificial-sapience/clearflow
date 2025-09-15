"""Console handler for pretty-printing message events during flow execution.

This module provides a callback handler that displays flow progress to the console
with colored output and structured formatting for better visibility.
"""

import sys
from datetime import datetime
from types import TracebackType
from typing import override

from clearflow import Command, Event, Message, Observer


class ConsoleHandler(Observer):
    """Observer that pretty-prints flow execution to console.

    Provides colored, structured output showing:
    - Flow lifecycle (start/end)
    - Node execution progress
    - Message types and content
    - Error states
    """

    def __init__(self) -> None:
        """Initialize console handler."""

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Handle flow start event.

        Args:
            flow_name: Name of the flow starting
            message: Initial message being processed

        """
        ConsoleHandler.print_header(f"🚀 Flow Started: {flow_name}")
        ConsoleHandler.print_message("Input", message)
        ConsoleHandler.print_timestamp(message.timestamp)

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Handle flow end event.

        Args:
            flow_name: Name of the flow ending
            message: Final message from flow
            error: Exception if flow failed

        """
        if error:
            ConsoleHandler.print_header(f"❌ Flow Failed: {flow_name}", color="red")
            ConsoleHandler.print_error(error)
        else:
            ConsoleHandler.print_header(f"✅ Flow Completed: {flow_name}", color="green")
            ConsoleHandler.print_message("Output", message)
            ConsoleHandler.print_timestamp(message.timestamp)

        sys.stderr.write("\n")

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Handle node start event.

        Args:
            node_name: Name of node starting execution
            message: Message being passed to node

        """
        ConsoleHandler.print_node_status(f"⚙️  {node_name}", "processing", color="yellow")
        ConsoleHandler.print_message("Input", message, indent=2)

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Handle node end event.

        Args:
            node_name: Name of node that executed
            message: Message returned by node
            error: Exception if node failed

        """
        if error:
            ConsoleHandler.print_node_status(f"❌ {node_name}", "failed", color="red")
            ConsoleHandler.print_error(error, indent=2)
        else:
            ConsoleHandler.print_node_status(f"✓  {node_name}", "completed", color="green")
            ConsoleHandler.print_message("Output", message, indent=2)

    @staticmethod
    def print_header(text: str, color: str = "blue") -> None:
        """Print a section header."""
        border = "=" * 60
        colored_text = ConsoleHandler.colorize(text, color)
        sys.stderr.write(f"\n{border}\n{colored_text}\n{border}\n")

    @staticmethod
    def print_node_status(node: str, status: str, color: str = "white") -> None:
        """Print node execution status."""
        colored_status = ConsoleHandler.colorize(status, color)
        sys.stderr.write(f"  {node}: {colored_status}\n")

    @staticmethod
    def get_message_style(message: Message) -> tuple[str, str]:
        """Get color and symbol for message type.

        Args:
            message: Message to style

        Returns:
            Tuple of (color_name, symbol)

        """
        if isinstance(message, Command):
            return "cyan", "→"
        if isinstance(message, Event):
            return "magenta", "←"
        return "white", "•"

    @staticmethod
    def print_message(label: str, message: Message, indent: int = 1) -> None:
        """Print message details."""
        spaces = "  " * indent
        msg_type = message.__class__.__name__

        type_color, type_symbol = ConsoleHandler.get_message_style(message)
        colored_type = ConsoleHandler.colorize(f"{type_symbol} {msg_type}", type_color)
        sys.stderr.write(f"{spaces}{label}: {colored_type}\n")

        # Show key fields (excluding internal metadata)
        for key, value in message.__dict__.items():
            if not key.startswith("_") and key not in {"id", "timestamp", "triggered_by_id", "run_id"}:
                sys.stderr.write(f"{spaces}  {key}: {value}\n")

    @staticmethod
    def print_error(error: Exception, indent: int = 1) -> None:
        """Print error details."""
        spaces = "  " * indent
        error_text = ConsoleHandler.colorize(f"Error: {error.__class__.__name__}: {error}", "red")
        sys.stderr.write(f"{spaces}{error_text}\n")

    @staticmethod
    def print_timestamp(timestamp: datetime) -> None:
        """Print timestamp information."""
        timestamp_text = ConsoleHandler.colorize(f"⏰ {timestamp.strftime('%H:%M:%S.%f')[:-3]} UTC", "dim")
        sys.stderr.write(f"  {timestamp_text}\n")

    @staticmethod
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
        """Start showing loading indicator.

        Returns:
            Self for context manager protocol

        """
        self.running = True
        sys.stderr.write(f"\r{self.message}... ")
        sys.stderr.flush()
        return self

    async def __aexit__(
        self, _exc_type: type[BaseException] | None, exc_val: BaseException | None, _exc_tb: TracebackType | None
    ) -> None:
        """Stop showing loading indicator."""
        self.running = False
        if exc_val:
            sys.stderr.write("❌\n")
        else:
            sys.stderr.write("✓\n")
        sys.stderr.flush()
