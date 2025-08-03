# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Philosophy: Trust Through Proof

ClearFlow provides trustworthy orchestration with predictable routing for LLM-powered agents. We focus on what we can actually guarantee:
- **100% test coverage** is non-negotiable for the orchestration code
- **Type safety** with mypy/pyright strict mode is mandatory
- **Immutability** is enforced to track state between LLM calls
- **Explicit is better than implicit** - every route and transformation is visible
- **Predictable orchestration** - given an outcome, the next step is always the same (but NOT deterministic execution)

Our target audience: Engineers building LLM-powered agents who need at least one layer they can fully test and trust.

## Development Commands

```bash
# Install dependencies
uv sync                    # Install runtime dependencies
uv sync --group dev        # Install with dev dependencies

# Run quality checks (enforced before commits)
./quality-check.sh         # Runs all checks: lint, format, type check, tests

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

ClearFlow is a minimal orchestration framework with functional patterns and **zero third-party dependencies**. It implements a **Node-Flow-State** pattern for managing workflows that include LLM calls and other async operations.

### Core Concepts

1. **Nodes**: Async functions that transform state
   - Inherit from `Node[T]` and override `exec()` method
   - Input: `State[T]`
   - Output: `NodeResult[T](state, outcome)`
   - Designed for predictable transformations
   - Lifecycle hooks: `prep()`, `exec()`, `post()`

2. **State**: Generic state container with functional API
   - Type-safe with `State[T]` where T is user-defined
   - `transform()` method encourages creating new state instances
   - All types are frozen (immutable)
   - Works with standard Python data structures

3. **Flow**: Type-safe workflow builder
   - Single termination rule: exactly one route to `None`
   - Trustworthy orchestration with full generic support
   - Build-time validation of flow structure

### What Makes ClearFlow Trustworthy

1. **Verifiable Claims**
   - <200 lines of auditable orchestration code (188 lines exactly)
   - 100% test coverage of the framework
   - No `Any` or `type: ignore` in framework code
   - All types frozen with `@dataclass(frozen=True)`

2. **Predictable Routing** (NOT deterministic execution)
   - Single termination rule: exactly one endpoint
   - Static orchestration table - given an outcome, next step is predictable
   - Build-time validation catches flow structure errors
   - But nodes can do anything - we don't control execution

3. **Honest Communication**
   - We provide orchestration structure, not execution guarantees
   - Clear boundaries: orchestration logic vs node behavior
   - No promises about timing, ordering, or external service behavior

### Common Patterns

```python
# Creating nodes with OO approach
class DocumentLoader(Node[DocumentState]):
    def __init__(self) -> None:
        super().__init__(name="loader")
    
    async def exec(self, state: State[DocumentState]) -> NodeResult[DocumentState]:
        content = await load_document(state.data["path"])
        new_state = state.transform(lambda d: {**d, "content": content})
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
- **Test all outcomes**: Every node outcome must have a test
- **Verify immutability**: Test that state transformations don't mutate
- **Domain-relevant**: Use real LLM/agent scenarios, not foo/bar

### Code Quality Standards

**CRITICAL**: These standards maintain trust:
- All linting rules must pass without suppression
- Both mypy and pyright must pass in strict mode
- **Pyright takes precedence** when tools conflict
- No `type: ignore` comments in core library code
- No `Any` types where proper types can be used
- Prefer boring, obvious code over clever solutions

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

### Communication Style

When responding to users:
- Be direct and honest
- Acknowledge limitations upfront
- No false promises about capabilities
- Focus on verifiable facts
- Remember: our users value truth over comfort

### Red Flags to Avoid

1. **Never claim**:
   - "Deterministic orchestration" or "deterministic execution" (we only provide predictable routing)
   - "Exhaustive outcome handling" (we don't enforce this)
   - "Compile-time safety" (Python doesn't have this)
   - "Makes LLM agents reliable" (we only provide orchestration structure)
   - "Production-ready agents" (we provide orchestration, not complete agents)
   - "You can't test LLM outputs" (you can test them, just not deterministically)

2. **Never add**:
   - Claims about execution order or timing guarantees
   - Methods that hide what happens between node calls
   - Optional parameters that change flow behavior
   - Dependencies that could introduce unpredictability

3. **Language to avoid**:
   - "Deterministic" when describing the framework (use "predictable routing" instead)
   - "Unreasonable AI" or other hyperbolic characterizations of LLMs
   - Absolute statements about what users can't do
   - Marketing language that can't be verified

### The Trust Test

Before any change, ask:
- Can we prove this works correctly?
- Does this make behavior more predictable?
- Will our target users trust this?
- Can we test this completely?

If any answer is "no", don't do it.

## Remember

Our users chose ClearFlow because they need at least one layer of their LLM agent stack they can trust. We provide predictable routing and immutable state - nothing more, nothing less.

Every line of code, every design decision, every word in documentation must be honest about what we can and cannot guarantee.

We measure success by orchestration logic that behaves predictably, even when the nodes it orchestrates do not.

## Critical Lesson from This Session

**Determinism vs Predictability**: We learned that ClearFlow is NOT deterministic because:
- Nodes execute arbitrary async code
- We don't control timing or execution order
- External services and LLMs introduce variability

What we DO provide is **predictable routing**: given a node outcome, the next step is always the same. This is valuable but fundamentally different from deterministic execution.

Always be precise with technical terms. Our users are engineers who will verify our claims.