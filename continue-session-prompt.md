# Continue Session: Fix Critical Type Safety Issue

## Context

See `session-context.md` for the full discovery of the PEP 695 variance issue that undermines our terminal type pattern.

## The Problem

PEP 695's automatic variance inference makes our `Node[TIn, TOut]` type parameters:
- `TIn`: contravariant (input only)
- `TOut`: **covariant** (output only)

This allows unsafe assignments like:
```python
concrete: Node[StartChat, ChatCompleted] = ...
wider: Node[StartChat, ChatCompleted | UserMessageReceived] = concrete  # ALLOWED (bad!)
```

## Your Mission

Help me fix this critical type safety issue. See `plan.md` for the full task list.

## Primary Options to Explore

### Option 1: Switch to Traditional TypeVars
```python
from typing import TypeVar, Generic

TMessageIn = TypeVar('TMessageIn', bound=Message)  # Invariant
TMessageOut = TypeVar('TMessageOut', bound=Message)  # Invariant

class NodeInterface(Generic[TMessageIn, TMessageOut], ABC):
    ...
```

### Option 2: Force Invariance Through Usage
Add dummy usage to make type parameters appear in both positions:
```python
class NodeInterface[TMessageIn, TMessageOut]:
    _phantom_in: TMessageOut | None = None  # Force TMessageOut in input position
    _phantom_out: type[TMessageIn] | None = None  # Force TMessageIn in output position
```

### Option 3: Runtime Validation
Keep current code but add runtime checks and better documentation.

## Success Criteria

1. Type checkers catch incorrect union return types
2. `create_chat_flow()` correctly typed as `-> Node[StartChat, ChatCompleted]`
3. All examples pass type checking with correct annotations
4. Solution maintains clean API and good developer experience

## Start By

1. Test which option works best for enforcing invariance
2. Implement the fix across the codebase
3. Update all example type annotations
4. Ensure 100% test coverage still passes
5. Document the solution and any limitations

Please think carefully about the trade-offs of each approach before proceeding.