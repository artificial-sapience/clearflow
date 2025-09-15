# ClearFlow Architecture Restructuring Plan

## Overview

Migrate ClearFlow to a clean architecture with explicit public/private boundaries using the "_internal/" pattern. This will eliminate ambiguity about what is public API vs internal implementation detail, fixing all linter warnings and making the codebase more maintainable.

## Current Issues

1. `_NodeInterface` causes pyright "private usage" errors when used across modules
2. No clear boundary between public API and internal implementation

## Target Architecture

```text
clearflow/
  __init__.py                 # Re-exports only (no implementation)

  # Public API modules (thin wrappers)
  messages.py                 # Public Message, Command, Event
  nodes.py                    # Public Node (was MessageNode)
  flows.py                    # Public flow (was message_flow)
  callbacks.py                # Public CallbackHandler, CompositeHandler
  strict_base_model.py        # Public StrictBaseModel

  _internal/                  # All real implementation
    __init__.py
    node_interface.py         # NodeInterface (no underscore needed!)
    message_impl.py           # Message, Command, Event implementation
    node_impl.py              # Node implementation (was message_node_impl)
    flow_impl.py              # flow implementation (was message_flow_impl)
    callbacks_impl.py         # Callback implementations
    strict_base_model_impl.py # StrictBaseModel implementation
```

## Remaining Migration Steps

### Step 1: Create _internal/ Directory Structure

```bash
mkdir clearflow/_internal
touch clearflow/_internal/__init__.py
```

### Step 2: Move Implementations to _internal/

Move and rename files:
- `node_interface.py` → `_internal/node_interface.py` (keep as NodeInterface)
- `message.py` → `_internal/message_impl.py`
- `message_node.py` → `_internal/node_impl.py`
- `message_flow.py` → `_internal/flow_impl.py`
- `callbacks.py` → `_internal/callbacks_impl.py`
- `strict_base_model.py` → `_internal/strict_base_model_impl.py`

Update internal imports within `_internal/`:
```python
# _internal/node_impl.py
from clearflow._internal.node_interface import NodeInterface  # No underscore!
from clearflow._internal.strict_base_model_impl import StrictBaseModelImpl
```

### Step 3: Create Public Wrapper Modules

Create thin wrapper modules at root:

```python
# clearflow/nodes.py
"""Nodes for ClearFlow orchestration."""
from clearflow._internal.node_impl import NodeImpl as _Node

__all__ = ["Node"]

class Node(_Node):
    """Base class for workflow nodes."""
    pass
```

```python
# clearflow/flows.py
"""Flow construction for ClearFlow."""
from clearflow._internal.flow_impl import flow as _flow

__all__ = ["flow"]

flow = _flow  # Direct re-export of function
```

Similar pattern for messages.py, callbacks.py, strict_base_model.py.

### Step 4: Update __init__.py to Re-export Only

```python
# clearflow/__init__.py
"""ClearFlow: Compose type-safe flows for emergent AI."""

from clearflow.callbacks import CallbackHandler, CompositeHandler
from clearflow.flows import flow
from clearflow.messages import Command, Event, Message
from clearflow.nodes import Node
from clearflow.strict_base_model import StrictBaseModel

__all__ = [
    "CallbackHandler",
    "Command",
    "CompositeHandler",
    "Event",
    "flow",
    "Message",
    "Node",
    "StrictBaseModel",
]
```

### Step 5: Update All Imports

Update test and example imports to use public API:
```python
# Instead of:
from clearflow.message import Message
from clearflow.message_node import Node

# Use:
from clearflow import Message, Node
# or
from clearflow.messages import Message
from clearflow.nodes import Node
```

### Step 6: Configure Linters

Add to `pyproject.toml`:
```toml
[tool.pyright]
reportPrivateImportUsage = "error"
reportPrivateUsage = "warning"

[tool.importlinter]
root_package = "clearflow"

[[tool.importlinter.contracts]]
name = "No external access to internals"
type = "forbidden"
sources = ["tests", "examples"]
forbidden = ["clearflow._internal"]
```

### Step 7: Add Boundary Tests

Create `tests/test_public_api.py` to verify API boundaries.

### Step 8: Documentation Updates

Update README.md and CLAUDE.md with new structure.

### Step 9: Final Quality Check

Run `./quality-check.sh` to ensure everything passes.

## Success Criteria

1. ✅ No linter warnings about private usage
2. ✅ Clear public/private boundary
3. ✅ All tests use public API only
4. ✅ All examples use public API only
5. ✅ NodeInterface is internal but usable within `_internal/`
6. ✅ Documentation reflects new structure

## Benefits After Migration

1. **Developer Experience**: Clear what's public vs private
2. **Maintainability**: Can refactor `_internal/` freely
3. **Documentation**: Each public module is a natural docs chapter
4. **Type Safety**: No ambiguity about what types are exposed
5. **Tool Support**: Linters and IDEs understand the boundaries