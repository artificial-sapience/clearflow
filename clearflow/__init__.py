# Copyright (c) 2025 ClearFlow Contributors

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Protocol, TypeVar, cast, override

__all__ = [
    "Node",
    "NodeResult",
    "flow",
]

# Type definitions needed for mypy compatibility with PEP 695 syntax
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


@dataclass(frozen=True)
class NodeResult[T]:
    """Result of node execution with state and outcome."""

    state: T
    outcome: Outcome


# Type alias for NodeResult with unknown state type
AnyNodeResult = NodeResult[Any]


@dataclass(frozen=True, kw_only=True)
class Node[TIn, TOut = TIn](ABC, NodeBase):
    """Abstract base for workflow nodes.

    Subclass and implement async exec() to process state and return outcomes for routing.
    Supports optional prep() and post() hooks for setup and cleanup.

    Type parameters:
        TIn: Input state type
        TOut: Output state type (defaults to TIn for non-transforming nodes)

    Examples:
        Node[State]           # Non-transforming: State -> State
        Node[Input, Output]   # Transforming: Input -> Output

    """

    name: str  # Required - subclasses must provide at construction

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
        current_node = self.start_node
        current_state: object = state

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
            current_state = result.state  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]


@dataclass(frozen=True)
class _FlowBuilder[TIn]:
    """Flow builder for composing node routes.

    TIn: The input type the flow accepts

    This builder creates an incomplete flow. Call terminate() to specify
    the termination node and get a _TerminatedFlowBuilder that can be built.
    """

    _name: str
    _start: NodeBase  # Starting node (type-erased)
    _routes: MappingProxyType[RouteKey, NodeBase | None]  # Heterogeneous node types

    def route(
        self,
        from_node: NodeBase,
        outcome: Outcome,
        to_node: NodeBase,  # Note: No longer accepts None
    ) -> "_FlowBuilder[TIn]":
        """Connect nodes: from_node --outcome--> to_node.

        Args:
            from_node: Source node
            outcome: Outcome string that triggers this route
            to_node: Destination node (use terminate() for flow termination)

        Returns:
            New FlowBuilder with added route

        """
        if not from_node.name:
            msg = f"from_node must have a non-empty name: {from_node}"
            raise ValueError(msg)

        # Create new dict with existing routes plus new route
        route_key: RouteKey = (from_node.name, outcome)
        new_routes = {**self._routes, route_key: to_node}

        return _FlowBuilder[TIn](
            _name=self._name,
            _start=self._start,
            _routes=MappingProxyType(new_routes),
        )

    def terminate[TOut](
        self,
        node: Node[TAny, TOut],  # Any input, specific output
        outcome: Outcome,
    ) -> "_TerminatedFlowBuilder[TIn, TOut]":
        """Specify the termination node and outcome.

        This creates a complete flow that can be built. The output type
        of the flow is determined by the termination node's output type.

        Args:
            node: The node that terminates the flow
            outcome: The outcome from this node that ends the flow

        Returns:
            A TerminatedFlowBuilder that can be built into a flow

        """
        if not node.name:
            msg = f"Termination node must have a non-empty name: {node}"
            raise ValueError(msg)

        # Check if there's already a termination (None route)
        for (from_node, _), to_node in self._routes.items():
            if to_node is None:
                msg = (
                    f"Flow '{self._name}' already has a termination from "
                    f"node '{from_node}'. Only one termination is allowed."
                )
                raise ValueError(msg)

        # Add the termination route
        route_key: RouteKey = (node.name, outcome)
        new_routes = {**self._routes, route_key: None}

        return _TerminatedFlowBuilder[TIn, TOut](
            _name=self._name,
            _start=self._start,
            _routes=MappingProxyType(new_routes),
            _termination_node=node,
        )


@dataclass(frozen=True)
class _TerminatedFlowBuilder[TIn, TOut]:
    """A flow builder with a defined termination point.

    This builder represents a complete flow that can be built.
    The flow transforms TIn to TOut, where TOut is determined
    by the termination node's output type.
    """

    _name: str
    _start: NodeBase
    _routes: MappingProxyType[RouteKey, NodeBase | None]
    _termination_node: Node[TAny, TOut]  # Tracks the output type

    def build(self) -> Node[TIn, TOut]:
        """Build and return the flow as a Node.

        Returns:
            A flow node that transforms TIn to TOut

        """
        return _Flow[TIn, TOut](
            name=self._name,
            start_node=self._start,
            routes=self._routes,
        )


def flow[TIn, TOut](name: str, start: Node[TIn, TOut]) -> _FlowBuilder[TIn]:
    """Create a flow with the given name and starting node.

    Args:
        name: The name of the flow
        start: The starting node that accepts TIn and outputs TOut

    Returns:
        A flow builder for chaining route definitions

    Example:
        flow("Pipeline", my_node).route(...).build()

    """
    if not name or not name.strip():
        msg = "Flow name must be a non-empty string"
        raise ValueError(msg)

    return _FlowBuilder[TIn](
        _name=name,
        _start=start,  # Will be treated as NodeBase
        _routes=MappingProxyType({}),  # Empty immutable mapping
    )
