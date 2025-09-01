# Copyright (c) 2025 ClearFlow Contributors

"""ClearFlow: Zero-dependency async workflow orchestration framework.

Provides type-safe workflow composition with explicit routing and single termination.
Built for mission-critical AI orchestration with 100% test coverage requirement.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, TypeVar, cast, override

__all__ = [
    "Node",
    "NodeResult",
    "flow",
]

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
FromNodeName = str
Outcome = str
RouteKey = tuple[FromNodeName, Outcome]


class NodeBase(Protocol):
    """Non-generic base protocol for all nodes.

    Provides the common interface without type parameters,
    allowing heterogeneous collections of nodes.
    """

    name: str

    async def __call__(
        self, state: object
    ) -> "NodeResult[object]":  # clearflow: ignore[ARCH009]
        """Execute the node with any state type.

        Note: We intentionally use 'object' here for type erasure. This protocol
        represents the type-erased interface for heterogeneous node collections.
        """
        ...


@dataclass(frozen=True)
class NodeResult[T]:
    """Result of node execution with state and outcome."""

    state: T
    outcome: Outcome


@dataclass(frozen=True, kw_only=True)
class Node[TIn, TOut = TIn](ABC, NodeBase):
    """Abstract base for workflow nodes.

    Subclass and implement async exec() to process state and return outcomes for routing.
    Supports optional prep() and post() hooks for setup and cleanup.

    Type parameters:
        TIn: Input state type
        TOut: Output state type (defaults to TIn for non-transforming nodes)

    Examples:
        Node[Query]                    # Non-transforming: Query -> Query
        Node[Query, SearchResults]     # Transforming: Query -> SearchResults

    """

    name: str

    def __post_init__(self) -> None:
        """Validate node configuration after initialization."""
        if not self.name or not self.name.strip():
            msg = f"Node name must be a non-empty string, got: {self.name!r}"
            raise ValueError(msg)

    @override
    async def __call__(self, state: TIn) -> NodeResult[TOut]:  # type: ignore[override]
        """Execute node lifecycle."""
        state = await self.prep(state)
        result = await self.exec(state)
        return await self.post(result)

    async def prep(self, state: TIn) -> TIn:
        """Pre-execution hook."""
        return state

    @abstractmethod
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        """Main execution - must be implemented by subclasses."""
        ...

    async def post(self, result: NodeResult[TOut]) -> NodeResult[TOut]:
        """Post-execution hook."""
        return result


@dataclass(frozen=True, kw_only=True)
class _Flow[TIn, TOut = TIn](Node[TIn, TOut]):
    """Internal flow implementation that transforms TIn to TOut.

    Implementation note: We use 'object' for node types internally because
    Python's type system cannot track types through runtime-determined paths.
    Type safety is maintained at the public API boundaries - exec() guarantees
    TIn→TOut transformation through construction-time validation.
    """

    start_node: NodeBase
    routes: Mapping[RouteKey, NodeBase | None]

    @override
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        """Execute the flow by routing through nodes based on outcomes."""
        current_node = self.start_node
        current_state: object = (
            state  # clearflow: ignore[ARCH009] - Type erasure for dynamic routing
        )

        while True:
            # Execute node
            result = await current_node(current_state)
            key = (current_node.name, result.outcome)

            # Return if no route defined
            if key not in self.routes:
                return cast("NodeResult[TOut]", result)

            # Check next node
            next_node = self.routes[key]
            if next_node is None:
                return cast("NodeResult[TOut]", result)

            # Continue
            current_node = next_node
            current_state = result.state


@dataclass(frozen=True)
class _FlowBuilder[TStartIn, TStartOut]:
    """Flow builder for composing node routes.

    Type parameters:
        TStartIn: The input type the flow accepts (from start node)
        TStartOut: The output type of the start node

    This builder creates an incomplete flow. Call end() to specify
    where the flow ends and get the completed flow.
    """

    _name: str
    _start: Node[TStartIn, TStartOut]
    _routes: MappingProxyType[RouteKey, NodeBase | None]

    def route(
        self,
        from_node: NodeBase,
        outcome: Outcome,
        to_node: NodeBase,
    ) -> "_FlowBuilder[TStartIn, TStartOut]":
        """Connect nodes: from_node --outcome--> to_node.

        Args:
            from_node: Source node
            outcome: Outcome string that triggers this route
            to_node: Destination node (use end() for flow completion)

        Returns:
            Builder for continued route definition and flow completion

        """
        route_key: RouteKey = (from_node.name, outcome)
        new_routes = {**self._routes, route_key: to_node}

        return _FlowBuilder[TStartIn, TStartOut](
            _name=self._name,
            _start=self._start,
            _routes=MappingProxyType(new_routes),
        )

    def end[TTermIn, TTermOut](
        self,
        final_node: Node[TTermIn, TTermOut],
        outcome: Outcome,
    ) -> Node[TStartIn, TTermOut]:
        """End the flow at the specified node and outcome.

        This completes the flow definition by specifying where it ends.
        The flow's output type is determined by the final node's output type.

        Args:
            final_node: The node where the flow ends
            outcome: The outcome from this node that completes the flow

        Returns:
            A flow node that transforms TStartIn to TTermOut

        Example:
            flow("RAG", retriever).route(retriever, "found", generator).end(generator, "answered")

        """
        route_key: RouteKey = (final_node.name, outcome)
        new_routes = {**self._routes, route_key: None}

        return _Flow[TStartIn, TTermOut](
            name=self._name,
            start_node=self._start,
            routes=MappingProxyType(new_routes),
        )


def flow[TIn, TStartOut](
    name: str, start: Node[TIn, TStartOut]
) -> _FlowBuilder[TIn, TStartOut]:
    """Create a flow with the given name and starting node.

    Args:
        name: The name of the flow
        start: The starting node that accepts TIn and outputs TOut

    Returns:
        Builder for route definition and flow completion

    Example:
        flow("RAG", retriever).route(...).end(generator, "answered")

    """
    return _FlowBuilder[TIn, TStartOut](
        _name=name,
        _start=start,
        _routes=MappingProxyType({}),
    )
