# Plan: Symmetric API and Union Terminal Types for complete_flow

## Overview

Improve the `complete_flow` API to be symmetric with `create_flow` and support union terminal types, making flows more expressive and consistent.

## Status: NOT STARTED

## Priority Considerations

- This is a non-breaking enhancement (existing code continues to work)
- Union support adds significant expressiveness to the framework
- API symmetry improves developer experience

## Implementation Tasks

### Task 1: Update FlowBuilder Abstract Interface
**Files**: `clearflow/flow.py`

1. Update `complete_flow` signature in abstract `FlowBuilder` class:
   - Rename `from_node` to `ending_node`
   - Rename generic parameters from `TFromIn/TFromOut` to `TEndIn/TEndOut`
   - Keep `final_outcome: type[TEnd]` parameter
   - Update docstring to reflect new naming

2. Run `./quality-check.sh clearflow/flow.py` - must pass 100%

**Success Criteria**:
- Abstract interface updated
- Type checking passes
- All quality checks pass for this file

### Task 2: Add Union Type Detection Helper
**Files**: `clearflow/_internal/flow_impl.py`

1. Add helper function `_extract_union_types()`:
   ```python
   def _extract_union_types(type_hint: type[Message]) -> tuple[type[Message], ...]:
       """Extract individual types from a union type or return single type."""
   ```
   - Handle `types.UnionType` (Python 3.10+ `X | Y` syntax)
   - Handle single types (return as single-element tuple)
   - Use `get_args()` from typing module

2. Run `./quality-check.sh clearflow/_internal/flow_impl.py` - must pass 100%

**Success Criteria**:
- Helper function added
- Handles both union and single types
- Quality checks pass

### Task 3: Update _FlowBuilder Implementation
**Files**: `clearflow/_internal/flow_impl.py`

1. Update `complete_flow` method in `_FlowBuilder`:
   - Rename `from_node` to `ending_node`
   - Rename generics to `TEndIn/TEndOut`
   - Use `_extract_union_types()` to handle union final_outcome
   - Create multiple terminal routes for union types
   - Update all references in method body

2. Update `_validate_and_create_route` calls:
   - Pass `ending_node` instead of `from_node`
   - Handle multiple route creation for unions

3. Update validation to ensure:
   - All types in union are valid outputs from ending_node
   - No duplicate terminal routes

4. Run `./quality-check.sh clearflow/_internal/flow_impl.py` - must pass 100%

**Success Criteria**:
- Implementation handles union types correctly
- Multiple terminal routes created for unions
- Type validation works for all cases
- Quality checks pass

### Task 4: Update Existing Tests
**Files**: `tests/test_flow.py`, `tests/test_observe.py`

1. Update all `complete_flow` calls:
   - No parameter changes needed (positional args stay same)
   - Verify tests still pass with new implementation

2. Run `./quality-check.sh tests/` - must pass 100%

**Success Criteria**:
- All existing tests pass
- No regressions
- 100% coverage maintained

### Task 5: Add Union Terminal Type Tests
**Files**: `tests/test_flow.py`

1. Add test `test_flow_union_terminal_types()`:
   - Create node with union output (e.g., `SuccessEvent | ErrorEvent`)
   - Use `complete_flow(node, SuccessEvent | ErrorEvent)`
   - Verify flow terminates on either type
   - Test type safety

2. Add test `test_flow_partial_union_terminal()`:
   - Node outputs `A | B | C`
   - Terminal only on `A | B` (not C)
   - Verify C needs routing, A and B terminate

3. Add test `test_invalid_union_terminal_type()`:
   - Try to mark types as terminal that node can't output
   - Should raise TypeError

4. Run `./quality-check.sh tests/test_flow.py` - must pass 100%

**Success Criteria**:
- New tests pass
- Union terminal types work correctly
- Type validation catches errors
- 100% coverage maintained

### Task 6: Update Type Validation
**Files**: `clearflow/_internal/flow_impl.py`

1. Update `_validate_route_types()`:
   - Handle validation when outcome is a union
   - Each type in union must be valid output from ending_node

2. Update `_validate_output_type()`:
   - Support checking union types against node outputs
   - All union members must be in valid outputs

3. Run `./quality-check.sh clearflow/_internal/flow_impl.py` - must pass 100%

**Success Criteria**:
- Validation handles unions correctly
- Clear error messages for invalid unions
- Quality checks pass

### Task 7: Documentation Updates
**Files**: `clearflow/flow.py`, `clearflow/_internal/flow_impl.py`

1. Update all docstrings:
   - Reflect new `ending_node` naming
   - Document union type support
   - Add examples with union terminals

2. Update inline comments:
   - Explain union handling logic
   - Document route creation for unions

3. Run `./quality-check.sh clearflow/` - must pass 100%

**Success Criteria**:
- Documentation accurate and complete
- Examples show union usage
- Quality checks pass

### Task 8: Integration Testing
**Files**: All test files

1. Run full test suite:
   - `./quality-check.sh` - must pass 100%
   - All tests pass
   - 100% coverage maintained
   - No linting issues
   - No type errors

2. Test examples still work:
   - Verify example flows work with changes
   - No breaking changes for users

**Success Criteria**:
- Full quality check passes
- All examples work
- No regressions

## Technical Details

### Union Type Handling

When `final_outcome` is a union (e.g., `A | B`):
1. Extract constituent types: `[A, B]`
2. Validate each type is in ending_node's outputs
3. Create terminal route for each: `(ending_node, A) -> None`, `(ending_node, B) -> None`
4. Flow type becomes `Node[TStartIn, A | B]`

### Route Storage

Routes stored as `tuple[RouteEntry, ...]` where:
- RouteEntry = `((node, message_type), destination)`
- Terminal routes have `destination = None`
- Multiple terminals supported via multiple entries

### Type Safety

- Pyright validates union types at build time
- Runtime validation ensures all union members are valid
- Clear error messages for type mismatches

## Risk Mitigation

1. **Backward Compatibility**: Existing single-type usage unchanged
2. **Type Safety**: All union types validated at runtime
3. **Performance**: Linear search still O(n) for small route tables
4. **Testing**: Comprehensive test coverage for all cases

## Success Metrics

-  API more symmetric and intuitive
-  Union terminal types fully supported
-  100% test coverage maintained
-  All quality checks pass
-  No breaking changes for existing users