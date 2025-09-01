# Type Transformation Design for ClearFlow

## Executive Summary

ClearFlow needs to support type-transforming nodes (`Node[TIn, TOut]`) to enable real-world, mission-critical workflows where data fundamentally changes shape as it flows through processing stages. This document captures the analysis, design decisions, and rationale for this enhancement.

## Problem Statement

### Current Limitation
ClearFlow currently only supports `Node[T]` where input and output types are the same. This forces developers to:
- Use bloated "god objects" containing all possible fields
- Use union types with runtime `isinstance` checks
- Write defensive code for "impossible" states
- Sacrifice type safety at stage boundaries

### Real-World Need
Mission-critical systems require type transformation:
- **Medical**: `RawPatientData → ValidatedData → Diagnosis → TreatmentPlan`
- **Financial**: `PaymentRequest → RiskAssessment → ApprovedTransaction → Settlement`
- **Aerospace**: `SensorReadings → CalibratedData → ControlCommands → ActuatorSignals`
- **Document Processing**: `RawBytes → ParsedContent → ExtractedEntities → IndexedDocument`

## Design Analysis

### Options Considered

#### 1. Union Types (Current Workaround)
```python
State = StateA | StateB | StateC
# Every node needs isinstance checks
```
**Rejected**: Forces defensive programming, reduces type safety, creates unreachable code paths.

#### 2. Compositional Approach (Haskell-style)
```python
node1.then(node2).then(node3)  # Type-safe composition
```
**Rejected**: Incompatible with dynamic routing based on runtime values.

#### 3. Type Erasure with Protocols
```python
class StateProtocol(Protocol): ...
Node[TIn: StateProtocol, TOut: StateProtocol]
```
**Rejected**: Doesn't solve the core problem, adds unnecessary complexity.

#### 4. Honest Runtime Reality (Selected)
```python
class Node[TIn, TOut](ABC): ...  # Public API: strongly typed
class _Flow[TIn, TOut](Node[TIn, TOut]):
    start_node: object  # Internal: honest about runtime dynamism
```
**Selected**: Acknowledges Python's limitations while maintaining type safety at boundaries.

### Key Insight: Boundary vs Implementation

Similar to our immutability pattern (public `tuple`, internal `list`), we maintain:
- **Strong types at public boundaries** - All public APIs use proper types
- **Pragmatic implementation internally** - Use `object` for dynamic routing
- **Type safety preserved** - Users get full type checking at API level

## Design Decision

### Core Principles

1. **Type Safety at Boundaries**: Public methods strictly typed
2. **Internal Pragmatism**: Implementation uses `object` for routing
3. **No Backwards Compatibility**: Breaking changes acceptable
4. **Documentation Honesty**: Clear about why `object` is used internally
5. **Mission-Critical Standards**: No suppressions, 100% coverage

### Final Design

```python
from typing import TypeVar
from abc import ABC, abstractmethod

# Module-level type variables for transformations
TIn = TypeVar("TIn")
TOut = TypeVar("TOut")

@dataclass(frozen=True, kw_only=True)
class Node[TIn, TOut](ABC):
    """A node that transforms state from TIn to TOut.
    
    Examples:
    - Non-transforming: Node[State, State]
    - Transforming: Node[InputState, OutputState]
    """
    name: str = field(default="")
    
    @abstractmethod
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        """Execute transformation with full type safety."""
        ...

@dataclass(frozen=True, kw_only=True)
class _Flow[TIn, TOut](Node[TIn, TOut]):
    """Flow orchestrating nodes to transform TIn to TOut.
    
    Internal implementation uses object for dynamic routing.
    This is a fundamental limitation: static typing cannot
    track types through runtime-determined paths.
    """
    
    # Internal fields use object - this is an implementation detail
    # hidden from users. The public exec() method maintains type safety.
    start_node: object  # First node, determined at build time
    routes: Mapping[RouteKey, object | None]  # Dynamic routing table
    
    @override
    async def exec(self, state: TIn) -> NodeResult[TOut]:
        """Execute flow with guaranteed TIn→TOut transformation."""
        current_node: object = self.start_node
        current_state: object = state
        
        while True:
            result = await current_node(current_state)
            # ... routing logic ...
            
        # Type assertion at boundary - construction ensures this is correct
        return cast(NodeResult[TOut], result)
```

### Flow Builder Updates

```python
@dataclass(frozen=True)
class Flow[TIn, TOut]:
    """Type-safe flow builder."""
    _name: str
    
    def start_with(self, node: Node[TIn, Any]) -> _StartedWithFlow[TIn, Any]:
        """Start with a node that accepts TIn."""
        ...

@dataclass(frozen=True)
class _StartedWithFlow[TIn, TCurrent]:
    """Flow builder tracking current output type."""
    
    def route(self, 
              from_node: object,  # Any node previously added
              outcome: str,
              to_node: object | None) -> _StartedWithFlow[TIn, Any]:
        """Add route - types checked at runtime during build."""
        ...
    
    def build(self) -> Node[TIn, Any]:
        """Build flow - output type determined by termination points."""
        ...
```

## Rationale

### Why Use `object` Internally?

1. **It's Honest**: We genuinely cannot know intermediate types at compile time with dynamic routing
2. **It's Contained**: Only used internally, never exposed in public API
3. **It's Documented**: Clear explanation in docstrings and comments
4. **It's Necessary**: No other solution exists for dynamic routing in Python's type system
5. **It's Safe**: Type safety maintained at API boundaries

### Why This Approach?

1. **Enables Real Workflows**: Supports actual data transformation patterns
2. **Maintains Type Safety**: Full checking at public boundaries
3. **Pythonic**: Embraces duck typing internally, strong contracts externally
4. **Mission-Critical**: No defensive code, no unreachable paths
5. **Honest**: Acknowledges language limitations rather than fighting them

## Migration Impact

### Breaking Changes

1. `Node[T]` becomes `Node[TIn, TOut]`
2. Flow builder API changes to handle type parameters
3. Existing code needs updates (no backwards compatibility)

### Benefits After Migration

1. **Explicit Transformations**: `Node[RawData, ProcessedData]`
2. **No isinstance Checks**: Types are known at compile time
3. **100% Test Coverage**: No unreachable defensive code
4. **Better Documentation**: Types document the transformation
5. **Memory Efficiency**: No need to carry all data through pipeline

## Success Criteria

1. Sociocracy can use `Node[PreSynthesisState, PostSynthesisState]` without isinstance
2. All quality checks pass (mypy, pyright, ruff)
3. 100% test coverage maintained
4. No type suppressions needed
5. Real-world examples demonstrate value

## Decision Record

**Date**: 2025-08-31
**Decision**: Implement type transformation support using `object` internally
**Rationale**: Enables mission-critical workflows while acknowledging Python's type system limitations
**Trade-offs**: Internal use of `object` vs impossible perfect static typing with dynamic routing