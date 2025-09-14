# Callback System Implementation Plan

## Overview

Replace the Observer pattern with an industry-standard Callback system that enables integration with observability platforms without affecting flow execution.

**Status**: Callback system fully implemented and functional. Observer pattern pending removal.

## Definition of Done

Each task is complete ONLY when `./quality-check.sh` passes 100% with zero violations and no suppressions for all files created, updated, or affected by the task.

## ✅ Phase 1: Core Implementation - COMPLETED

All Phase 1 tasks completed. CallbackHandler base class implemented with proper error handling and integrated into MessageFlow.

## ✅ Phase 2: Advanced Features - COMPLETED

### Task 2.1: Implement CompositeHandler - COMPLETED ✅

**Requirements**: REQ-008
**Status**: COMPLETED ✅

1. Added `CompositeHandler` class to `callbacks.py`:
   - Accepts multiple handlers
   - Executes in registration order
   - Each handler's errors isolated

2. `./quality-check.sh clearflow/callbacks.py` - passes 100%

### Task 2.2: Support Nested Flow Callbacks - COMPLETED ✅

**Requirements**: REQ-011
**Status**: COMPLETED ✅

1. Update flow composition logic:
   - When MessageFlow is used as a node
   - Propagate parent callbacks to nested flow
   - Maintain callback context through nesting

2. Run `./quality-check.sh clearflow/message_flow.py` - must pass 100%

## Phase 3: Testing

### Task 3.1: Core Interface Tests

**Test Requirements**: REQ-001, REQ-002, REQ-003, REQ-004
**Status**: COMPLETED ✅

1. Create `tests/test_callbacks.py`:
   - `test_callback_handler_interface()` - Verify base class and methods
   - `test_callback_default_noop()` - Verify default implementations
   - `test_callback_stdlib_only()` - Verify no external dependencies

2. Run `./quality-check.sh tests/test_callbacks.py` - must pass 100%

### Task 3.2: Execution and Error Handling Tests - COMPLETED ✅

**Test Requirements**: REQ-005, REQ-006, REQ-007
**Status**: COMPLETED ✅

1. Added to `tests/test_callbacks.py`:
   - `test_callback_error_handling()` - Errors don't affect flow
   - `test_callback_error_logging()` - Errors logged to stderr
   - `test_callback_execution_order()` - Verify lifecycle order

2. `./quality-check.sh tests/test_callbacks.py` - passes 100%

### Task 3.3: Integration Tests - COMPLETED ✅

**Test Requirements**: REQ-008, REQ-009, REQ-010, REQ-011
**Status**: COMPLETED ✅

1. Added to `tests/test_callbacks.py`:
   - `test_composite_handler()` - Multiple handlers work
   - `test_composite_handler_error_isolation()` - Error isolation verified
   - `test_flow_callback_integration()` - Callbacks invoked correctly
   - `test_nested_flow_callbacks()` - Propagation works

2. `./quality-check.sh tests/test_callbacks.py` - passes 100%

### Task 3.4: Type Safety and Performance Tests - COMPLETED ✅

**Test Requirements**: REQ-012, REQ-013, REQ-014, REQ-015, REQ-016, REQ-017, REQ-018
**Status**: COMPLETED ✅

1. Added to `tests/test_callbacks.py`:
   - `test_no_node_modification()` - Existing nodes unchanged
   - `test_callback_type_safety()` - Types preserved
   - `test_callback_zero_overhead()` - No callbacks = no overhead
   - `test_callback_async_execution()` - Non-blocking
   - `test_callback_no_retention()` - No message references kept
   - `test_composite_handler_error_logging()` - CompositeHandler error paths
   - `test_callback_on_node_error()` - Node error path coverage

2. `./quality-check.sh` - passes 100% with 100% test coverage

## Phase 4: Migration

### Task 4.1: Remove Observer Pattern

**Status**: Not started
**Dependencies**: All Phase 1-3 tasks must be complete

1. Delete files:
   - `clearflow/observer.py`
   - `tests/test_observer.py`

2. Update `clearflow/__init__.py`:
   - Remove Observer imports
   - Remove from `__all__`

3. Run `./quality-check.sh clearflow tests` - must pass 100% (full suite after deletion)

### Task 4.2: Update Examples with Callbacks

**Status**: Not started
**Dependencies**: Task 4.1 must be complete

1. Create `ConsoleHandler` in examples:
   - `examples/shared/console_handler.py`
   - Pretty-print message events to console

2. Update portfolio example:
   - Add ConsoleHandler for visibility
   - Show progress through specialist nodes

3. Update chat example:
   - Add simple logging handler
   - Demonstrate callback integration

4. Run `./quality-check.sh examples` - must pass 100%

## Phase 5: Documentation

### Task 5.1: Update Documentation

**Status**: Not started
**Dependencies**: All Phase 1-4 tasks must be complete

1. Update relevant docstrings
2. Ensure examples in docs work
3. Run `./quality-check.sh` - must pass 100% (full project check)

## Success Criteria

- All 18 requirements implemented and tested ✅
- Zero dependencies added to core ✅
- 100% test coverage maintained ✅
- All examples updated and working (pending Phase 4)
- `./quality-check.sh` passes for every task ✅

## Risk Mitigation

- Each task is atomic and must pass quality checks
- Tests use only public API (no internal imports)
- Type safety verified by pyright strict mode
- No suppressions allowed without explicit approval

## Completed Work (Previous Sessions)

### Message Flow API Redesign ✅

- Implemented explicit source node routing pattern
- Changed from `.from_node().route()` to `.route(from_node, outcome, to_node)`
- Used type erasure for flexible union type handling
- Updated all tests and examples
- Documented the API changes and design rationale

### Chat Example Improvements ✅

- Fixed UserNode complexity (Grade B to A)
- Renamed AssistantMessageSent to AssistantMessageReceived for symmetry
- Simplified proxy node pattern documentation

### Callback System Implementation ✅ (Current Session)

- Implemented CallbackHandler base class with 4 lifecycle methods
- Added CompositeHandler for multiple callback support with error isolation
- Integrated callbacks into MessageFlow with zero overhead when disabled
- Added 17 comprehensive tests covering all 18 requirements
- Achieved 100% test coverage for callback system
- All quality checks pass (linting, formatting, type checking, complexity)
