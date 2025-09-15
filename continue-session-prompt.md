# Continue Session Prompt

Please read @session-context.md and @plan.md to understand our progress.

## Current Priority

We need to complete the `_internal/` architecture restructuring to solve the pyright private usage errors with `_NodeInterface`.

## Next Immediate Tasks

1. **Create _internal/ directory structure**
2. **Move all implementations to _internal/**
3. **Create public wrapper modules at root**
4. **Update imports throughout codebase**

## Key Context

- We've already simplified naming (Node, flow) and cleaned up all legacy references
- The `_NodeInterface` currently causes pyright errors when used across modules
- Solution: Move to `_internal/` pattern where NodeInterface won't need underscore prefix
- All examples now use simplified directory names without `_message_driven` suffix

## Success Criteria

- No pyright errors about private usage
- Clear public/private API boundaries
- All tests and examples use only public imports
- Quality checks pass 100%

Please continue with the _internal/ restructuring per the plan.