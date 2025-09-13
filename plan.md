# ClearFlow Architecture Migration Plan

## 🚀 Phase 2: Complete Migration to Message-Driven Architecture

**Status**: Phase 1 Complete ✅ - Message-driven architecture implemented with 88/88 tests passing

**Critical Issue**: Portfolio example lost LLM intelligence - using hardcoded logic instead of DSPy/OpenAI

### Priority Tasks (Critical - Next Session)

#### 1. 🔴 Fix Portfolio Example LLM Integration
**CRITICAL**: The message-driven portfolio example has completely lost the LLM intelligence from the original
- **Problem**: Currently uses `secrets.SystemRandom()` instead of DSPy/OpenAI
- **Required**: Restore full LLM intelligence using DSPy signatures and OpenAI calls
- **Tasks**:
  - Copy `shared/` directory with DSPy config from original example
  - Copy all `*/signature.py` files for DSPy signatures
  - Rewrite all nodes to use `dspy.Predict()` with proper signatures
  - Add `.env.example` with OPENAI_API_KEY placeholder
  - Test with real OpenAI API to verify LLM calls work

#### 2. Complete Quality Compliance for Portfolio Example
- Fix all relative imports (partially done - needs verification)
- Add "Returns" sections to all docstrings (DOC201 violations)
- Remove magic values - already added constants but needs verification
- Fix exception handling to catch specific exceptions
- Ensure 100% quality check pass rate

### Remaining Phase 2 Tasks

#### 3. Remove Legacy Architecture
- Remove Node-Flow-State from `clearflow/__init__.py`
- Remove legacy tests from `tests/` directory
- Maintain 100% coverage with message-driven tests only

#### 4. Update Documentation
- Update README.md for message-driven architecture only
- Create MIGRATION.md for users transitioning from legacy
- Update all code examples in docs to use message-driven

#### 5. Release v1.x with Message-Driven Only
- Minor version bump (not v2.0) justified by Alpha status
- Announce breaking change in release notes
- Update PyPI package

### Quality Standards (Enforced)
- **100% test coverage** via public API only
- **Grade A complexity** across all code
- **Zero pyright errors**
- **ALL code** (examples, tests, docs) must meet mission-critical standards
- **No relative imports** anywhere in codebase
- **No suppressions** without explicit user approval