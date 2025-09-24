# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Concept

**ClearFlow**: Message-driven orchestration for AI workflows with type safety, immutability, and 100% test coverage.

## Architecture Overview

### Message Flow Pattern

```text
Command → Node → Event → Node → Event → End
```

- **Commands**: Request actions (`AnalyzeCommand`, `LoadCommand`)
- **Events**: Record what happened (`AnalysisComplete`, `DocumentLoaded`)
- **Nodes**: Transform messages (`Node[TIn, TOut]`)
- **Flows**: Route by message type with single termination

### Key Files Structure

```text
clearflow/
├── __init__.py          # Public API exports
├── message.py           # Command/Event base classes
├── node.py              # Node interface
├── flow.py              # FlowBuilder interface
├── observer.py          # Observer pattern
└── _internal/
    ├── flow_impl.py     # Flow implementation
    └── callback_handler.py
```

## Development Commands

```bash
# Setup
uv sync --all-extras

# Run all quality checks (MUST PASS 100%)
./quality-check.sh

# Individual commands
uv run ruff check --fix .        # Lint with fixes
uv run ruff format .              # Format code
uv run pyright .                  # Type checking
uv run pytest -xvs                # Run all tests
uv run pytest -xvs -k test_name   # Run specific test
uv run pytest --cov=clearflow --cov-fail-under=100  # Coverage

# Run examples
cd examples/chat && uv run python main.py
cd examples/portfolio_analysis && uv run python main.py
cd examples/rag && uv run python main.py
```

## Quality Requirements

### Zero Tolerance Policies

1. **100% test coverage** - No exceptions
2. **No linter suppressions** without explicit user approval
3. **pyright strict mode** - All type errors must be fixed
4. **Immutable data** - Enforced by custom linters

### Custom Linters (Auto-run in quality-check.sh)

- `check-architecture-compliance.py`: No `_internal` imports in tests
- `check-immutability.py`: Use `tuple` not `list`, frozen dataclasses
- `check-test-suite-compliance.py`: Proper async test patterns

## Code Patterns

### Creating a Message-Driven Flow

```python
from typing import override
from clearflow import Node, Command, Event, create_flow

# 1. Define messages
class ProcessCommand(Command):
    data: str

class ProcessedEvent(Event):
    result: str
    triggered_by_id: str  # Required for events

# 2. Create node
class ProcessorNode(Node[ProcessCommand, ProcessedEvent]):
    name: str = "processor"

    @override
    async def process(self, msg: ProcessCommand) -> ProcessedEvent:
        return ProcessedEvent(
            result=f"Processed: {msg.data}",
            triggered_by_id=msg.id
        )

# 3. Build flow
flow = (
    create_flow("pipeline", ProcessorNode())
    .route(ProcessorNode(), ProcessedEvent, NextNode())
    .end_flow(CompleteEvent)  # Single termination
)

# 4. Run
result = await flow.process(ProcessCommand(data="test"))
```

### Testing Patterns

```python
# Always use public API
from clearflow import Node, create_flow  # ✓
from clearflow._internal import ...      # ✗

# Test real scenarios
async def test_multi_agent_flow():
    """Test actual AI orchestration patterns."""
    flow = create_portfolio_analysis_flow()
    result = await flow.process(StartAnalysisCommand(...))
    assert isinstance(result, DecisionMadeEvent)

# Extract complex assertions
def _assert_event_causality(event: Event, command: Command) -> None:
    assert event.triggered_by_id == command.id
    assert event.run_id == command.run_id
```

### Adding Observers

```python
from clearflow import Observer

class LoggingObserver(Observer):
    async def on_node_start(self, node: str, message: Message) -> None:
        print(f"[{node}] Processing: {message.id}")

flow = (
    create_flow("pipeline", start_node)
    .observe(LoggingObserver())  # Add before end_flow
    .route(start_node, EventType, next_node)
    .end_flow(CompleteEvent)
)
```

## Important Constraints

### Type Safety

- Use `Node[TIn, TOut]` with precise types
- Union types for branching: `Node[Cmd, EventA | EventB]`
- No `Any` types except metaclass patterns

### Immutability Rules

- Messages are Pydantic models with `frozen=True`
- Type annotations: `tuple[T, ...]` not `list[T]`
- No mutable default arguments
- Use `cast()` for accumulation patterns in linters/tests

### Import Rules

- Absolute imports only (no relative imports)
- Tests must use public API from `clearflow` module
- Examples use full paths: `from examples.chat.nodes import ChatNode`

## Common Tasks

### Add New Message Type

```python
class MyEvent(Event):
    data: str
    triggered_by_id: str  # Required for Event
    run_id: str | None = None  # Auto-generated if None
```

### Create Multi-Path Node

```python
class RouterNode(Node[InputCmd, SuccessEvent | ErrorEvent]):
    name: str = "router"

    @override
    async def process(self, msg: InputCmd) -> SuccessEvent | ErrorEvent:
        if validate(msg):
            return SuccessEvent(triggered_by_id=msg.id)
        return ErrorEvent(error="Invalid", triggered_by_id=msg.id)
```

### Handle Node Errors

```python
flow = (
    create_flow("safe_pipeline", StartNode())
    .route(StartNode(), SuccessEvent, ProcessNode())
    .route(StartNode(), ErrorEvent, ErrorHandler())  # Error path
    .route(ProcessNode(), CompleteEvent, FinalNode())
    .route(ErrorHandler(), CompleteEvent, FinalNode())
    .end_flow(CompleteEvent)
)
```

## Project Status

- **Version**: Alpha (0.x.y) - Breaking changes allowed
- **Python**: 3.13+ required (PEP 695 support)
- **Dependencies**: Pydantic only
- **Code size**: ~700 SLOC core
- **Test coverage**: 100% required
- **PyPI**: <https://pypi.org/project/clearflow/>

## Key Principles

1. **Message-driven**: Commands trigger, Events record
2. **Type-safe**: Full static typing, no runtime surprises
3. **Immutable**: All data transformations create new objects
4. **Testable**: Every path must be tested
5. **Explicit**: No hidden behavior or implicit routing

## Remember

- Fix root causes, not symptoms
- Every file is production code (including examples)
- Single responsibility per flow
- Causality tracking makes debugging possible

## Lean 4 Development (packages/stigmergic/lean)

### Build Commands

```bash
# Build quietly (suppresses info messages, shows errors/warnings)
lake -q build

# Full build with diagnostics
lake build

# Clean rebuild
lake clean && lake -q build
```

### Lean 4 Specification Standards

- **No `sorry` in proofs** - All theorems must be proven
- **Minimal linter suppressions** - Document justification for each suppression
- **Document all public declarations** - PURPOSE, PRECONDITIONS, POSTCONDITIONS, INVARIANTS
- **Bijective correspondence** - Math notation paired with English explanation
- **Properties as theorems** - If it matters, prove it (e.g., `age_monotonic`, `decay_non_increasing`)
- **Preservation theorems** - All operations need theorems proving field preservation
- **Document WHERE invariants enforced** - Not just what, but which module enforces them

### Common Lean 4 Issues & Solutions

**Issue**: "upstreamableDecl" linter warnings for simple types
**Solution**: Add domain-specific theorems/properties or use `set_option linter.upstreamableDecl false`

**Issue**: ppRoundtrip linter with inductive type doc comments
**Solution**: Use `set_option linter.ppRoundtrip false` - formatting issue with `where` + doc comments

**Issue**: Heartbeat info messages cluttering output
**Solution**: Use `lake -q build` for quiet mode

**Issue**: Type safety vs flexibility tension (e.g., String types)
**Solution**: Use inductive types with `custom` escape hatch + smart constructor validation

### Normative Decision Tracking

**REQUIRED**: Every specification module needs a corresponding `*Decisions.lean` file:
- `Signal.lean` → `SignalDecisions.lean`
- Document alternatives, rationale, dependencies, status
- Categories: `DC_STGM_*` (Definitional), `OA_STGM_*` (Ontological), `AD_STGM_*` (Architectural)
- Mark superseded decisions with `.Superseded` status and reference to replacement
