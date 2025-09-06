# ClearFlow

[![Coverage Status](https://coveralls.io/repos/github/artificial-sapience/ClearFlow/badge.svg?branch=main)](https://coveralls.io/github/artificial-sapience/ClearFlow?branch=main)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

Type-safe orchestration for unpredictable AI.

---

## Why ClearFlow?

- **Type-safe state transformations** – Errors caught at development time, not runtime
- **Single exit enforcement** – No ambiguous endings
- **100% test coverage** – Every path proven to work
- **Immutable state transformations** – No hidden state mutations
- **Zero dependencies** – No hidden failure modes
- **~250 lines total** – Entire system can be quickly audited

---

## Installation

```bash
pip install clearflow
```

---

## 60-second Quickstart: RAG Pipeline

```python
from dataclasses import dataclass
from typing import override
from clearflow import Node, NodeResult, flow

# 1) Define immutable state transitions
@dataclass(frozen=True)
class Query:
    question: str

@dataclass(frozen=True)
class Context:
    question: str
    documents: list[str]

@dataclass(frozen=True)
class Answer:
    question: str
    documents: list[str]
    response: str

# 2) Define nodes for each step
@dataclass(frozen=True)
class Retriever(Node[Query, Context]):
    name: str = "retriever"
    
    @override
    async def exec(self, state: Query) -> NodeResult[Context]:
        # Retrieve domain-specific documents (e.g., internal KB, product docs)
        docs = [
            "The T-800 neural net processor runs at 120 teraflops.",
            "T-800 models require 30 seconds for full system boot sequence."
        ]
        return NodeResult(Context(state.question, docs), outcome="retrieved")

@dataclass(frozen=True)
class Generator(Node[Context, Answer]):
    name: str = "generator"
    
    @override
    async def exec(self, state: Context) -> NodeResult[Answer]:
        # Generate answer grounded in retrieved domain knowledge
        response = f"Based on documentation: {state.documents[0]}"
        return NodeResult(
            Answer(state.question, state.documents, response), 
            outcome="answered"
        )

# 3) Build RAG flow with explicit routing
retriever = Retriever()
generator = Generator()

rag_flow = (
    flow("RAG", retriever)
    .route(retriever, "retrieved", generator)
    .end(generator, "answered")
)

# 4) Run it
import asyncio

async def main() -> None:
    result = await rag_flow(Query("What are the T-800's processing specifications?"))
    print(result.state.response)  # "Based on documentation: The T-800 neural net processor..."

asyncio.run(main())
```

---

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

A function that creates a flow builder with **explicit routing**:

```python
flow("Name", start_node)
  .route(start_node, "outcome1", next_node)
  .route(next_node, "outcome2", final_node)
  .end(final_node, "done")  # exactly one termination
```

**Routing**: Routes are `(node, outcome)` pairs. Each outcome must have exactly one route.  
**Type inference**: The flow infers types from start to end, supporting transformations.  
**Composability**: A flow is itself a `Node` – compose flows within flows.

---

## ClearFlow vs PocketFlow

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **State** | Immutable, passed via `NodeResult` | Mutable, passed via `shared` param |
| **Routing** | Outcome-based explicit routes | Action-based graph edges |
| **Termination** | Exactly one exit enforced | Multiple exits allowed |
| **Type safety** | Full Python 3.13+ generics | Dynamic (no annotations) |
| **Lines** | ~250 | ~90 |

Both are minimalist. ClearFlow emphasizes **robust, type-safe orchestration**. PocketFlow emphasizes **brevity and flexibility**.

---

## Development

```bash
# Install uv (if not already installed)
pipx install uv

# Clone and set up development environment
git clone https://github.com/artificial-sapience/ClearFlow.git
cd ClearFlow
uv sync --all-extras     # Creates venv and installs deps automatically
./quality-check.sh       # Run all checks
```

---

## License

[MIT](LICENSE)

---

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.
