# Copyright (c) 2025 ClearFlow Contributors

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TypeVar, cast, override

__all__ = [
    "Flow",
    "Node",
    "NodeResult",
]

# Type definitions
T = TypeVar("T")  # Kept for backwards naming compatibility
TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
FromNodeName = str
Outcome = str
RouteKey = tuple[FromNodeName, Outcome]


@dataclass(frozen=True)
class NodeResult[T]:
    """Result of node execution with state and outcome."""

    state: T
    outcome: Outcome


@dataclass(frozen=True, kw_only=True)
class Node[TIn, TOut=TIn](ABC):
    """Async node that transforms state from TIn to TOut.
    
    For non-transforming nodes, use Node[T] which defaults to Node[T, T].
    For transforming nodes, use Node[TIn, TOut] explicitly.
    
    Examples:
        Node[State]           # Non-transforming: State -> State
        Node[State, State]    # Explicit non-transforming
        Node[Input, Output]   # Transforming: Input -> Output
    """

    name: str = field(default="")

    def __post_init__(self) -> None:
        """Set name from class if not provided."""
        if not self.name:
            # Use object.__setattr__ to bypass frozen dataclass restriction
            object.__setattr__(self, "name", self.__class__.__name__)

    async def __call__(self, state: TIn) -> NodeResult[TOut]:
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
class _Flow[TIn, TOut=TIn](Node[TIn, TOut]):
    """Internal flow implementation that transforms TIn to TOut.
    
    Implementation note: We use 'object' for node types internally because
    Python's type system cannot track types through runtime-determined paths.
    Type safety is maintained at the public API boundaries - exec() guarantees
    TIn→TOut transformation through construction-time validation.
    """

    start_node: object  # clearflow: ignore[ARCH009] - Runtime routing requires object type; types validated at build time
    routes: Mapping[RouteKey, object | None]  # clearflow: ignore[ARCH009] - Runtime routing table; node types vary by route

    @override
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        current_node: object = self.start_node  # clearflow: ignore[ARCH009] - Runtime dispatch; actual types tracked at build
        current_state: object = state  # clearflow: ignore[ARCH009] - State transforms through pipeline; type varies per node

        # Execution loop
        while True:
            # Execute current node
            result = await current_node(current_state)

            # Find next node in routes based on outcome
            key: RouteKey = (current_node.name, result.outcome)

            # Check if route exists
            if key not in self.routes:
                # No route defined - for nested flows, bubble up the outcome
                # For top-level flows, this is an error
                if not self.routes:
                    # Flow has no routes at all - it's a single-node flow
                    # Return the result as-is
                    return cast(NodeResult[TOut], result)
                # Flow has some routes but not for this outcome
                # This means the flow should terminate with this outcome
                return cast(NodeResult[TOut], result)

            next_node = self.routes[key]

            if next_node is None:
                # Explicit termination - cast is safe due to build-time validation
                return cast(NodeResult[TOut], result)
            # Continue to next node
            current_node = next_node
            current_state = result.state


@dataclass(frozen=True)
class _StartedWithFlow[TIn, TCurrent]:
    """Private: Flow builder tracking current output type.
    
    TIn: The input type the flow starts with
    TCurrent: The current output type at this stage of building
    """

    _name: str
    _start: Node[TIn, object]  # clearflow: ignore[ARCH009] - Build-time type validation; runtime needs object
    _routes: MappingProxyType[RouteKey, object | None]  # clearflow: ignore[ARCH009] - Dynamic routing table holds heterogeneous node types

    def route(
        self, from_node: object, outcome: Outcome, to_node: object | None  # clearflow: ignore[ARCH009] - Nodes have varying types; validated at build
    ) -> "_StartedWithFlow[TIn, object]":  # clearflow: ignore[ARCH009] - Return type tracks build progress
        """Connect nodes: from_node --outcome--> to_node.
        
        Type checking is performed at runtime during build.
        We use 'object' here because Python cannot track types through
        dynamic routing at compile time.
        """
        if not hasattr(from_node, 'name') or not from_node.name:  # type: ignore[attr-defined]
            msg = f"from_node must have a name: {from_node}"
            raise ValueError(msg)

        # Create new dict with existing routes plus new route
        route_key: RouteKey = (from_node.name, outcome)  # type: ignore[attr-defined]
        new_routes = {**self._routes, route_key: to_node}

        return _StartedWithFlow[TIn, object](  # clearflow: ignore[ARCH009] - Build-time type tracking
            _name=self._name, _start=self._start, _routes=MappingProxyType(new_routes)
        )

    def build(self) -> Node[TIn, object]:  # clearflow: ignore[ARCH009] - Returns flow with runtime dispatch
        """Build and return the flow as a Node.
        
        The output type is 'object' because it depends on runtime routing.
        Type safety is maintained at the API boundary.
        """
        # Validate single termination
        none_routes = [
            (from_node, outcome)
            for (from_node, outcome), to_node in self._routes.items()
            if to_node is None
        ]

        if len(none_routes) > 1:
            msg = (
                f"Flow '{self._name}' has multiple termination points "
                f"(routes to None): {none_routes}. "
                f"Flows must have exactly one termination point."
            )
            raise ValueError(msg)

        return _Flow[TIn, object](name=self._name, start_node=self._start, routes=self._routes)  # clearflow: ignore[ARCH009] - Flow with runtime type dispatch


@dataclass(frozen=True)
class Flow[TIn, TOut=TIn]:
    """Type-safe flow builder with immutable construction.
    
    TIn: Input type the flow accepts
    TOut: Output type the flow produces (defaults to TIn for non-transforming flows)
    """

    _name: str

    def __post_init__(self) -> None:
        """Validate flow name."""
        if not self._name or not self._name.strip():
            msg = "Flow name must be a non-empty string"
            raise ValueError(msg)

    def start_with(self, node: Node[TIn, object]) -> _StartedWithFlow[TIn, object]:  # clearflow: ignore[ARCH009] - Accept any output type from start node
        """Set starting node that accepts TIn.
        
        The node's input type must match TIn, output type can be anything.
        """
        return _StartedWithFlow[TIn, object](  # clearflow: ignore[ARCH009] - Builder tracks TIn, output varies
            _name=self._name,
            _start=node,
            _routes=MappingProxyType({}),  # Explicit empty immutable mapping
        )
