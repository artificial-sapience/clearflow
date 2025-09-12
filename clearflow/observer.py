"""Observer pattern implementation for message flows."""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import cast, final, override

from clearflow.message import Message

__all__ = [
    "ObservableFlow",
    "Observer",
]

# Import internal flow implementation for decorator pattern
# This is intentionally using a private class within the same package
from clearflow.message_flow import (
    MessageRouteKey,
    _MessageFlow,  # pyright: ignore[reportPrivateUsage]  # Internal package use
)
from clearflow.message_node import Node


@dataclass(frozen=True, kw_only=True)
class Observer[TMessage: Message](ABC):
    """Observer that processes messages without affecting routing.

    Observers:
    - Cannot modify messages
    - Cannot affect routing decisions
    - Execute concurrently (main flow waits for completion)
    - Exceptions propagate and stop flow execution immediately (fail-fast)

    Example: A SecurityObserver can throw SecurityViolationException to halt
    suspicious operations immediately.
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
class ObservableFlow[TStart: Message, TEnd: Message](Node[TStart, TEnd]):
    """Observable decorator for message flows (not individual nodes).

    Decorates ONLY message flows (_MessageFlow) with observation capabilities.
    This is intentional - we observe workflows, not individual operations.
    Provides non-invasive observation of message flows without affecting
    the core business logic or routing behavior.
    Being a Node allows observable flows to be nested within other flows.
    """

    name: str
    flow: _MessageFlow[TStart, TEnd]  # Explicitly requires a flow, not any node
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

    @override
    async def process(self, message: TStart) -> TEnd:
        """Process flow with observation of all intermediate messages.

        Args:
            message: Initial message to start the flow

        Returns:
            Final message when flow reaches termination

        """
        # Direct access to flow internals - no casting or isinstance needed!
        current_node = self.flow.start_node
        current_message: Message = message

        # Observe the initial message
        await self._notify_observers(current_message)

        while True:
            # Execute node
            output_message = await current_node.process(current_message)

            # Observe the output
            await self._notify_observers(output_message)

            # Route to next node
            route_key: MessageRouteKey = (type(output_message), current_node.name)
            next_node = self.flow.routes.get(route_key)

            if next_node is None:
                return cast("TEnd", output_message)

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
            # Run observers concurrently - exceptions will propagate immediately
            tasks = tuple(obs.observe(message) for obs in observers)
            # Without return_exceptions, any observer exception stops the flow
            await asyncio.gather(*tasks)

    def _get_observers_for(self, message_type: type[Message]) -> tuple[Observer[Message], ...]:
        """Get all observers that can handle this message type.

        Args:
            message_type: Type of message to find observers for

        Returns:
            Tuple of observers that can handle the message type

        """
        exact_observers = self.observers.get(message_type, ())

        base_observers = tuple(
            obs
            for obs_type, obs_list in self.observers.items()
            if obs_type != message_type and issubclass(message_type, obs_type)
            for obs in obs_list
        )

        return exact_observers + base_observers
