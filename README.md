# ClearFlow

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/clearflow?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/clearflow)
[![Coverage Status](https://coveralls.io/repos/github/artificial-sapience/clearflow/badge.svg?branch=main)](https://coveralls.io/github/artificial-sapience/clearflow?branch=main)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt)

Correctness-first orchestration for probabilistic AI. Type-safe, deeply immutable, 100% code coverage.

## Why ClearFlow?

- **Message-driven architecture** – Commands trigger actions, Events record facts
- **100% test coverage** – Every path verified to work
- **Type-safe flows** – Full static typing with pyright strict mode
- **Deep immutability** – All state transformations create new immutable data
- **Minimal dependencies** – Only Pydantic for validation and immutability
- **Single completion** – Exactly one end message type per flow

## How It Works

ClearFlow uses message-driven orchestration:

```text
Command → Node → Event → Node → Event → End
```

- **Commands** request actions: "analyze this portfolio"
- **Events** record what happened: "risk assessment completed"
- **Nodes** process messages and emit new ones
- **Flows** route messages between nodes based on type

Every message knows where it came from (causality tracking), making complex AI orchestration debuggable and testable.

## Quick Start

```bash
pip install clearflow
```

**Note**: ClearFlow is in alpha. Pin your version in production (`clearflow==0.x.y`) as breaking changes may occur in minor releases.

## Real-World Examples

| Example | What It Shows |
|---------|---------------|
| [Chat](examples/chat/) | OpenAI integration with conversation history |
| [Portfolio Analysis](examples/portfolio_analysis/) | Multi-agent coordination using DSPy |
| [RAG](examples/rag/) | Document chunking and FAISS vector search |

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

## ClearFlow vs PocketFlow

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **Architecture** | Message-driven (Commands/Events) | State-based transformations |
| **State** | Immutable messages with causality tracking | Mutable, passed via `shared` param |
| **Routing** | Message type-based explicit routes | Action-based graph edges |
| **Completion** | Single end message type | Multiple exits allowed |
| **Type safety** | Full static typing with pyright strict | Dynamic (no annotations) |

## Development

### Install uv

- Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install uv.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone and set up development environment

```bash
git clone https://github.com/artificial-sapience/clearflow.git
cd clearflow
uv sync --all-extras     # Creates venv and installs deps automatically
./quality-check.sh       # Run all checks
```

## License

[MIT](LICENSE)

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.
