"""Observer pattern for monitoring message flow execution.

This module provides the Observer base class for ClearFlow, enabling
integration with observability platforms, debugging tools, and user
interfaces without affecting flow execution.
"""

from clearflow.message import Message

__all__ = ["Observer"]


class Observer:
    """Base class for observing messages during flow execution.

    Create custom observers by subclassing and overriding only the methods
    you need. All methods have no-op defaults, so you can monitor just the
    lifecycle points you care about. Any errors raised will be caught and
    logged without affecting flow execution.
    """

    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Handle flow start event.

        Args:
            flow_name: Name of the flow that is starting
            message: Initial message being processed

        """
        _ = self, flow_name, message  # No-op in base implementation

    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Handle flow end event.

        Args:
            flow_name: Name of the flow that is ending
            message: Final message from the flow (if successful)
            error: Exception that terminated the flow (if any)

        """
        _ = self, flow_name, message, error  # No-op in base implementation

    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Handle node start event.

        Args:
            node_name: Name of the node about to execute
            message: Message being passed to the node

        """
        _ = self, node_name, message  # No-op in base implementation

    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Handle node end event.

        Args:
            node_name: Name of the node that just executed
            message: Message returned by the node (if successful)
            error: Exception raised by the node (if any)

        """
        _ = self, node_name, message, error  # No-op in base implementation
