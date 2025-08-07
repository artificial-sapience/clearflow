# Contributing to ClearFlow

Thank you for considering contributing to ClearFlow. This project maintains strict standards to ensure trustworthiness for mission-critical AI systems.

## Our Standards

**Every contribution must maintain:**
- 100% test coverage
- Zero type errors (mypy and pyright strict mode)
- Immutable state (all dataclasses frozen)
- No external dependencies

If your contribution reduces any of these metrics, we'll work with you to address it or suggest alternatives.

## Setup

```bash
# Install ClearFlow for testing
pip install clearflow

# For development
git clone https://github.com/consent-ai/ClearFlow.git
cd ClearFlow
uv sync --group dev        # Install with dev dependencies
./quality-check.sh         # Verify all checks pass
```

## Before You Contribute

1. Read [docs/target-audience.md](docs/target-audience.md) to understand who we build for
2. Understand our philosophy: Trust through proof, not promises
3. Review the codebase - it's less than 200 lines

## Code Requirements

### Immutability is Non-Negotiable

```python
# ✅ Correct - using transform()
async def exec(self, state: State[dict]) -> NodeResult[dict]:
    new_state = state.transform(lambda d: {**d, "processed": True})
    return NodeResult(new_state, "success")

# ❌ Wrong - State doesn't have these methods
state.with_data(...)  # Does not exist
state.get(...)        # Does not exist
state.data["key"] = value  # Mutation not allowed
```

### Type Safety is Mandatory

- Every function must have type annotations
- No `Any` types unless interfacing with external APIs
- No `type: ignore` comments
- Pyright takes precedence when tools disagree

### Testing Standards

```bash
# Your PR must pass all of these
./quality-check.sh

# Individual checks if needed
uv run pytest --cov=clearflow --cov-fail-under=100
uv run mypy --strict clearflow tests examples
uv run pyright clearflow tests examples
```

## What We Accept

### High-Value Contributions

1. **Bug fixes** that maintain all quality metrics
2. **Performance improvements** with benchmarks
3. **Documentation fixes** for accuracy
4. **New examples** showing real patterns (not toys)

### What Makes a Good Example

Examples should demonstrate actual use cases:
- Error handling patterns with LLMs
- State management across conversations  
- Convergence patterns for single termination
- Recovery from API failures

## What We Reject

1. **Features that add complexity** without clear benefit
2. **Convenience methods** that hide behavior
3. **External dependencies** for any reason
4. **Code that reduces type safety** 
5. **"Clever" solutions** over obvious ones
6. **Documentation** instead of working examples
7. **Broad refactoring** without clear value

## Pull Request Process

1. **One thing per PR** - easier to review and reject if needed
2. **Run quality checks** - `./quality-check.sh` must pass
3. **Update tests** - maintain 100% coverage
4. **Add to CHANGELOG** - under "Unreleased"
5. **Reference issue** - link to the problem you're solving

### PR Title Format
- `fix: correct single termination validation`
- `feat: add retry example with backoff`
- `docs: fix incorrect State example`

## Development Workflow

```bash
# Create your branch
git checkout -b fix/specific-issue

# Make changes and test
./quality-check.sh

# Commit with clear message
git commit -m "fix: prevent multiple routes to None"

# Push and create PR
git push origin fix/specific-issue
```

## Questions?

- Check existing examples first
- Read the code - it's short
- Open an issue for discussion

## Remember

We measure success by production reliability, not feature count. Every line of code is a liability. Every dependency is a risk. 

Your contribution should make ClearFlow more trustworthy, not just more capable.

**Important**: ClearFlow provides predictable routing, not deterministic execution. Be precise with technical terms - our users will verify our claims.

---

By contributing, you agree that your code will be held to these standards. We'd rather have no contributions than ones that compromise trust.