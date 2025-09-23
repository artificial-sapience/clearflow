# Development Plan

## Current Priority: Complete Coverage Fix

### Immediate Tasks
- [x] Added `branch = true` to workspace coverage config
- [x] Removed defensive exception handlers from type validation
- [ ] **Achieve 100% coverage**: Currently at 98% with 4 lines uncovered
  - Lines 33, 39: Handle missing type hints and TypeVars in output validation
  - Lines 57, 67: Handle missing type hints and Union types in input validation
  - Decision needed: Remove these edge cases entirely or add tests for them
  - Philosophy: Enforce strict typing (fail fast) vs allow flexibility for generic nodes

### Final Workspace Migration Steps
- [ ] Push coverage fix to stigmergic-mvp branch
- [ ] Ensure CI passes with workspace structure
- [ ] Merge workspace migration to main

## Stigmergic System Development

### Phase 0: Formal Specification (Current)
- [x] Move Lean4 specification standards to stigmergic package
- [x] Create placeholder Python structure
- [ ] Complete Lean4 formal specification per lean4-spec-standard/
- [ ] Prove key properties and theorems
- [ ] Define interface contracts mathematically

### Phase 1: MVP Foundation (After Specification)
- [ ] Implement core Trace dataclass based on Lean4 spec
- [ ] Implement minimal Environment with trace storage
- [ ] Create StigmergicAgent base class with DSPy integration
- [ ] Add simple keyword-based attraction mechanism
- [ ] Create test suite with 100% coverage requirement
- [ ] Implement basic goal injection interface
- [ ] Add simple completion detection

### Phase 2: DSPy Integration
- [ ] Configure DSPy with appropriate LLM backends
- [ ] Implement ChainOfThought signatures for agent decisions
- [ ] Create role-specific agent templates
- [ ] Add DSPy-based trace generation
- [ ] Implement basic feedback collection
- [ ] Create DSPy optimization pipeline

### Future Phases
See original plan.md for Phases 3-6 details once MVP is complete.

## Success Criteria
- Workspace structure with two independent packages
- 100% test coverage maintained for ClearFlow
- Stigmergic package follows Lean4-first approach
- Both packages pass quality-check.sh
- Independent PyPI releases for each package