"""Internal callback handler implementation."""

import sys
from collections.abc import Sequence

from clearflow.message import Message
from clearflow.observer import Observer


class CallbackHandler:
    """Internal handler that manages observers with automatic error isolation."""

    def __init__(self, observers: Sequence[Observer]) -> None:
        """Initialize with observers.

        Args:
            observers: Sequence of observer instances to notify

        """
        self._observers = tuple(observers) if observers else ()

    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Notify all observers of flow start.

        Args:
            flow_name: Name of the flow that is starting
            message: Initial message being processed

        """
        for observer in self._observers:
            try:
                await observer.on_flow_start(flow_name, message)
            except Exception as e:  # noqa: BLE001  # Isolate observer errors
                sys.stderr.write(f"Observer error in {observer.__class__.__name__}.on_flow_start: {e}\n")

    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Notify all observers of flow end.

        Args:
            flow_name: Name of the flow that is ending
            message: Final message from the flow
            error: Exception that terminated the flow (if any)

        """
        for observer in self._observers:
            try:
                await observer.on_flow_end(flow_name, message, error)
            except Exception as e:  # noqa: BLE001  # Isolate observer errors
                sys.stderr.write(f"Observer error in {observer.__class__.__name__}.on_flow_end: {e}\n")

    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Notify all observers of node start.

        Args:
            node_name: Name of the node about to execute
            message: Message being passed to the node

        """
        for observer in self._observers:
            try:
                await observer.on_node_start(node_name, message)
            except Exception as e:  # noqa: BLE001  # Isolate observer errors
                sys.stderr.write(f"Observer error in {observer.__class__.__name__}.on_node_start: {e}\n")

    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Notify all observers of node end.

        Args:
            node_name: Name of the node that just executed
            message: Message returned by the node
            error: Exception raised by the node (if any)

        """
        for observer in self._observers:
            try:
                await observer.on_node_end(node_name, message, error)
            except Exception as e:  # noqa: BLE001  # Isolate observer errors
                sys.stderr.write(f"Observer error in {observer.__class__.__name__}.on_node_end: {e}\n")
