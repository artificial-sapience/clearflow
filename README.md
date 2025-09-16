# ClearFlow

[![Coverage Status](https://coveralls.io/repos/github/artificial-sapience/clearflow/badge.svg?branch=main)](https://coveralls.io/github/artificial-sapience/clearflow?branch=main)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/clearflow?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/clearflow)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt)

Compose type-safe flows for emergent AI. 100% test coverage, minimal dependencies.

## Why ClearFlow?

- **100% test coverage** – Every path proven to work
- **Type-safe transformations** – Errors caught at development time, not runtime
- **Immutable state** – No hidden mutations
- **Minimal dependencies** – Only Pydantic for validation and immutability
- **Single exit enforcement** – No ambiguous endings
- **AI-Ready Documentation** – llms.txt for optimal coding assistant integration

## Quick Start

```bash
pip install clearflow
```


## AI Assistant Integration

ClearFlow provides comprehensive documentation in [llms.txt](https://llmstxt.org/) format for optimal AI assistant support.

### Claude Code Setup

Add ClearFlow documentation to Claude Code with one command:

```bash
claude mcp add-json clearflow-docs '{
    "type":"stdio",
    "command":"uvx",
    "args":["--from", "mcpdoc", "mcpdoc", "--urls", "ClearFlow:https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt"]
}'
```

For IDEs (Cursor, Windsurf), see the [mcpdoc documentation](https://github.com/langchain-ai/mcpdoc#configuration).

### Direct URL Access

Use these URLs directly in any AI tool that supports llms.txt:

- **Minimal index** (~2KB): <https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt>
- **Full documentation** (~63KB): <https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms-full.txt>

## Examples

| Name | Description |
|------|-------------|
| [Chat](examples/chat/) | Simple conversational flow with OpenAI |
| [Portfolio Analysis](examples/portfolio_analysis/) | Multi-specialist workflow for financial analysis |
| [RAG](examples/rag/) | Full retrieval-augmented generation with vector search |

## Core Concepts

### `Node[TIn, TOut]`

A unit that transforms state from `TIn` to `TOut` (or `Node[T]` when types are the same).

- `prep(state: TIn) -> TIn` – optional pre-work/validation  
- `exec(state: TIn) -> NodeResult[TOut]` – **required**; return new state + outcome  
- `post(result: NodeResult[TOut]) -> NodeResult[TOut]` – optional cleanup/logging  

Nodes are frozen dataclasses that execute async transformations without mutating input state.

### `NodeResult[T]`

Holds the **new state** and an **outcome** string used for routing.

### `flow()`

A function that creates a flow with **explicit routing**:

```python
flow("Name", starting_node)
  .route(starting_node, ProcessedEvent, next_node)
  .route(next_node, TransformedEvent, final_node)
  .end_flow(CompletedEvent)  # Terminal type defines flow's goal
```

**Routing**: Routes are `(node, MessageType)` pairs. Each message type must have exactly one route.
**Type inference**: The flow infers types from start to end, supporting transformations.
**Composability**: A flow is itself a `Node` – compose flows within flows.

## Terminal Type Pattern

Each flow has **exactly ONE goal** defined by its terminal message type. This enforces single responsibility principle – a flow completes when ANY node produces the terminal type.

### Key Rules

1. **Single Terminal Type**: Declare one message type that completes the flow via `end_flow(MessageType)`
2. **Immediate Termination**: Flow ends as soon as any node produces the terminal type
3. **No Terminal Routing**: Terminal types cannot be routed between nodes – they always end the flow
4. **Build-Time Validation**: Terminal type conflicts are caught during flow construction

### Example

```python
from clearflow import Event, Command, Node, flow

# Define your terminal event
class AnalysisComplete(Event):
    """Flow goal: Complete the analysis."""
    result: str
    confidence: float

# Build flow with single terminal type
analysis_flow = (
    flow("Analysis", input_node)
    .route(input_node, DataValidated, analyzer)
    .route(analyzer, NeedsReview, reviewer)
    .route(reviewer, Approved, finalizer)
    .end_flow(AnalysisComplete)  # ONE goal: produce AnalysisComplete
)
```

When ANY node (`analyzer`, `reviewer`, or `finalizer`) produces `AnalysisComplete`, the flow terminates immediately with that result.

### Benefits

- **Clear Intent**: Each flow's purpose is explicit in its terminal type
- **Simplified Testing**: Test that flows produce correct terminal type
- **Better Composition**: Flows with clear goals compose naturally
- **Type Safety**: Terminal type mismatches caught at build time

## ClearFlow vs PocketFlow

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **State** | Immutable, passed via `NodeResult` | Mutable, passed via `shared` param |
| **Routing** | Outcome-based explicit routes | Action-based graph edges |
| **Termination** | Exactly one exit enforced | Multiple exits allowed |
| **Type safety** | Full Python 3.13+ generics | Dynamic (no annotations) |

ClearFlow emphasizes **robust, type-safe orchestration** with validation and guardrails. PocketFlow emphasizes **brevity and flexibility** with minimal overhead.

## Migration Guide (v2.0)

The terminal type pattern is a breaking change from node-based termination. Here's how to update your flows:

### Before (v1.x)
```python
flow = (
    flow("Process", start_node)
    .route(start_node, "success", process_node)
    .route(process_node, "done", end_node)
    .end(end_node, "complete")  # Node-based termination
)
```

### After (v2.0)
```python
flow = (
    flow("Process", start_node)
    .route(start_node, StartedEvent, process_node)
    .route(process_node, ProcessedEvent, end_node)
    .end_flow(CompletedEvent)  # Terminal type termination
)
```

### Key Changes

1. **Replace outcome strings with Message types**: Routes now use concrete message types instead of strings
2. **Replace `end(node, outcome)` with `end_flow(MessageType)`**: Declare the terminal type, not a node
3. **Remove routes to None**: Terminal types automatically end the flow – no explicit None routing

### Why This Change?

- **Single Responsibility**: Each flow has ONE clear goal
- **Type Safety**: Message types provide compile-time checking
- **Simplified Logic**: No need to track which nodes can terminate
- **Better Testing**: Test flows by their terminal output type

## Development

### Install uv

- Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install uv.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone and set up development environment

```bash
git clone https://github.com/artificial-sapience/clearflow.git
cd ClearFlow
uv sync --all-extras     # Creates venv and installs deps automatically
./quality-check.sh       # Run all checks
```

## License

[MIT](LICENSE)

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.
