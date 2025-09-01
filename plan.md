# ClearFlow Type Transformation Implementation Plan

## Overview
Transform ClearFlow from supporting only `Node[T]` to supporting type-transforming nodes `Node[TIn, TOut]`. This is a breaking change with no backwards compatibility.

## Phase 1: Core Type System Updates

### Task 1.1: Update Type Variables
**File**: `clearflow/__init__.py`
- [ ] Add `TIn = TypeVar("TIn")` at module level
- [ ] Add `TOut = TypeVar("TOut")` at module level
- [ ] Keep existing `T = TypeVar("T")` for backwards naming

### Task 1.2: Update Node Class
**File**: `clearflow/__init__.py`
- [ ] Change `class Node[T](ABC)` to `class Node[TIn, TOut](ABC)`
- [ ] Update `__call__` signature: `async def __call__(self, state: TIn) -> NodeResult[TOut]`
- [ ] Update `prep` signature: `async def prep(self, state: TIn) -> TIn`
- [ ] Update `exec` signature: `async def exec(self, state: TIn) -> NodeResult[TOut]`
- [ ] Update `post` signature: `async def post(self, result: NodeResult[TOut]) -> NodeResult[TOut]`
- [ ] Update docstring to explain transformation capability

### Task 1.3: Update NodeResult
**File**: `clearflow/__init__.py`
- [ ] Verify `NodeResult[T]` works with new `TOut` type
- [ ] No changes needed - already generic

## Phase 2: Flow Implementation Updates

### Task 2.1: Update _Flow Class
**File**: `clearflow/__init__.py`
- [ ] Change `class _Flow(Node[T])` to `class _Flow[TIn, TOut](Node[TIn, TOut])`
- [ ] Change `start_node: Node[T]` to `start_node: object`
- [ ] Change `routes: Mapping[RouteKey, Node[T] | None]` to `routes: Mapping[RouteKey, object | None]`
- [ ] Update `exec` signature to handle TIn→TOut
- [ ] Add type casting at return boundary: `cast(NodeResult[TOut], result)`
- [ ] Add comprehensive docstring explaining why `object` is used internally

### Task 2.2: Update _StartedWithFlow Class
**File**: `clearflow/__init__.py`
- [ ] Change to track input and current output types: `class _StartedWithFlow[TIn, TCurrent]`
- [ ] Update `_start: Node[T]` to `_start: object`
- [ ] Update `_routes` to use `object`
- [ ] Update `route` method to accept `object` for nodes
- [ ] Update `build` method to return `Node[TIn, Any]` (output type dynamic)

### Task 2.3: Update Flow Builder Class
**File**: `clearflow/__init__.py`
- [ ] Change `class Flow[T]` to `class Flow[TIn, TOut]`
- [ ] Update `start_with` to accept any compatible node
- [ ] Return appropriate builder type from `start_with`
- [ ] Update docstrings to explain usage

## Phase 3: Testing

### Task 3.1: Create Type Transformation Tests
**File**: `tests/test_type_transformation.py` (new)
- [ ] Test simple transformation: `Node[A, B]`
- [ ] Test identity transformation: `Node[A, A]`
- [ ] Test pipeline: A→B→C→D
- [ ] Test branching with different types
- [ ] Test error cases (ensure no defensive code needed)
- [ ] Test with real-world example (e.g., document processing)

### Task 3.2: Update Existing Tests
**File**: `tests/test_clearflow.py`
- [ ] Update all `Node[T]` to `Node[T, T]` for non-transforming nodes
- [ ] Ensure all tests still pass
- [ ] Add backwards compatibility tests if needed

### Task 3.3: Integration Test with Sociocracy Pattern
**File**: `tests/test_sociocracy_pattern.py` (new)
- [ ] Create PreSynthesisState and PostSynthesisState types
- [ ] Create SynthesizeNode[PreSynthesisState, PostSynthesisState]
- [ ] Build flow with type transformation
- [ ] Verify no isinstance checks needed
- [ ] Ensure 100% coverage

## Phase 4: Documentation

### Task 4.1: Update README
**File**: `README.md`
- [ ] Add type transformation examples
- [ ] Explain Node[TIn, TOut] vs Node[T, T]
- [ ] Add real-world usage patterns
- [ ] Document breaking changes

### Task 4.2: Update Inline Documentation
**File**: `clearflow/__init__.py`
- [ ] Add detailed docstrings explaining object usage
- [ ] Document type transformation patterns
- [ ] Add examples in docstrings

### Task 4.3: Create Migration Guide
**File**: `MIGRATION.md` (new)
- [ ] Document breaking changes
- [ ] Provide before/after examples
- [ ] Explain benefits of new design
- [ ] Show how to update existing code

## Phase 5: Examples

### Task 5.1: Create Type Transformation Example
**File**: `examples/type_transformation/` (new)
- [ ] Create document processing pipeline example
- [ ] Show RawDocument→ParsedDoc→EnrichedDoc→IndexedDoc
- [ ] Demonstrate type safety without isinstance

### Task 5.2: Update Existing Examples
**Files**: `examples/*/`
- [ ] Update to use Node[T, T] syntax
- [ ] Ensure all examples still work
- [ ] Add comments explaining the type signatures

## Phase 6: Quality Assurance

### Task 6.1: Create Quality Check Script
**File**: `quality-check.sh` (new)
- [ ] Copy from Sociocracy and adapt
- [ ] Include mypy strict checks
- [ ] Include pyright checks
- [ ] Include ruff checks
- [ ] Include test coverage requirements

### Task 6.2: Update pyproject.toml
**File**: `pyproject.toml`
- [ ] Add mypy configuration (strict mode)
- [ ] Add pyright configuration
- [ ] Add ruff configuration
- [ ] Ensure no suppressions allowed

### Task 6.3: Run Full Quality Checks
- [ ] Run mypy --strict
- [ ] Run pyright
- [ ] Run ruff check
- [ ] Run ruff format
- [ ] Ensure 100% test coverage
- [ ] Fix any issues found

## Phase 7: Final Validation

### Task 7.1: Sociocracy Integration Test
- [ ] Update Sociocracy to use new ClearFlow
- [ ] Remove isinstance checks from SynthesizeNode
- [ ] Verify quality checks pass
- [ ] Ensure no defensive code needed

### Task 7.2: Performance Validation
- [ ] Benchmark before and after changes
- [ ] Ensure no performance regression
- [ ] Document any performance differences

### Task 7.3: Release Preparation
- [ ] Update version in pyproject.toml
- [ ] Create changelog entry
- [ ] Tag release
- [ ] Prepare release notes

## Success Criteria

1. ✅ All nodes can specify `Node[TIn, TOut]` for transformations
2. ✅ Flows handle type transformations without isinstance checks
3. ✅ 100% test coverage maintained
4. ✅ Zero type suppressions (`# type: ignore`)
5. ✅ All quality checks pass (mypy, pyright, ruff)
6. ✅ Sociocracy integration works without defensive code
7. ✅ Documentation clearly explains the design
8. ✅ Real-world examples demonstrate value

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing code | No backwards compatibility by design - clean break |
| Type checker confusion | Clear documentation about internal `object` usage |
| Performance impact | Benchmark and optimize if needed |
| User confusion | Comprehensive examples and migration guide |

## Timeline Estimate

- Phase 1-2 (Core Updates): 2-3 hours
- Phase 3 (Testing): 2-3 hours  
- Phase 4-5 (Documentation/Examples): 2 hours
- Phase 6 (Quality): 1-2 hours
- Phase 7 (Validation): 1-2 hours

**Total: 8-13 hours of focused work**

## Notes

- This is a breaking change - no backwards compatibility
- Internal use of `object` is intentional and documented
- Focus on type safety at public API boundaries
- Ensure Sociocracy benefits from these changes