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
- **Minimal dependencies** - Only Pydantic for validation and immutability

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

ClearFlow is a minimal orchestration framework with functional patterns and **minimal dependencies** (only Pydantic). It implements a **message-driven architecture** for managing workflows that include language model calls and other async operations.

### Core Concepts

1. **Nodes**: Message processing units
   - Inherit from `Node[TIn, TOut]` and override `process()` method
   - Nodes are Pydantic models with a required `name` field
   - Input: Message of type `TIn` (Command or Event)
   - Output: Message of type `TOut` (Command or Event)
   - Support union types for flexible message handling

2. **Messages**: Immutable data carriers
   - `Command`: Imperative requests with optional trigger
   - `Event`: Past-tense facts with required trigger
   - Auto-generated IDs and timestamps
   - Causality tracking via `triggered_by_id` and `run_id`
   - Inherit from `StrictBaseModel` for validation

3. **Flow**: Type-safe workflow builder
   - Create with `create_flow("name", starting_node)` function
   - Chain with `.route(from_node, MessageType, to_node)`
   - End with `.end_flow(TerminalType)` for single termination
   - Terminal type enforces single responsibility principle
   - Full generic support with type inference

### Key Facts

- **Code size**: ~1000 lines total, ~700 non-comment lines
- **Test coverage**: 100% required
- **Type safety**: No unnecessary `Any` (required for metaclass patterns)
- **Immutability**: All models are immutable via Pydantic
- **Routing**: Explicit (NOT deterministic execution)
- **Single termination**: Exactly one terminal message type per flow

### Common Patterns

```python
from typing import override
from clearflow import Node, Event, Command, create_flow

# Creating nodes - Node is a Pydantic model
class DocumentLoader(Node[LoadCommand, DocumentLoadedEvent | ErrorEvent]):
    name: str = "loader"

    @override
    async def process(self, message: LoadCommand) -> DocumentLoadedEvent | ErrorEvent:
        try:
            content = await load_document(message.path)
            return DocumentLoadedEvent(
                content=content,
                run_id=message.run_id,
                triggered_by_id=message.id
            )
        except Exception as e:
            return ErrorEvent(
                error_message=str(e),
                run_id=message.run_id,
                triggered_by_id=message.id
            )

# Building a flow with terminal type pattern
loader = DocumentLoader()
processor = ProcessorNode()
finalizer = FinalizerNode()

flow_instance = (
    create_flow("Pipeline", loader)
    .route(loader, DocumentLoadedEvent, processor)
    .route(loader, ErrorEvent, finalizer)
    .route(processor, ProcessedEvent, finalizer)
    .end_flow(PipelineCompleteEvent)  # Terminal type defines goal
)
```

### Terminal Type Pattern

Each flow has **exactly ONE goal** defined by its terminal message type:

```python
# WRONG: String-based routing (old pattern)
flow = create_flow("Old", start)
    .route(node_a, "success", node_b)  # NO LONGER SUPPORTED
    .route(node_b, "done", node_c)  # NO LONGER SUPPORTED

# RIGHT: Message type routing (current pattern)
flow = create_flow("Current", start)
    .route(node_a, ProcessedEvent, node_b)
    .route(node_b, ValidatedEvent, node_c)
    .end_flow(WorkflowCompleteEvent)  # Terminal type defines goal
```

**Single Responsibility Principle**: Each flow should do ONE thing well:

- **Chat flow**: Goal is `ChatCompleted` - end conversation
- **RAG indexing**: Goal is `IndexCreatedEvent` - create index
- **RAG query**: Goal is `AnswerGeneratedEvent` - generate answer
- **Analysis flow**: Goal is `AnalysisComplete` - complete analysis

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
- No `Any` types
- Prefer boring, obvious code over clever solutions

**UNIVERSAL REQUIREMENT**: Every single line of code in this project must meet mission-critical quality standards:

- Core modules
- Test files
- Example code
- Documentation code blocks
- Linter scripts
- Build scripts
- ALL Python code

**No Exceptions Policy**:

- Examples are production templates - they MUST demonstrate best practices
- Tests are production code - they MUST be maintainable and clear
- Documentation code blocks MUST be executable and correct
- Even utility scripts MUST pass all quality checks

**Import Standards (Universal)**:

- **Absolute imports only** - No relative imports anywhere in the codebase
- **Import from public APIs** - `from clearflow import ...` not `from clearflow.internal import ...`
- **Explicit is better** - Full paths provide clarity and refactoring safety

**Example Compliance**:

```python
# WRONG - relative import in example
from .messages import Command

# CORRECT - absolute import for examples
from examples.chat_message_driven.messages import Command

# CORRECT - importing from public API
from clearflow import Node, create_flow
```

**Rationale**: In mission-critical systems, there are no "throwaway" files. Every file could be copied, referenced, or used as a template. Maintaining uniform quality prevents bad patterns from propagating into production systems.

**LINTER SUPPRESSION POLICY**:

- **NEVER add linter suppressions without explicit user approval**
- This includes: `# noqa`, `# pyright: ignore`, etc.
- All approved suppressions MUST include a justification comment
- Example: `# noqa: C901  # Display function complexity acceptable for UI`
- Always fix the root cause instead of suppressing when possible

**TC001 RULE ENFORCEMENT**:

- **TC001 violations indicate real code issues** - unnecessary type-annotated intermediate variables
- Pattern to eliminate: `result: SomeType = some_expression` followed by immediate usage
- Solution: Use `some_expression` directly instead of creating intermediate variable
- These violations correctly identify code ceremony that serves no purpose
- Eliminating them also removes unnecessary runtime imports

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
   - Examples must pass ALL quality checks (no exceptions)
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
**Example**: Public API exports all components in `__all__` list:

```python
__all__ = [
    "Command",
    "Event",
    "FlowBuilder",
    "Message",
    "Node",
    "NodeInterface",
    "Observer",
    "StrictBaseModel",
    "create_flow",
]
```

**Architecture Rule**: Tests must import from public API only
**Implementation**: Added ARCH011 linter rule to detect `from clearflow.submodule import ...` in tests
**Enforcement**: Tests use `from clearflow import Node, create_flow` instead of submodule imports

**Critical Rule**: Public functions should only accept and return public types
**Discovered**: If `create_flow().end_flow()` returns an internal `_Flow`, it's returned as public `Node` interface
**Solution**: Return type is `Node[TStartIn, TEnd]` which is a public interface

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
    assert output.run_id == input_msg.run_id
```

### Architecture Linter Enhancement

**Pattern**: Extend linter for new architectural requirements
**Example**: Added ARCH011 to prevent tests accessing non-public modules:

```python
non_public_modules = [
    "clearflow._internal.flow_impl", "clearflow._internal.callback_handler"
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

## Example Organization

**Mission-Critical Example Standards**:

- Examples MUST use absolute imports only (no relative imports)
- Examples MUST pass ALL quality checks with zero violations
- Examples MUST demonstrate production best practices
- Examples MUST be treated as production code, not demos

**Directory Structure**:

```
examples/
├── chat/                    # Chat example
├── portfolio_analysis/      # Portfolio analysis example
├── rag/                     # RAG example
└── README.md                # Examples overview
```

### Alpha Release Classification

**Strategy**: Use Alpha status to justify breaking changes in minor releases
**Justification**: Low adoption (no GitHub stars/issues) allows architectural shifts
**pyproject.toml**: `"Development Status :: 3 - Alpha"` enables minor version breaking changes

## Messaging Principles

- **Avoid vague claims** - "Full transparency" misleads about features we don't have
- **Use active voice** - "Compose flows" not "Composing flows"
- **Acknowledge AI nature** - "emergent AI" not "unpredictable AI" (less adversarial)
- **Be specific** - "Type-safe", "Minimal dependencies" are verifiable features

## Session Learnings: 2025-01-17

### Quality Check Standards

**Critical Rule**: ALL quality check warnings are errors - zero tolerance
**Discovered**: PLR6301 warnings about methods that could be static must be fixed
**Solution**: Make methods static when they don't use instance state

### LLM Integration Patterns

**Pattern**: LLM-powered linters using ClearFlow's message-driven architecture
**Implementation**: Created type_safety_analyzer_claude demonstrating:
- AST parsing in CodeParserNode (no LLM needed)
- DSPy signatures for structured LLM analysis
- Observer pattern for progress visibility during LLM calls
- Single terminal type (not unions) per ClearFlow requirement

**Key Learning**: ClearFlow flows ARE nodes - use `.process()` not `.run()`

### Observer Integration

**Pattern**: Add observers before calling `.end_flow()`:
```python
flow_builder = create_flow("Name", start_node)
    .route(node_a, EventA, node_b)

if verbose:
    flow_builder = flow_builder.observe(observer)

return flow_builder.end_flow(TerminalEvent)
```

### Architecture Compliance

**Rule**: Private methods accessed via class name violate ARCH006
**Solution**: Make methods public (remove underscore) when accessed as static

### Immutability Requirements

**Enforced by linters**:
- No `dict` or `list` in type annotations (use `Mapping`, `tuple`)
- Frozen dataclasses required
- No mutable default arguments

**Exception**: Building lists with `.append()` allowed within functions

### DSPy Configuration

**Required for OpenAI integration**:
```python
# Load .env from multiple locations
env_locations = [Path(".env"), Path("../.env"), Path("../../.env")]
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        break

# Configure DSPy with proper settings
lm = dspy.LM(
    model=f"openai/{model}",
    api_key=api_key,
    temperature=1.0,  # Required for gpt-5-nano
    max_tokens=16000  # Required for reasoning models
)
```

## Session Learnings: 2025-01-15

### Observer Pattern Refactoring

**Completed**: Renamed callback system to Observer pattern for clarity

- `CallbackHandler` → internal implementation detail
- `Observer` → public base class with no-op defaults
- `.with_callbacks()` → `.observe()` method
- Removed redundant error handling in `_safe_callback` (CallbackHandler already handles all errors)

### API Naming Decisions

**Function**: `create_flow()` creates flows explicitly
**Rationale**: Self-documenting name follows stdlib patterns like `asyncio.create_task()`
**Implementation**: Defined in `flow_impl.py`, exported through `__init__.py`

### StrictBaseModel Documentation

**Key Setting**: `arbitrary_types_allowed=True` is essential for user flexibility
**Rationale**: Mission-critical systems need to integrate with existing codebases
**Users need**: Frozen dataclasses, domain types, AI library types (LangChain, DSPy, etc.)

### Architecture Compliance

**Discovered**: Tests importing from `_internal` violate architecture and are caught by linter
**Pattern**: ARCH003 violation prevents tests from using internal implementation
**Solution**: All tests must use public API from `clearflow/__init__.py`

### Documentation Best Practices

**Config documentation pattern**:

```python
model_config = ConfigDict(
    # Category name
    setting=value,  # One-line what
    # One-line why
)
```

**Class docstring structure**:

1. One-line purpose statement
2. "Why use this" section with bullets
3. Realistic code example with >>> prompts
4. "Perfect for" section with use cases
