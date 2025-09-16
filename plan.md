# Plan: Critical Type Safety Fix for Terminal Type Pattern

## CRITICAL ISSUE: PEP 695 Variance Inference Breaks Type Safety

The terminal type pattern's type safety is compromised because PEP 695 automatically infers:
- `TMessageIn` as **contravariant** (only in input position)
- `TMessageOut` as **covariant** (only in output position)

This allows `Node[StartChat, ChatCompleted]` to be assignable to `Node[StartChat, UserMessageReceived | ChatCompleted]`, which breaks our single terminal type guarantee.

## Priority Tasks

### Task 1: Fix Variance Issue (CRITICAL)
**Status**: Investigation complete, solution needed

Options to explore:
1. **Switch to traditional TypeVars** with explicit invariance
2. **Add dummy usage** to force invariance inference
3. **Restructure Node interface** to prevent covariance
4. **Document the limitation** and fix incorrect type annotations

### Task 2: Fix Incorrect Type Annotations
**Status**: Pending

Files with incorrect union return types:
- `examples/chat/chat_flow.py`: Should return `Node[StartChat, ChatCompleted]` not union
- Review all other examples for similar issues

### Task 3: Add Type Safety Tests
**Status**: Not started

Create tests that would catch variance issues:
- Test that flow return types match their terminal types
- Test that union types are not allowed where single types are expected
- Consider adding a custom linter rule

### Task 4: Version and Release
**Status**: Not started

After fixing type safety:
1. Decide version bump (2.0.1 for bugfix or 2.1.0 for API change)
2. Update changelog with variance fix
3. Document breaking changes if API changes

## Success Criteria

1.  Terminal type pattern fully documented
2.  All "zero dependencies" claims updated to "minimal dependencies"
3.    Type system enforces single terminal types (BLOCKED by variance issue)
4. ó All examples use correct type annotations
5. ó Type safety tests prevent future regressions