# Development Plan

## Current Priority: Workspace Migration

### Immediate Issue to Resolve
- [ ] **Fix coverage regression**: Tests pass with 100% coverage in original structure but only 97% in workspace structure
  - Missing coverage in `clearflow/_internal/flow_impl.py` lines 32-33, 36, 42, 59-60, 63, 73
  - These are exception handlers and edge cases that were previously covered
  - Need to determine why moving to packages/ breaks this coverage

### Workspace Setup Tasks
- [x] Create root workspace pyproject.toml with shared dependencies
- [x] Move ClearFlow to packages/clearflow/
- [x] Move stigmergic-related docs and specs to packages/stigmergic/
- [x] Update quality-check.sh for workspace paths
- [x] Update GitHub workflows for multi-package support
- [ ] Resolve test coverage regression in workspace structure
- [ ] Create feature branch for workspace migration
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