"""Callback system for observing flow execution without affecting control flow.

This module provides the callback interface for ClearFlow, enabling integration
with observability platforms, debugging tools, and user interfaces without
introducing dependencies or affecting flow execution.
"""

import sys
from typing import override

from clearflow.message import Message


class CallbackHandler:
    """Base class for handling flow lifecycle callbacks.

    REQ-001: Defines CallbackHandler base class with lifecycle methods.
    REQ-002: Includes four async lifecycle methods for flow and node events.
    REQ-003: All methods have default no-op implementations.
    REQ-004: Uses only Python standard library types.

    Callbacks enable observation of flow execution without affecting control flow.
    Errors in callbacks are logged but not propagated, ensuring flows continue
    regardless of callback failures.
    """

    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Handle flow start event.

        Args:
            flow_name: Name of the flow that is starting
            message: Initial message being processed

        Note:
            Default implementation is a no-op (REQ-003).
            Errors in this method will not affect flow execution (REQ-005).

        """
        _ = self  # Subclasses may use self
        del flow_name, message  # Unused in base implementation

    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Handle flow end event.

        Args:
            flow_name: Name of the flow that is ending
            message: Final message from the flow (if successful)
            error: Exception that terminated the flow (if any)

        Note:
            Default implementation is a no-op (REQ-003).
            Errors in this method will not affect flow execution (REQ-005).

        """
        _ = self  # Subclasses may use self
        del flow_name, message, error  # Unused in base implementation

    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Handle node start event.

        Args:
            node_name: Name of the node about to execute
            message: Message being passed to the node

        Note:
            Default implementation is a no-op (REQ-003).
            Errors in this method will not affect flow execution (REQ-005).

        """
        _ = self  # Subclasses may use self
        del node_name, message  # Unused in base implementation

    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Handle node end event.

        Args:
            node_name: Name of the node that just executed
            message: Message returned by the node (if successful)
            error: Exception raised by the node (if any)

        Note:
            Default implementation is a no-op (REQ-003).
            Errors in this method will not affect flow execution (REQ-005).

        """
        _ = self  # Subclasses may use self
        del node_name, message, error  # Unused in base implementation


class CompositeHandler(CallbackHandler):
    """Callback handler that executes multiple handlers in order.

    REQ-008: Provides CompositeHandler for multiple handlers.

    Each handler is executed in registration order, with errors isolated
    so one handler's failure doesn't affect others.
    """

    def __init__(self, *handlers: CallbackHandler) -> None:
        """Initialize with multiple handlers.

        Args:
            *handlers: Callback handlers to execute in order

        """
        self.handlers = handlers

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Execute all handlers' on_flow_start methods.

        Args:
            flow_name: Name of the flow that is starting
            message: Initial message being processed

        """
        for handler in self.handlers:
            try:
                await handler.on_flow_start(flow_name, message)
            except Exception as e:  # noqa: BLE001  # REQ-005: Catch all exceptions
                sys.stderr.write(f"CompositeHandler: {handler.__class__.__name__}.on_flow_start failed: {e}\n")

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Execute all handlers' on_flow_end methods.

        Args:
            flow_name: Name of the flow that is ending
            message: Final message from the flow
            error: Exception that terminated the flow (if any)

        """
        for handler in self.handlers:
            try:
                await handler.on_flow_end(flow_name, message, error)
            except Exception as e:  # noqa: BLE001  # REQ-005: Catch all exceptions
                sys.stderr.write(f"CompositeHandler: {handler.__class__.__name__}.on_flow_end failed: {e}\n")

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Execute all handlers' on_node_start methods.

        Args:
            node_name: Name of the node about to execute
            message: Message being passed to the node

        """
        for handler in self.handlers:
            try:
                await handler.on_node_start(node_name, message)
            except Exception as e:  # noqa: BLE001  # REQ-005: Catch all exceptions
                sys.stderr.write(f"CompositeHandler: {handler.__class__.__name__}.on_node_start failed: {e}\n")

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Execute all handlers' on_node_end methods.

        Args:
            node_name: Name of the node that just executed
            message: Message returned by the node
            error: Exception raised by the node (if any)

        """
        for handler in self.handlers:
            try:
                await handler.on_node_end(node_name, message, error)
            except Exception as e:  # noqa: BLE001  # REQ-005: Catch all exceptions
                sys.stderr.write(f"CompositeHandler: {handler.__class__.__name__}.on_node_end failed: {e}\n")
