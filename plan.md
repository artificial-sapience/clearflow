# Callback System Implementation Plan

## Overview

Replace the Observer pattern with an industry-standard Callback system that enables integration with observability platforms without affecting flow execution.

## Definition of Done

Each task is complete ONLY when `./quality-check.sh` passes 100% with zero violations and no suppressions.

## Phase 1: Core Implementation

### Task 1.1: Implement CallbackHandler Base Class
**Requirements**: REQ-001, REQ-002, REQ-003, REQ-004

1. Create `clearflow/callbacks.py` with:
   - Abstract `CallbackHandler` base class
   - Four lifecycle methods with default no-op implementations
   - Full type annotations using only stdlib types
   - Reference requirement numbers in comments

2. Update `clearflow/__init__.py`:
   - Add `CallbackHandler` to imports
   - Add to `__all__` list

3. Run `./quality-check.sh` - must pass 100%

### Task 1.2: Add Callback Support to MessageFlow Builder
**Requirements**: REQ-009, REQ-016

1. Update `clearflow/message_flow.py`:
   - Add `callbacks` field to `_MessageFlowBuilder`
   - Add `with_callbacks()` method to builder (returns builder)
   - Pass callbacks to `MessageFlow` in `end()` method
   - Reference requirement numbers in implementation

2. Update `MessageFlow` class:
   - Add optional `callbacks` field
   - Ensure zero overhead when callbacks is None (REQ-016)

3. Run `./quality-check.sh` - must pass 100%

### Task 1.3: Implement Callback Invocation in MessageFlow
**Requirements**: REQ-005, REQ-006, REQ-007, REQ-010, REQ-017

1. Update `MessageFlow.process()` method:
   - Add `_safe_callback()` helper method for error handling
   - Invoke `on_flow_start` at beginning
   - Invoke `on_node_start` before node execution
   - Invoke `on_node_end` after node execution
   - Invoke `on_flow_end` at termination
   - Ensure synchronous execution order (REQ-007)

2. Implement error handling:
   - Wrap all callback invocations in try-except
   - Log errors to stderr but don't propagate

3. Run `./quality-check.sh` - must pass 100%

## Phase 2: Advanced Features

### Task 2.1: Implement CompositeHandler
**Requirements**: REQ-008

1. Add `CompositeHandler` class to `callbacks.py`:
   - Accepts multiple handlers
   - Executes in registration order
   - Each handler's errors isolated

2. Run `./quality-check.sh` - must pass 100%

### Task 2.2: Support Nested Flow Callbacks
**Requirements**: REQ-011

1. Update flow composition logic:
   - When MessageFlow is used as a node
   - Propagate parent callbacks to nested flow
   - Maintain callback context through nesting

2. Run `./quality-check.sh` - must pass 100%

## Phase 3: Testing

### Task 3.1: Core Interface Tests
**Test Requirements**: REQ-001, REQ-002, REQ-003, REQ-004

1. Create `tests/test_callbacks.py`:
   - `test_callback_handler_interface()` - Verify abstract class and methods
   - `test_callback_default_noop()` - Verify default implementations
   - `test_callback_stdlib_only()` - Verify no external dependencies

2. Run `./quality-check.sh` - must pass 100%

### Task 3.2: Execution and Error Handling Tests
**Test Requirements**: REQ-005, REQ-006, REQ-007

1. Add to `tests/test_callbacks.py`:
   - `test_callback_error_handling()` - Errors don't affect flow
   - `test_callback_error_logging()` - Errors logged to stderr
   - `test_callback_execution_order()` - Verify lifecycle order

2. Run `./quality-check.sh` - must pass 100%

### Task 3.3: Integration Tests
**Test Requirements**: REQ-008, REQ-009, REQ-010, REQ-011

1. Add to `tests/test_callbacks.py`:
   - `test_composite_handler()` - Multiple handlers work
   - `test_flow_callback_integration()` - Callbacks invoked correctly
   - `test_nested_flow_callbacks()` - Propagation works

2. Run `./quality-check.sh` - must pass 100%

### Task 3.4: Type Safety and Performance Tests
**Test Requirements**: REQ-012, REQ-013, REQ-014, REQ-015, REQ-016, REQ-017, REQ-018

1. Add to `tests/test_callbacks.py`:
   - `test_no_node_modification()` - Existing nodes unchanged
   - `test_callback_type_safety()` - Types preserved
   - `test_callback_zero_overhead()` - No callbacks = no overhead
   - `test_callback_async_execution()` - Non-blocking
   - `test_callback_no_retention()` - No message references kept

2. Run `./quality-check.sh` - must pass 100%

## Phase 4: Migration

### Task 4.1: Remove Observer Pattern
**Clean up obsolete code**

1. Delete files:
   - `clearflow/observer.py`
   - `tests/test_observer.py`

2. Update `clearflow/__init__.py`:
   - Remove Observer imports
   - Remove from `__all__`

3. Run `./quality-check.sh` - must pass 100%

### Task 4.2: Update Examples with Callbacks
**Demonstrate callback usage**

1. Create `ConsoleHandler` in examples:
   - `examples/shared/console_handler.py`
   - Pretty-print message events to console

2. Update portfolio example:
   - Add ConsoleHandler for visibility
   - Show progress through specialist nodes

3. Update chat example:
   - Add simple logging handler
   - Demonstrate callback integration

4. Run `./quality-check.sh` - must pass 100%

## Phase 5: Documentation

### Task 5.1: Update Documentation
**Ensure all docs reflect new system**

1. Update relevant docstrings
2. Ensure examples in docs work
3. Run `./quality-check.sh` - must pass 100%

## Success Criteria

- All 18 requirements implemented and tested
- Zero dependencies added to core
- 100% test coverage maintained
- All examples updated and working
- `./quality-check.sh` passes for every task

## Risk Mitigation

- Each task is atomic and must pass quality checks
- Tests use only public API (no internal imports)
- Type safety verified by pyright strict mode
- No suppressions allowed without explicit approval