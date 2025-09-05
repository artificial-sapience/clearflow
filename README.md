# ClearFlow

[![Coverage Status](https://coveralls.io/repos/github/artificial-sapience/ClearFlow/badge.svg?branch=main)](https://coveralls.io/github/artificial-sapience/ClearFlow?branch=main)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

Type-safe async workflow orchestration for language models. **Explicit routing, immutable state, zero dependencies.**

---

## Why ClearFlow?

- **Predictable control flow** – explicit routes, no hidden magic  
- **Immutable, typed state** – frozen state passed via `NodeResult`  
- **One exit rule** – exactly one termination route enforced  
- **Tiny surface area** – one file, three exports: `Node`, `NodeResult`, `flow`  
- **100% test coverage** – every line tested  
- **Zero runtime deps** – bring your own clients (OpenAI, Anthropic, etc.)  

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
        # Retrieve relevant documents from vector store
        docs = ["Paris is the capital of France.", "London is the capital of UK."]
        return NodeResult(Context(state.question, docs), outcome="retrieved")

@dataclass(frozen=True)
class Generator(Node[Context, Answer]):
    name: str = "generator"
    
    @override
    async def exec(self, state: Context) -> NodeResult[Answer]:
        # Generate answer using LLM with retrieved context
        response = f"Based on context: {state.documents[0]}"
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
    result = await rag_flow(Query("What is the capital of France?"))
    print(result.state.response)  # "Based on context: Paris is the capital of France."

asyncio.run(main())
```

---

## Core Concepts

### `Node[TIn, TOut]`

A unit that transforms state from `TIn` to `TOut` (or `Node[T]` when types are the same).

- `prep(state: TIn) -> TIn` – optional pre-work/validation  
- `exec(state: TIn) -> NodeResult[TOut]` – **required**; return new state + outcome  
- `post(result: NodeResult[TOut]) -> NodeResult[TOut]` – optional cleanup/logging  

Nodes are `async`, **pure** (no side effects), and use frozen dataclasses.

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

## Example: Agent Router

```python
from dataclasses import dataclass, replace
from typing import override
from clearflow import Node, NodeResult, flow

@dataclass(frozen=True)
class Request:
    query: str
    intent: str = ""
    response: str = ""

@dataclass(frozen=True)
class Classifier(Node[Request]):
    name: str = "classifier"
    
    @override
    async def exec(self, state: Request) -> NodeResult[Request]:
        # Classify intent: "code", "docs", or "general"
        intent = "code" if "bug" in state.query else "general"
        return NodeResult(replace(state, intent=intent), outcome=intent)

@dataclass(frozen=True)
class CodeAgent(Node[Request]):
    name: str = "code_agent"
    
    @override
    async def exec(self, state: Request) -> NodeResult[Request]:
        return NodeResult(
            replace(state, response="Here's a code solution..."),
            outcome="handled"
        )

@dataclass(frozen=True)
class GeneralAgent(Node[Request]):
    name: str = "general_agent"
    
    @override
    async def exec(self, state: Request) -> NodeResult[Request]:
        return NodeResult(
            replace(state, response="I can help with that..."),
            outcome="handled"
        )

# Build router flow
classifier = Classifier()
code_agent = CodeAgent()
general_agent = GeneralAgent()

router = (
    flow("AgentRouter", classifier)
    .route(classifier, "code", code_agent)
    .route(classifier, "general", general_agent)
    .route(code_agent, "handled", None)    # terminate
    .route(general_agent, "handled", None) # terminate
    .build()
)

await router(Request(query="fix this bug"))  # Routes to CodeAgent
```

See more: [Chat example](examples/chat/) | [Structured output](examples/structured_output/)

---

## Testing Example

Nodes are easy to test in isolation because they are pure functions over typed state:

```python
import pytest
from dataclasses import dataclass
from typing import override
from clearflow import Node, NodeResult

@dataclass(frozen=True)
class Counter(Node[int]):
    name: str = "counter"
    
    @override
    async def exec(self, state: int) -> NodeResult[int]:
        return NodeResult(state + 1, "incremented")

@pytest.mark.asyncio
async def test_counter() -> None:
    counter = Counter()
    result = await counter(0)
    assert result.state == 1
    assert result.outcome == "incremented"
```

---

## When to Use ClearFlow

- LLM workflows where you need explicit control  
- Systems requiring clear error handling paths  
- Projects with strict dependency requirements  
- Applications where debugging matters  

---

## ClearFlow vs PocketFlow

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **State** | Immutable, passed via `NodeResult` | Shared store (mutable dict) |
| **Routing** | Explicit `(node, outcome)` routes | Graph with labeled edges |
| **Termination** | Exactly one `None` route enforced | Multiple exit patterns |
| **Type safety** | Full Python 3.13+ generics | Dynamic |
| **Lines** | ~250 | 100 |

Both are minimalist. ClearFlow emphasizes **type safety and explicit control**. PocketFlow emphasizes **brevity and shared state**.

---

## Development

```bash
# Install uv (if not already installed)
pip install --user uv   # or: pipx install uv

# Clone and set up development environment
git clone https://github.com/artificial-sapience/ClearFlow.git
cd ClearFlow
uv sync --all-extras      # Creates venv and installs deps automatically
./quality-check.sh       # Run all checks
```

---

## License

[MIT](LICENSE)

---

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.
