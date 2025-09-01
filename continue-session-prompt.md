# Continue ClearFlow Session

Please continue working on ClearFlow test updates.

## Context Files
- Review **session-context.md** for what was accomplished and key decisions
- Review **plan.md** for remaining tasks

## Current Priority Task

Continue updating test files to use the new builder API:
```python
# Old pattern to replace:
Flow[T]("name").start_with(node).route(...).route(..., None).build()

# New pattern to use:
flow("name", node).route(...).end(final_node, "outcome")
```

## Specific Next Steps

1. **Complete test_flow.py updates**
   - The file is partially updated (linear flow and branching flow done)
   - Check for any remaining tests that need updating

2. **Update test_real_world_scenarios.py and test_error_handling.py**
   - These files definitely use the old Flow API
   - Update to new builder pattern with AI-focused examples

3. **Check remaining test files**
   - Verify which other test files need updates
   - Update any that use the old Flow[T]().start_with() pattern

## Important Guidelines

- Use realistic AI workflows in tests (RAG, chat routing, embeddings, etc.)
- Ensure node names are meaningful (e.g., "retriever", "classifier", not "node1")
- Tests should serve as examples for users
- Maintain 100% test coverage

## Success Criteria
- All tests use the new flow() → route() → end() API
- All tests pass
- Quality check passes at 100%: `./quality-check.sh`

Start by running the quality checks against tests/

The quality checks must pass first and then the tests themselves.