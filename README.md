# ClearFlow

Trustworthy orchestration for LLM-powered agents. Predictable routing. Immutable state. Single termination enforced.

[![codecov](https://codecov.io/gh/consent-ai/ClearFlow/graph/badge.svg)](https://codecov.io/gh/consent-ai/ClearFlow)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## For Production Agents

If you're building LLM-powered agents for mission and life-critical systems - financial trading bots, medical diagnostic assistants, industrial control systems, autonomous code generators, security incident responders - you understand the challenges of working with probabilistic AI systems.

You need predictable foundations. ClearFlow provides explicit, trustworthy orchestration so your framework isn't another source of surprises.

## What We Actually Do

We provide a trustworthy orchestration framework for connecting LLM calls and other async operations in your agents.

**What we guarantee:**
- **Static orchestration** - Given a node outcome, the next step is always predictable
- **Type-safe generics** - Full mypy/pyright strict validation
- **Immutable state** - State objects cannot be mutated, only transformed
- **Single termination** - Every flow has exactly one endpoint, enforced at build time
- **No hidden behavior** - What you define is what executes

**What we DON'T guarantee:**
- Deterministic execution (your nodes can do anything)
- Consistent timing or ordering of async operations  
- Protection from failures in your node implementations
- Any behavior of the LLMs or external services you call

## Verify Our Claims

- **100% test coverage**: Run `./quality-check.sh`
- **Type safety**: Check [clearflow/__init__.py](clearflow/__init__.py) - no `Any`, no `type: ignore`
- **Minimal codebase**: 191 lines in `clearflow/__init__.py`
- **Zero dependencies**: Check `dependencies = []` in [pyproject.toml](pyproject.toml)
- **Immutable types**: All dataclasses use `frozen=True`
- **Single termination**: See enforcement in `_StartedWithFlow.build()` method

## Get Started

```bash
# Clone and install locally (package not yet published)
git clone https://github.com/consent-ai/ClearFlow.git
cd ClearFlow
pip install -e .
```

See [examples/chat](examples/chat/) for a working example showing the core patterns.

## Early Stage Notice

ClearFlow is young (v0.x) and focused. We do one thing well: provide trustworthy orchestration for LLM-powered agents. We're the foundation layer - you bring your own LLM integrations and agent logic.

## Philosophy

We believe:
- **Explicit is better than implicit** - Every route and transformation is visible
- **Type safety prevents errors** - Catch issues at development time, not in production
- **Immutability aids debugging** - Trace exactly how state changes through your flow
- **Constraints enable confidence** - Single termination means predictable completion

ClearFlow is a minimal orchestration layer that does exactly what you tell it to do - nothing more, nothing less.

## Acknowledgments

ClearFlow was inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s elegant Node-Flow-State pattern and its proof that powerful workflow systems can be built with minimal code. We've adopted their core concepts and naming conventions while adding functional patterns, type safety, and immutability constraints needed for mission-critical systems.

## License

MIT