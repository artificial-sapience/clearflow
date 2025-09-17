# Repository Guidelines

## Project Structure & Module Organization
The core package lives in `clearflow/` with flow orchestration (`flow.py`), node definitions (`node.py`), immutable message models (`message.py`), and shared internals under `_internal/`. Public types are re-exported via `clearflow/__init__.py`. Tests mirror the package inside `tests/`, sharing fixtures in `tests/conftest.py`. Reference examples sit under `examples/`, while `docs/` and `linters/` hold assistant-facing docs and custom compliance scripts. Keep CLI helpers in `scripts/` and infrastructure configuration (coverage, linting) in `pyproject.toml`.

## Build, Test, and Development Commands
Create or refresh the local environment with `uv sync --all-extras`. Run the full gate with `./quality-check.sh`, which bootstraps a `.venv` and executes linting, typing, security, and coverage checks. For targeted work, `uv run ruff check clearflow` lints, `uv run ruff format` enforces formatting, and `uv run pyright clearflow tests` performs type analysis. Execute the test suite (enforcing 100% coverage) via `uv run pytest -xv --cov=clearflow --cov-report=term-missing --cov-fail-under=100`.

## Coding Style & Naming Conventions
Code targets Python 3.13+, 4-space indentation, and 120-character lines. Ruff’s formatter enforces double quotes and import ordering, so always run it before committing. Keep modules pure and free of runtime side effects—state is immutable by design. Every public function, method, and module must be fully type-annotated; prefer explicit generics for flow nodes. Follow Pydantic model naming (`*Model`) and favour descriptive node names that match their branch outcome.

## Testing Guidelines
Write pytest tests in `tests/` using `test_<unit>.py` files and descriptive function names like `test_route_validates_branch`. Maintain branch parity between tests and production modules. Avoid fixtures with global state; rely on dataclass or Pydantic factories in `conftest.py`. The default quality script also runs bespoke guards (`linters/check-test-suite-compliance.py`)—tests must pass without relying on `# pragma: no cover` or muted assertions.

## Commit & Pull Request Guidelines
Adopt Conventional Commit prefixes (e.g., `feat(flow): ...`, `refactor(node): ...`). Commits should compile, type-check, and keep coverage at 100%. PRs need a clear summary, linked issues, and relevant screenshots or transcripts when UI or agent prompts change. Highlight risk areas and note any follow-up work. Request reviews only after `./quality-check.sh` succeeds locally.

## Quality & Security Gates
Architecture and immutability linters (`linters/check-architecture-compliance.py`, `linters/check-immutability.py`) must stay green. Security scans (`uv run bandit`, `uv run pip-audit`) run automatically in the quality script; address findings rather than suppressing them. Complexity is enforced with `uv run xenon` at grade A—refactor high-complexity nodes instead of relaxing thresholds.
