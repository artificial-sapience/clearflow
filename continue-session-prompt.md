# Continue Pydantic Migration Session

Please read the following context files to understand the current state:

1. @session-context.md - Full context from previous session
2. @plan.md - Remaining tasks and current progress

## Current Task

We're migrating ClearFlow from vanilla dataclasses to Pydantic dataclasses for maximum type safety and validation. We've completed Phases 1-3 but hit a blocker in Phase 4.

## Immediate Priority

**Resolve MessageFlow inheritance issue**: MessageFlow inherits from Node (now a Pydantic dataclass) but itself uses vanilla `@dataclass`, causing ~76 type errors.

**Your task**:

1. Analyze why MessageFlow can't simply use `@strict_dataclass`
2. Propose and implement a solution that uses `@strict_dataclass`
3. Ensure both MessageFlow and _MessageFlowBuilder are properly migrated
4. Run `./quality-check.sh clearflow/message_flow.py` to verify

## Constraints

- Prefer maximum strictness (use `@strict_dataclass` wherever possible)
- Maintain 100% quality check compliance
- Don't use suppressions without explicit approval
- Follow patterns established in session-context.md

## Success Criteria

- MessageFlow properly inherits from Pydantic Node
- Zero type errors in message_flow.py
- Quality check passes 100%

After resolving MessageFlow, we'll tackle the test suite updates (Phase 6) where ~300+ test message classes need migration to `@strict_dataclass`.

Let's continue where we left off!
