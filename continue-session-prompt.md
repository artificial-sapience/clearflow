# Continue Session: Stigmergic Coordination Lean4 Specification

Please continue our work on formally specifying the Stigmergic Coordination MVP in Lean 4.

## Context
Read @session-context.md for the current state of our work. The plan and task list are in @plan.md.

## Current Issue
We are fixing compilation errors in `Primitives.lean`. The `Metadata` structure needs its operations updated to work with the new format. We cannot use linter suppressions (except `linter.minImports false`).

## Immediate Task
Fix the remaining compilation error in `/packages/stigmergic/lean/Stigmergic/Foundation/Primitives.lean`:

1. Update all Metadata operations to use the new structure format
2. Run `lake build` from the lean directory to verify compilation
3. Once Primitives.lean compiles, create Trace.lean following our Lean4 standards

## Standards
Follow @packages/stigmergic/lean4-spec-standard/ exactly:
- All public declarations need documentation with PURPOSE, PRECONDITIONS, POSTCONDITIONS, INVARIANTS
- Bijective correspondence between math and English
- No linter suppressions except minImports
- Proof-carrying types where properties matter

## Important Files
- Theory: @packages/stigmergic/docs/stigmergic-coordination-theory.md
- Current work: @packages/stigmergic/lean/Stigmergic/Foundation/Primitives.lean
- Reference: @packages/stigmergic/lean-reference/lean/ for patterns

Please proceed methodically, ensuring each type is fully specified and proven correct before moving to the next.