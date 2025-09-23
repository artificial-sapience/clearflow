# Repository Guidelines

## Project Structure & Module Organization

Core runtime lives in `clearflow/`: `flow.py` orchestrates flows, `node.py` defines nodes, `message.py` carries immutable payloads, and `_internal/` houses shared internals. Public APIs are re-exported in `clearflow/__init__.py`. Tests mirror the package in `tests/` with reusable factories in `tests/conftest.py`. Reference flows sit in `examples/`, assistant-facing docs land in `docs/`, and compliance tooling stays in `linters/`. CLI helpers reside in `scripts/`, while project-wide configuration (coverage, linting, tooling) is tracked in `pyproject.toml`.

## Build, Test, and Development Commands

- `uv sync --all-extras` bootstraps the environment with all optional dependencies.
- `./quality-check.sh` provisions a managed `.venv` and runs lint, type, security, and coverage gates.
- `uv run ruff check clearflow` lints; pair with `uv run ruff format` before committing.
- `uv run pyright clearflow tests` performs static type analysis across code and tests.
- `uv run pytest -xv --cov=clearflow --cov-report=term-missing --cov-fail-under=100` executes the full test suite with strict coverage.

## Coding Style & Naming Conventions

Target Python 3.13+, four-space indentation, and 120-character lines. Ruff enforces double quotes and import ordering—run the formatter after edits. Keep modules pure with no side effects and prefer immutable patterns throughout. Annotate every public function, method, and module, using explicit generics for flow nodes. Name Pydantic models with a `*Model` suffix and choose node identifiers that reflect their branch outcome.

## Testing Guidelines

Write pytest tests under `tests/` using filenames like `test_flow_routing.py` and descriptive function names (e.g., `test_route_validates_branch`). Mirror production modules with matching test coverage. Avoid global fixtures; use factories provided in `tests/conftest.py`. Keep total coverage at 100% and leave no gaps—bespoke guards in `linters/check-test-suite-compliance.py` enforce these rules.

## Commit & Pull Request Guidelines

Follow Conventional Commits (e.g., `feat(flow): add dynamic branch` or `fix(node): guard empty payload`). Ensure each commit formats, lints, type-checks, and passes tests. Pull requests should summarise intent, reference issues, and include transcripts or screenshots when agent prompts or outputs change. Highlight risks, note follow-up items, and request review only after `./quality-check.sh` succeeds locally.

## Quality & Security Gates

Stay ahead of automated guards: `linters/check-architecture-compliance.py` and `linters/check-immutability.py` validate design constraints, while `uv run bandit` and `uv run pip-audit` scan for security issues. Complexity must remain at Xenon grade A; refactor high-complexity nodes instead of silencing warnings. Treat findings as blockers until resolved.
