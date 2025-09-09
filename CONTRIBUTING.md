# Contributing to ClearFlow

Thank you for your interest in contributing to ClearFlow!

## Development Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   uv sync --all-extras
   ```

## Code Quality Standards

All contributions must maintain our zero-tolerance quality standards:

- **100% test coverage** - No exceptions
- **Type safety** - Must pass `uv run pyright` in strict mode
- **Code formatting** - Must pass `uv run ruff format`
- **Linting** - Must pass `uv run ruff check`
- **Custom linters** - Must pass all checks in `./quality-check.sh`

Run all checks before submitting:

```bash
./quality-check.sh
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the coding standards
3. Ensure all tests pass with 100% coverage
4. Update documentation if needed
5. Submit a pull request with a clear description

## Commit Messages

Follow conventional commits format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `ci:` CI/CD changes

## Updating llms.txt Files

When making significant changes to documentation or API:

- [ ] Update llms.txt if new documentation files are added
- [ ] Regenerate llms-full.txt using `python scripts/generate_llms_full.py`
- [ ] Verify all URLs in llms.txt are valid and accessible
- [ ] Test with an AI assistant to ensure proper understanding

## Testing Guidelines

- Write tests that demonstrate real AI orchestration patterns
- Test through public API only (no private imports)
- Ensure all state transformations are immutable
- Cover all edge cases and error conditions

## Documentation

- Keep documentation concise and factual
- Focus on what the code does, not philosophy
- Use clear examples that work exactly as shown
- Avoid marketing language or unverifiable claims

## Questions?

Open an issue for discussion before making large changes.
