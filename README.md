# ClearFlow

A minimal orchestration framework for LLM-powered agents with predictable routing, immutable state, and enforced single termination.

[![codecov](https://codecov.io/gh/consent-ai/ClearFlow/graph/badge.svg?token=29YHLHUXN3)](https://codecov.io/gh/consent-ai/ClearFlow)
[![PyPI version](https://badge.fury.io/py/clearflow.svg)](https://badge.fury.io/py/clearflow)
[![CI Status](https://github.com/consent-ai/ClearFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/consent-ai/ClearFlow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

## What ClearFlow Does

ClearFlow is an orchestration framework for LLM-powered agents that provides predictable routing between async operations. Built for production systems where surprises are unacceptable.

**Guarantees:**
- **Static orchestration** - Given a node outcome, the next step is always predictable
- **Type-safe generics** - Full mypy/pyright strict validation
- **Immutable state** - State objects cannot be mutated, only transformed
- **Single termination** - Every flow has exactly one endpoint, enforced at build time
- **No hidden behavior** - What you define is what executes

**Limitations:**
- No deterministic execution (nodes execute arbitrary async code)
- No timing or ordering guarantees for async operations
- No protection from failures in node implementations
- No control over LLM or external service behavior

## Verification

- **100% test coverage**: Run `./quality-check.sh`
- **Type safety**: Check [clearflow/__init__.py](clearflow/__init__.py) - no `Any`, no `type: ignore`
- **Minimal codebase**: 191 lines in `clearflow/__init__.py`
- **Zero dependencies**: Check `dependencies = []` in [pyproject.toml](pyproject.toml)
- **Immutable types**: All dataclasses use `frozen=True`
- **Single termination**: See enforcement in `_StartedWithFlow.build()` method

## Quick Start

```python
from clearflow import Flow, Node, NodeResult, State

class ProcessNode(Node[dict]):
    async def exec(self, state: State[dict]) -> NodeResult[dict]:
        # Transform state immutably
        new_state = state.transform(lambda d: {**d, "processed": True})
        return NodeResult(new_state, outcome="success")

# Build flow with single termination
flow = (
    Flow[dict]("Pipeline")
    .start_with(ProcessNode("process"))
    .route("process", "success", None)  # Single termination point
    .build()
)

# Execute
initial_state = State({"input": "data"})
result = await flow(initial_state)
```

See [examples/chat](examples/chat/) for a complete working example.

## Installation

```bash
# From PyPI
pip install clearflow
```

**Package:** [pypi.org/project/clearflow](https://pypi.org/project/clearflow/)

## Design Principles

- **Explicit over implicit** - Every route and transformation is visible
- **Type safety** - Catch issues at development time, not in production
- **Immutability** - Trace state changes through the flow without side effects
- **Single termination** - One endpoint per flow ensures predictable completion

ClearFlow is a minimal orchestration layer (< 200 lines) with zero dependencies that executes exactly as defined.

## Acknowledgments

ClearFlow builds on [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern, adding functional patterns, type safety, and immutability constraints for production systems.

## License

MIT