"""Observer pattern implementation for message flows."""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import final

from clearflow.message import Message
from clearflow.message_flow import MessageFlow

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class Observer[TMessage: Message](ABC):
    """Observer that processes messages without affecting flow.

    Observers:
    - Cannot modify messages
    - Cannot affect routing
    - Execute concurrently (main flow waits for completion)
    - Errors are isolated and don't break main flow
    """

    name: str

    @abstractmethod
    async def observe(self, message: TMessage) -> None:
        """Process message for side effects only.

        Args:
            message: Message to observe and process

        """
        ...


@final
@dataclass(frozen=True, kw_only=True)
class ObservableFlow[TStart: Message, TEnd: Message]:
    """Wraps a core flow to add observation capabilities.

    Provides non-invasive observation of message flows without affecting
    the core business logic or routing behavior.
    """

    core_flow: MessageFlow[TStart, TEnd]
    observers: Mapping[type[Message], tuple[Observer[Message], ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def observe[TMsg: Message](
        self, message_type: type[TMsg], observer: Observer[TMsg]
    ) -> "ObservableFlow[TStart, TEnd]":
        """Add an observer for a specific message type.

        Args:
            message_type: Type of message to observe
            observer: Observer instance to add

        Returns:
            New ObservableFlow with the observer added

        """
        current = self.observers.get(message_type, ())
        new_observers_dict = {**self.observers, message_type: (*current, observer)}
        return replace(self, observers=MappingProxyType(new_observers_dict))

    async def execute(self, start_message: TStart) -> TEnd:
        """Execute flow with automatic observation.

        Args:
            start_message: Initial message to start the flow

        Returns:
            Final message from the core flow

        """
        return await self._execute_with_interception(start_message)

    async def _execute_with_interception(self, start_message: TStart) -> TEnd:
        """Execute core flow while intercepting all messages.

        Args:
            start_message: Initial message to start the flow

        Returns:
            Final message from the core flow

        """
        current_message = start_message
        current_node = self.core_flow.start_node

        # Observe the initial message
        await self._notify_observers(current_message)

        while True:
            # Execute node
            output_message = await current_node.process(current_message)

            # INTERCEPT: Notify observers asynchronously
            await self._notify_observers(output_message)

            # Check if we're at termination
            route_key = (type(output_message), current_node.name)
            next_node = self.core_flow.routes.get(route_key)

            if next_node is None:
                return output_message  # type: ignore[return-value]

            # Continue routing
            current_node = next_node
            current_message = output_message

    async def _notify_observers(self, message: Message) -> None:
        """Notify all observers registered for this message type.

        Args:
            message: Message to send to observers

        """
        observers = self._get_observers_for(type(message))

        if observers:
            # Run observers concurrently and await completion
            tasks = tuple(self._safe_observe(obs, message) for obs in observers)
            # Use gather with return_exceptions to ensure error isolation
            await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    async def _safe_observe(observer: Observer[Message], message: Message) -> None:
        """Execute observer with error isolation.

        Args:
            observer: Observer to execute
            message: Message to pass to observer

        """
        try:
            await observer.observe(message)
        except Exception:
            logger.exception("Observer %s failed", observer.name)

    def _get_observers_for(self, message_type: type[Message]) -> tuple[Observer[Message], ...]:
        """Get all observers that can handle this message type.

        Args:
            message_type: Type of message to find observers for

        Returns:
            Tuple of observers that can handle the message type

        """
        observers = []

        # Check exact type
        observers.extend(self.observers.get(message_type, ()))

        # Check base types (e.g., Observer[Event] handles all Events)
        for obs_type, obs_list in self.observers.items():
            if obs_type != message_type and issubclass(message_type, obs_type):
                observers.extend(obs_list)

        return tuple(observers)
