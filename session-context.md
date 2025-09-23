# Session Context: Coverage Fix and Philosophy Clarification

## Session Summary
We discovered and partially fixed a test coverage regression in the workspace structure, going from 97% to 98% coverage. The session revealed important philosophical questions about defensive programming vs fail-fast principles in ClearFlow.

## Technical Discoveries

### Coverage Regression Root Causes
1. **Missing `branch = true`**: The workspace pyproject.toml was missing branch coverage tracking
2. **Statement Count Difference**: Coverage.py counts 151 statements on workspace branch vs 116 on main
   - The files are identical - the difference is in how coverage counts statements
   - Likely includes docstrings or other non-executable lines differently
3. **Untested Defensive Code**: Exception handlers for invalid type hints were never tested

### Code Changes Made
1. **Added `branch = true` to `/pyproject.toml`** (committed)
2. **Removed try-except blocks from `_get_node_output_types`**
3. **Removed try-except blocks from `_get_node_input_types`**

### Current Coverage Status
- **98% coverage** with 4 lines uncovered in `flow_impl.py`:
  - Line 33: `return ()` when "return" not in hints
  - Line 39: `return ()` for TypeVar generic parameters
  - Line 57: `return ()` when "message" not in hints
  - Line 67: `return get_args(return_type)` for Union types

## Philosophical Decision Point

### Your Stated Principles
1. "We must remove dead code and defensive programming"
2. "We must fail fast unless this code is with regard to observability"
3. "We do want coverage of all lines of code including exception handlers"
4. "We do not want to count documentation as lines of code"

### The Decision: Strict Typing (Fail Fast)
**Decision made**: ClearFlow will enforce strict typing on all nodes.

**Rationale**:
- Aligns with "fail fast" principle
- Removes all defensive programming
- Ensures type safety throughout the system
- Achieves 100% coverage by removing untestable defensive code

**Implementation**:
- Remove all edge case handling for missing type hints
- Remove TypeVar special handling
- Any node without complete, concrete type annotations will cause immediate failure
- This means no generic nodes with TypeVars - all types must be concrete

## Technical Context

### Workspace Structure
- ClearFlow moved to `packages/clearflow/`
- Stigmergic placeholder at `packages/stigmergic/`
- Working on branch `stigmergic-mvp`
- All tests pass with current changes

### What TypeVar Handling Enables
```python
T = TypeVar('T')
class GenericNode(Node[T, T]):
    # This node works with any message type
    def process(self, message: T) -> T:
        return message
```

Without TypeVar handling, generic nodes would fail validation. This might be desirable (enforce concrete types) or problematic (lose flexibility).

## Next Steps
See `plan.md` for detailed task list. The immediate priority is deciding on the typing philosophy and achieving 100% coverage accordingly.