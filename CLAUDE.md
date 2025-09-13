# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Philosophy

**Tagline**: "Compose type-safe flows for emergent AI"

ClearFlow provides mission-critical AI orchestration with verifiable correctness. Built for Python engineers who demand:

- **Deep immutability** - All state transformations create new immutable data structures
- **Immutable transformations** - Nodes transform state without mutation (though they may perform I/O)
- **Type safety** - Full static typing with pyright strict mode
- **100% test coverage** - Every path tested, no exceptions
- **Explicit routing** - Given an outcome, the next step is always the same
- **Zero dependencies** - Stdlib only for maximum reliability

Target audience: Python engineers building mission-critical AI systems who require verifiable orchestration with explicit control flow.

## Development Commands

```bash
# Install dependencies
uv sync                    # Install runtime dependencies
uv sync --all-extras        # Install with dev dependencies

# Run quality checks (enforced before commits)
./quality-check.sh         # Runs all checks: custom linters, lint, format, type check, tests

# Custom linters (mission-critical compliance)
python linters/check-architecture-compliance.py  # Architecture violations
python linters/check-immutability.py            # Deep immutability enforcement
python linters/check-test-suite-compliance.py   # Test isolation and resource management

# Individual quality commands
uv run ruff check --fix clearflow tests                 # Auto-fix linting (no unsafe fixes)
uv run ruff format clearflow tests                      # Format code
uv run pyright clearflow tests                          # Type check (pyright - only type checker)
uv run pytest -x -v tests                              # Run all tests
uv run pytest -x -v tests -k "specific_test"           # Run specific test

# Coverage requirements
uv run pytest --cov=clearflow --cov-report=term-missing --cov-fail-under=100
```

## Architecture Overview

ClearFlow is a minimal orchestration framework with functional patterns and **zero third-party dependencies**. It implements a **Node-Flow-State** pattern for managing workflows that include language model calls and other async operations.

### Core Concepts

1. **Nodes**: Async functions that transform state
   - Inherit from `Node[T]` or `Node[TIn, TOut]` and override `exec()` method
   - Nodes are frozen dataclasses with a `name` field
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
   - Create with `flow("name", start_node)` function
   - Chain with `.route(from_node, outcome, to_node)`
   - End with `.end(final_node, outcome)` for single termination
   - Single termination rule: exactly one route to `None`
   - Full generic support with type inference

### Key Facts

- **Code size**: ~250 lines total, ~185 non-comment lines
- **Test coverage**: 100% required
- **Type safety**: No unnecessary `Any` (required for metaclass patterns)
- **Immutability**: All dataclasses frozen
- **Routing**: Explicit (NOT deterministic execution)
- **Single termination**: Exactly one route to `None` per flow

### Common Patterns

```python
from dataclasses import dataclass
from typing import override
from clearflow import Node, NodeResult, flow

# Creating nodes - Node is a frozen dataclass
@dataclass(frozen=True)
class DocumentLoader(Node[DocumentState]):
    name: str = "loader"
    
    @override
    async def exec(self, state: DocumentState) -> NodeResult[DocumentState]:
        content = await load_document(state["path"])
        new_state: DocumentState = {**state, "content": content}
        return NodeResult(new_state, outcome="loaded")

# Building a flow with single termination
loader = DocumentLoader()
processor = ProcessorNode()
complete = CompleteNode()

flow_instance = (
    flow("Pipeline", loader)
    .route(loader, "loaded", processor)
    .route(loader, "error", complete)
    .route(processor, "processed", complete)
    .end(complete, "done")  # Single termination
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
- Pyright must pass in strict mode (sole type checker)
- Minimal `# pyright: ignore` comments (only for documented limitations)
- No `Any` types except where required (e.g., metaclass patterns)
- Prefer boring, obvious code over clever solutions

**LINTER SUPPRESSION POLICY**:

- **NEVER add linter suppressions without explicit user approval**
- This includes: `# noqa`, `# pyright: ignore`, etc.
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

These linters run automatically as part of `./quality-check.sh` and enforce strict policies for violations.

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

- **Factual and concise** - No verbosity, no "we/our" language
- **Ego-free** - No defensiveness, no marketing speak
- **Direct responses** - State facts and limitations without explanation

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
   - "Deterministic" when describing the framework
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

- README.md: ~100 lines (proportional to 250-line codebase)
- Individual docs: <100 lines
- Total documentation: <500 lines

## Release Process

Automated via GitVersion and Release Drafter. Manual trigger of release.yml publishes to PyPI.
**PyPI Package**: <https://pypi.org/project/clearflow/>

## Critical Technical Distinctions

**Explicit routing ≠ Deterministic execution** - ClearFlow provides explicit routing (given outcome X, next step is always Y) but NOT deterministic execution.

## Technical Notes

- **Pyright only** - Removed mypy, pyright supports PEP 695 defaults
- **Type stubs** - Stub only what you use (6 DSPy APIs, not 127 files)
- **Metaclass patterns** - Field descriptors must return `Any` (standard practice)

## llms.txt Implementation

ClearFlow includes comprehensive llms.txt support for optimal AI assistant integration:

1. **Files**:
   - `llms.txt` - Minimal index with documentation links (~2KB)
   - `llms-full.txt` - Auto-generated expanded content (~63KB)
   - Generated with: `uv run llms_txt2ctx --optional true llms.txt > llms-full.txt`

2. **Key Decisions**:
   - Single `clearflow/__init__.py` contains entire implementation (not split files)
   - Example links point to README.md files (context before code)
   - Include CLAUDE.md in llms.txt for AI context
   - Use GitHub raw URLs (we have no separate website)

3. **Integration**:
   - See README.md for Claude Code setup instructions
   - Direct URLs work with any llms.txt-compatible tool

4. **Maintenance**:
   - Manual generation: `uv run python scripts/generate_llms_txt_files.py`
   - Review changes before committing to maintain quality
   - Validate URLs: `cat llms.txt | grep -oE 'https://[^)]+' | xargs -I {} curl -I {}`

## Complexity Management

**Radical Simplification Strategy** for Grade A compliance:

- Replace complex content analysis with static descriptions
- Remove file system dependencies when possible
- Use simple dictionary lookups instead of conditional chains
- Question if dynamic behavior is truly necessary

**Common Over-engineering Patterns to Avoid**:

- Complex text processing for marginal metadata gains
- Multiple decision branches for utility scripts
- Dynamic file content analysis when static works
- Perfect descriptions when "good enough" suffices

**Example**: llms.txt generation - static descriptions work as well as complex extraction

## Security and Suppressions

**Subprocess Security Suppressions** (legitimate cases):

```python
import subprocess  # noqa: S404  # Required for running uv/mcpdoc commands in dev setup
["uv", "run", "cmd"],  # noqa: S607  # Safe: hardcoded command with literal args
```

**Pattern**: Development/configuration scripts with hardcoded commands are safe to suppress

## Session Learnings

### Public API Design Patterns

**Pattern**: When adding new API components, always export through `__init__.py`
**Example**: Message API requires all components in `__all__` list:
```python
__all__ = [
    # Original API  
    "Node", "NodeResult", "flow",
    # Message API
    "Message", "Event", "Command", "MessageFlow", "MessageNode", "message_flow", "Observer", "ObservableFlow",
]
```

**Architecture Rule**: Tests must import from public API only
**Implementation**: Added ARCH011 linter rule to detect `from clearflow.submodule import ...` in tests
**Enforcement**: Tests use `from clearflow import MessageNode, message_flow` instead of submodule imports

**Critical Rule**: Public functions should only accept and return public types
**Discovered**: If `message_flow().end()` returns `_MessageFlow`, then `MessageFlow` must be public
**Solution**: Remove underscore prefix and export in `__all__` rather than using `Any` type suppressions

### Coverage Gap Patterns

**Pattern**: Missing coverage often indicates missing validation tests
**Example**: Node name validation (lines 41-42) required test with empty/whitespace names:
```python
async def test_node_name_validation() -> None:
    with pytest.raises(ValueError, match="Node name must be a non-empty string"):
        ProcessorNode(name="")
    with pytest.raises(ValueError, match="Node name must be a non-empty string"):
        ProcessorNode(name="   ")
```

### PLR6301 Handling for Mission-Critical Software

**Decision**: Convert test methods to standalone functions when they don't use `self`
**Rationale**: Aligns with "fix root cause" principle, improves clarity, follows pylint best practice
**Pattern**: 
```python
# Instead of:
class TestMessage:
    async def test_message_type_property(self) -> None: ...

# Use:
async def test_message_type_property() -> None:
    """Test that message_type returns the concrete class type."""
    ...
```

### Complexity Management in Production Tests

**Principle**: Tests ARE production code in mission-critical systems with small teams
**Pattern**: Extract helper functions when test complexity reaches Grade B
**Example**: Break complex assertions into focused helper functions:
```python
def _assert_processed_event_correct(output: ProcessedEvent, input_msg: ProcessCommand, expected_result: str) -> None:
    assert isinstance(output, ProcessedEvent)
    assert output.result == expected_result
    _assert_event_metadata_correct(output, input_msg)

def _assert_event_metadata_correct(output: ProcessedEvent, input_msg: ProcessCommand) -> None:
    assert output.processing_time_ms == 100.0
    assert output.triggered_by_id == input_msg.id
    assert output.flow_id == input_msg.flow_id
```

### Architecture Linter Enhancement

**Pattern**: Extend linter for new architectural requirements
**Example**: Added ARCH011 to prevent tests accessing non-public modules:
```python
non_public_modules = [
    "clearflow.message", "clearflow.message_node", 
    "clearflow.message_flow", "clearflow.observer"
]
if node.module in non_public_modules and is_test_file:
    # Violation: test importing from non-public API
```

### Suppression Policy Enforcement

**Critical Discovery**: Both quality-check.sh and CLAUDE.md explicitly require user approval for ALL suppressions
**Violation Pattern**: Adding `# noqa`, `# type: ignore`, or `clearflow: ignore` without asking first
**Correct Process**: 
1. Identify need for suppression
2. Ask user for explicit approval with justification
3. Only proceed if approved
4. Always include justification comment in suppression

## Message-Driven Architecture Migration

### Creating Parallel Examples Strategy

**Pattern**: Always create message-driven versions alongside legacy examples before removal
**Benefits**: Validates new architecture, provides migration reference, maintains working code

**Directory Structure**:
```
examples/
├── chat/                    # Legacy Node-Flow-State
├── chat_message_driven/     # New message-driven version  
├── rag/                     # Legacy
├── rag_message_driven/      # New
└── README_message_driven.md # Architecture comparison guide
```

**Critical Design Rule**: Avoid god-objects in events
**Implementation**: Each message should have single responsibility, focused data
```python
# Bad: God-object event
@dataclass(frozen=True, kw_only=True)
class AnalysisCompleteEvent(Event):
    full_market_data: MarketData      # Too much data
    all_analysis_results: dict       # Multiple concerns
    trading_recommendations: list    # Different responsibility

# Good: Focused events  
@dataclass(frozen=True, kw_only=True)
class MarketDataAnalyzedEvent(Event):
    asset_symbol: str
    analysis_score: float
    
@dataclass(frozen=True, kw_only=True)
class RecommendationGeneratedEvent(Event):
    asset_symbol: str
    recommendation: str
    confidence: float
```

### Message-Driven Flow Construction Patterns

**Standard Pattern**: Chain message transformations with explicit routing
```python
flow = (
    message_flow("ProcessName", start_node)
    .from_node(start_node)
    .route(OutputEvent, transform_node)
    .from_node(transform_node)
    .route(TransformedEvent, end_node)
    .from_node(end_node)
    .end(FinalEvent)
)
```

**Two-Phase Pattern**: Separate flows for different lifecycle phases
```python
# Phase 1: Setup/Indexing
indexing_flow = create_indexing_flow()
index_result = await indexing_flow.process(setup_command)

# Phase 2: Runtime/Query  
query_flow = create_query_flow()
query_result = await query_flow.process(QueryCommand(
    data=index_result.prepared_data,
    query=user_input
))
```

### Message Design Principles

**Causality Tracking**: All messages must include flow tracking
```python
@dataclass(frozen=True, kw_only=True)
class MyCommand(Command):
    # Business data
    data: str
    
    # Required causality (inherited from Message base)
    # triggered_by_id: MessageId | None
    # flow_id: FlowId
```

**Message Lifecycle**: Commands trigger work, Events represent outcomes
- **Commands**: Imperative requests ("ProcessDocument", "GenerateResponse")
- **Events**: Past-tense facts ("DocumentProcessed", "ResponseGenerated")

### Alpha Release Classification

**Strategy**: Use Alpha status to justify breaking changes in minor releases
**Justification**: Low adoption (no GitHub stars/issues) allows architectural shifts
**pyproject.toml**: `"Development Status :: 3 - Alpha"` enables minor version breaking changes

## Messaging Principles

- **Avoid vague claims** - "Full transparency" misleads about features we don't have
- **Use active voice** - "Compose flows" not "Composing flows"  
- **Acknowledge AI nature** - "emergent AI" not "unpredictable AI" (less adversarial)
- **Be specific** - "Type-safe", "Zero dependencies" are verifiable features
