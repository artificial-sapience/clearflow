# ClearFlow Development Plan

## Current Branch: `support-state-type-transformations`

## Immediate Priority Tasks

### 1. Fix Dependency Conflicts 🚨
- [ ] Resolve rich version conflict (dspy wants >=13.7.1, semgrep wants <13.6)
- [ ] Update ALL dependencies to latest stable versions (2025 versions)
- [ ] Test that all examples work with updated dependencies
- [ ] Ensure pyright finds dependencies correctly with new structure

### 2. Complete RAG Example
- [ ] Fix remaining pyright type errors in RAG example
- [ ] Add type stubs for numpy/openai if needed (or rely on built-in types)
- [ ] Ensure RAG example passes all quality checks
- [ ] Test RAG example with actual API calls

### 3. Finalize Dependency Organization
- [ ] Verify each example's pyproject.toml is complete
- [ ] Consider if examples should depend on local clearflow or PyPI version
- [ ] Update example READMEs with new installation instructions
- [ ] Document the new structure in CLAUDE.md

### 4. Final PR Preparation 📋
- [ ] Run full quality-check.sh on entire codebase
- [ ] Create detailed PR description including:
  - Type transformation support
  - Flow builder validation
  - Custom linters
  - Portfolio example refactoring (agents → specialists)
  - RAG example addition
  - Dependency reorganization with pyproject.toml
  - Badge additions
- [ ] Submit PR for review

## Future Considerations
- Add timeout and max iterations support to flow execution
- Create more examples following different design patterns
- Consider documentation site when project grows