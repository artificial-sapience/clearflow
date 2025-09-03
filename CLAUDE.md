# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Philosophy

ClearFlow provides mission-critical AI orchestration for functional programming practitioners. Built for Python engineers who demand:
- **Deep immutability** - All state transformations create new immutable data structures
- **Functional purity** - Side effects isolated, transformations are pure functions
- **Type safety** - Full static typing with mypy/pyright strict mode
- **100% test coverage** - Every path tested, no exceptions
- **Explicit routing** - Given an outcome, the next step is always the same
- **Zero dependencies** - Stdlib only for maximum reliability

Target audience: Python engineers building mission-critical AI systems who embrace functional programming patterns and require provably correct orchestration.

## Development Commands

```bash
# Install dependencies
uv sync                    # Install runtime dependencies
uv sync --group dev        # Install with dev dependencies

# Run quality checks (enforced before commits)
./quality-check.sh         # Runs all checks: custom linters, lint, format, type check, tests

# Custom linters (mission-critical compliance)
python3 linters/check-architecture-compliance.py  # Architecture violations
python3 linters/check-immutability.py            # Deep immutability enforcement
python3 linters/check-test-suite-compliance.py   # Test isolation and resource management

# Individual quality commands
uv run ruff check --fix clearflow tests                 # Auto-fix linting (no unsafe fixes)
uv run ruff format clearflow tests                      # Format code
uv run mypy --strict clearflow tests                    # Type check (mypy)
uv run pyright clearflow tests                          # Type check (pyright) - TAKES PRECEDENCE
uv run pytest -x -v tests                              # Run all tests
uv run pytest -x -v tests -k "specific_test"           # Run specific test

# Coverage requirements
uv run pytest --cov=clearflow --cov-report=term-missing --cov-fail-under=100
```

## Architecture Overview

ClearFlow is a minimal orchestration framework with functional patterns and **zero third-party dependencies**. It implements a **Node-Flow-State** pattern for managing workflows that include language model calls and other async operations.

### Core Concepts

1. **Nodes**: Async functions that transform state
   - Inherit from `Node[T]` and override `exec()` method
   - Input: state of type `T` (any type: dict, TypedDict, dataclass, primitives)
   - Output: `NodeResult[T](state, outcome)`
   - Designed for explicit transformations
   - Lifecycle hooks: `prep()`, `exec()`, `post()`

2. **State**: Unconstrained - use any type T
   - Type-safe with `T` where T is any Python type
   - Natural Python operations: `{**state, "key": "value"}`
   - Encourages immutable patterns
   - Works with dict, TypedDict, dataclass, primitives

3. **Flow**: Type-safe workflow builder
   - Single termination rule: exactly one route to `None`
   - Trustworthy orchestration with full generic support
   - Build-time validation of flow structure

### Key Facts

- **Code size**: <200 lines (currently 188)
- **Test coverage**: 100% required
- **Type safety**: No `Any` or `type: ignore` allowed
- **Immutability**: All dataclasses frozen
- **Routing**: Explicit (NOT deterministic execution)
- **Single termination**: Exactly one route to `None` per flow

### Common Patterns

```python
# Creating nodes with OO approach
class DocumentLoader(Node[DocumentState]):
    def __init__(self) -> None:
        super().__init__(name="loader")
    
    async def exec(self, state: DocumentState) -> NodeResult[DocumentState]:
        content = await load_document(state["path"])
        new_state: DocumentState = {**state, "content": content}
        return NodeResult(new_state, outcome="loaded")

# Building a flow with single termination
complete = CompleteNode()  # Convergence point

flow = (
    Flow[DocumentState]("Pipeline")
    .start_with(loader)
    .route(loader, "loaded", processor)
    .route(loader, "error", complete)
    .route(processor, "processed", complete)
    .route(complete, "done", None)  # Single termination
    .build()
)
```

### Testing Requirements

- **100% coverage**: No exceptions, ever
- **Deep immutability**: Use frozen dataclasses or tuples for all test state
- **Real AI scenarios**: Model actual AI orchestration patterns (RAG, agents, tool use)
- **Functional purity**: Test that transformations are pure with no side effects
- **Precise types**: Every test knows exact TIn and TOut types
- **Educational tests**: Tests should demonstrate best practices for mission-critical AI

### Code Quality Standards

**CRITICAL**: These standards maintain trust:
- All linting rules must pass without suppression
- Both mypy and pyright must pass in strict mode
- **Pyright takes precedence** when tools conflict
- No `type: ignore` comments in core library code
- No `Any` types where proper types can be used
- Prefer boring, obvious code over clever solutions

**LINTER SUPPRESSION POLICY**:
- **NEVER add linter suppressions without explicit user approval**
- This includes: `# noqa`, `# type: ignore`, `# pyright: ignore`, etc.
- All approved suppressions MUST include a justification comment
- Example: `# noqa: C901  # Display function complexity acceptable for UI`
- Always fix the root cause instead of suppressing when possible

#### Custom Linters

ClearFlow uses three custom linters to enforce mission-critical standards:

1. **Architecture Compliance** (`linters/check-architecture-compliance.py`)
   - No patching/mocking of internal components in tests
   - No imports from private modules (`_internal`)
   - No use of `TYPE_CHECKING` (indicates circular dependencies)
   - No `object` or `Any` types in parameters

2. **Immutability Compliance** (`linters/check-immutability.py`)
   - All dataclasses must have `frozen=True`
   - No `list` in type annotations (use `tuple[T, ...]`)
   - No mutable default arguments
   - No list building with `.append()` in production code

3. **Test Suite Compliance** (`linters/check-test-suite-compliance.py`)
   - No `asyncio.run()` in tests (use `@pytest.mark.asyncio`)
   - No manual event loop creation without cleanup
   - All async tests must have `@pytest.mark.asyncio`
   - All resources must use context managers

These linters run automatically as part of `./quality-check.sh` and enforce zero-tolerance policies for violations.

### Contributing Guidelines

1. **PR Standards**
   - Must maintain 100% test coverage
   - Must pass all type checks
   - Must use frozen dataclasses
   - Must handle all outcomes explicitly

2. **Documentation**
   - Focus on guarantees and limitations
   - No marketing language
   - Examples must work exactly as shown
   - Be explicit about what we don't do

3. **Feature Requests**
   - Reject anything that compromises type safety
   - Reject anything that reduces testability
   - Reject anything that adds implicit behavior
   - "No" is a complete answer

### Documentation Style

**CRITICAL**: All documentation must be:
- **Factual and concise** - No verbosity or repetition
- **Free of "we/our" language** - Use neutral technical language
- **Focused on what matters** - Essential information only
- **Proportional** - Documentation should be shorter than the code (200 lines)
- **Ego-free** - No defensiveness, no overselling, no anxiety

Examples:
- ❌ "We provide trustworthy orchestration for mission-critical systems"
- ✅ "Reliable language model orchestration. Type-safe with 100% test coverage."
- ❌ "Our philosophy is trust through proof"
- ✅ "100% test coverage required"
- ❌ "This guide explains how to create high-quality examples"
- ✅ "Creating Examples"

**Documentation Smell Test**:
If documentation sounds anxious, defensive, or like it's trying to impress, rewrite it.
Good documentation states facts without emotion.

When responding to users:
- Be direct and factual
- State limitations without defensiveness
- Use technical language, not marketing speak
- Keep responses concise
- Don't explain why you can't do something (preachy)

### Red Flags to Avoid

1. **Never claim**:
   - "Deterministic orchestration" or "deterministic execution" (we only provide explicit routing)
   - "Exhaustive outcome handling" (we don't enforce this)
   - "Compile-time safety" (Python doesn't have this)
   - "Makes language model agents reliable" (we only provide orchestration structure)
   - "Production-ready agents" (we provide orchestration, not complete agents)
   - "You can't test LLM outputs" (you can test them, just not deterministically)

2. **Never add**:
   - Claims about execution order or timing guarantees
   - Methods that hide what happens between node calls
   - Optional parameters that change flow behavior
   - Dependencies that could introduce unpredictability

3. **Language to avoid**:
   - "Deterministic" when describing the framework (use "explicit routing" instead)
   - "Unreasonable AI" or other hyperbolic characterizations of LLMs
   - Absolute statements about what users can't do
   - Marketing language that can't be verified

### Before Any Change

Ask:
- Can this be tested completely?
- Does this make behavior more explicit?
- Is this simpler than the alternative?

If any answer is "no", don't do it.

### Git Workflow

1. **Branch Protection**: Main branch requires PR with passing checks
2. **Conventional Commits**: Use `fix:`, `feat:`, `docs:`, `ci:` prefixes
3. **Local Protection**: Pre-commit hook prevents direct commits to main
4. **PR Process**:
   ```bash
   git checkout -b type/description
   # Make changes
   ./quality-check.sh
   git commit -m "type: clear description"
   git push -u origin type/description
   gh pr create --title "type: description" --body "concise explanation"
   ```

## Remember

ClearFlow provides explicit routing with single termination enforcement. Keep the code minimal, the documentation concise, and the claims verifiable.

## Documentation Size Limits

ClearFlow is ~166 lines. Documentation should be proportional:
- README.md: Keep concise but complete (~200 lines is reasonable for user-facing docs)
- CONTRIBUTING.md: <50 lines  
- Individual docs: <100 lines
- Total documentation: <500 lines

Balance completeness with conciseness. The README needs to properly onboard users while staying focused.

## Release Process

ClearFlow uses automated release management:

1. **Version Management**: GitVersion calculates versions based on git history
2. **Draft Releases**: Release Drafter maintains draft with changelog from PR merges
3. **Publishing**: Manual trigger of release.yml workflow:
   - Builds package with calculated version
   - Creates git tag
   - Publishes to PyPI via trusted publisher
   - Converts draft to published GitHub release

**Known Issues**:
- Draft release IDs can become stale - always fetch fresh by tag name
- PyPI trusted publisher requires exact workflow path match
- Version must be updated in pyproject.toml before building

**PyPI Package**: https://pypi.org/project/clearflow/

## Critical Technical Distinction

**Explicit routing ≠ Deterministic execution**

ClearFlow provides explicit routing (given outcome X, next step is always Y) but NOT deterministic execution (nodes execute arbitrary async code with unpredictable timing).

Always use precise technical terms. Users are engineers who will verify claims.

## Lessons Learned

1. **Documentation debt is real** - A 200-line library had 783 lines of docs (reduced to 150)
2. **Ego leaks into docs** - Watch for defensive language, "we/our", trying to sound important
3. **Less is more** - If you can say it in 20 lines instead of 100, do it
4. **Show, don't tell** - Code examples > philosophical manifestos
5. **Trust the code** - A well-written 200-line library doesn't need 450-line guides
6. **Be boring** - Boring, obvious code and docs are better than clever ones