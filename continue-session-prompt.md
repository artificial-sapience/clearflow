# Continue Session: Fix Architecture Violations

Please continue working on the ClearFlow quality improvements.

## Context
See `session-context.md` for complete background. We successfully completed PLR6301 test method conversion and implemented abstract Command/Event classes with a custom metaclass.

## Current Blocker: Architecture Violations

The quality check is failing with 4 ARCH010 violations in the metaclass implementation:

```
clearflow/message.py:7:0
  ARCH010: Importing 'Any' type defeats type safety
clearflow/message.py:19:29, 19:44, 19:52  
  ARCH010: Using 'Any' type defeats type safety
```

The issue is in our `AbstractMessageMeta.__call__` method that uses `Any` for args/kwargs.

## Immediate Task

**Fix the Any type usage in AbstractMessageMeta** while maintaining functionality.

### Options to Consider:
1. Replace `Any` with specific types (though metaclass signatures traditionally use Any)
2. Use `*args: object, **kwargs: object` instead
3. Define a Protocol for the expected signature
4. Request architectural exception for metaclass patterns

## Expected Outcome

After fixing the architecture violations:
- Run `./quality-check.sh` - should pass architecture compliance
- All 86 tests should still pass
- Command/Event instantiation prevention should still work

## Next Steps

Once architecture violations are resolved:
1. Address remaining ~76 pyright type errors in flow routing
2. Restore test coverage to 100%

See `plan.md` for complete task list and priorities.