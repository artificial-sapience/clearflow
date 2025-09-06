# Migration Guide: v0.x to v1.0

This guide covers breaking changes and migration steps for ClearFlow v1.0.

## Breaking Changes

### 1. Node Type Parameters

**Before:** Single type parameter

```python
class MyNode(Node[StateType]):
    async def exec(self, state: StateType) -> NodeResult[StateType]:
        ...
```

**After:** Input/Output type parameters

```python
@dataclass(frozen=True)
class MyNode(Node[StateType]):  # TOut defaults to TIn
    name: str = "my_node"
    
    @override
    async def exec(self, state: StateType) -> NodeResult[StateType]:
        ...

# Or with transformation:
@dataclass(frozen=True)
class TransformNode(Node[InputType, OutputType]):
    name: str = "transformer"
    
    @override
    async def exec(self, state: InputType) -> NodeResult[OutputType]:
        ...
```

### 2. Node Name Required

**Before:** Name defaults to class name

```python
class MyNode(Node[T]):
    # name automatically becomes "MyNode"
    pass
```

**After:** Name must be explicit

```python
@dataclass(frozen=True)
class MyNode(Node[T]):
    name: str = "my_node"  # Required field
```

### 3. Flow API Replaced

**Before:** Flow class with add() method

```python
flow = Flow(name="pipeline", start_node=start)
flow.add(start, "success", processor)
flow.add(processor, "done", None)  # Termination
```

**After:** flow() function with builder pattern

```python
flow_instance = (
    flow("pipeline", start)
    .route(start, "success", processor)
    .end(processor, "done")  # Single termination via end()
)
```

### 4. Single Termination Enforcement

**Before:** Multiple terminations allowed

```python
flow.add(node1, "outcome1", None)
flow.add(node2, "outcome2", None)  # Multiple terminations OK
```

**After:** Exactly one termination via end()

```python
flow_instance = (
    flow("pipeline", start)
    .route(start, "path1", node1)
    .route(start, "path2", node2)
    .route(node1, "done", node2)
    .end(node2, "complete")  # Only one end() allowed
)
```

### 5. Reachability Validation

**New:** Cannot route from unreachable nodes

```python
# This will raise ValueError:
flow_instance = (
    flow("pipeline", start)
    .route(unreachable_node, "outcome", end)  # Error: unreachable_node not reachable
    .end(end, "done")
)
```

### 6. Frozen Dataclasses Required

**Before:** Regular classes

```python
class MyNode(Node[T]):
    def __init__(self):
        self.mutable_field = []  # Mutable state allowed
```

**After:** Frozen dataclasses only

```python
@dataclass(frozen=True)
class MyNode(Node[T]):
    name: str = "my_node"
    # All fields must be immutable
```

## Migration Steps

### Step 1: Update Node Definitions

1. Add `@dataclass(frozen=True)` decorator
2. Add explicit `name` field
3. Add `@override` decorator to `exec()`
4. Update type parameters if transforming state

### Step 2: Replace Flow Usage

1. Replace `Flow()` with `flow()` function
2. Replace `.add()` calls with `.route()`
3. Replace termination `add(node, outcome, None)` with `.end(node, outcome)`
4. Ensure only one `.end()` call per flow

### Step 3: Update State Types

1. Ensure all state types are immutable (frozen dataclasses or tuples)
2. Replace mutable operations with `dataclasses.replace()`
3. Use tuples instead of lists for collections

### Step 4: Fix Import Statements

**Before:**

```python
from clearflow import Flow, Node, NodeResult
```

**After:**

```python
from clearflow import flow, Node, NodeResult  # flow is lowercase function
```

## Complete Example

**Before:**

```python
from clearflow import Flow, Node, NodeResult

class ProcessNode(Node[dict]):
    async def exec(self, state: dict) -> NodeResult[dict]:
        state["processed"] = True
        return NodeResult(state, outcome="done")

process = ProcessNode()
flow = Flow(name="pipeline", start_node=process)
flow.add(process, "done", None)
```

**After:**

```python
from dataclasses import dataclass
from typing import override
from clearflow import flow, Node, NodeResult

@dataclass(frozen=True)
class State:
    data: str
    processed: bool = False

@dataclass(frozen=True)
class ProcessNode(Node[State]):
    name: str = "processor"
    
    @override
    async def exec(self, state: State) -> NodeResult[State]:
        from dataclasses import replace
        new_state = replace(state, processed=True)
        return NodeResult(new_state, outcome="done")

process = ProcessNode()
pipeline = flow("pipeline", process).end(process, "done")
```

## Common Issues

### TypeError: Missing required 'name' field

**Solution:** Add `name: str = "node_name"` to your node class

### ValueError: No route defined for outcome

**Solution:** Ensure all possible outcomes have routes or terminations

### ValueError: Cannot route from 'node' - not reachable

**Solution:** Ensure nodes are connected in order from start node

### AttributeError: 'Flow' object has no attribute 'add'

**Solution:** Replace Flow class with flow() function and builder pattern

## Need Help?

See the [examples](examples/) directory for complete working code with the new API.
