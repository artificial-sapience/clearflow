# Reinforcement Design Doc Review (Session Notes)

Document: `packages/stigmergic/docs/reinforcement-design.md`
Review date: 2025-?

## Outstanding Issues Identified

1. **Constructors ignore new time types** (`packages/stigmergic/docs/reinforcement-design.md:198-229`)
   - `mkMVPAgent` still sets `lastReset := 0` instead of a `WallTime` value.
   - `mkMVPSignal` and `mkMVPReinforcement` continue to accept `Time` and never populate `wallCreated` / `wallAt`.
   - Result: snippets do not type-check under the new opaque `WallTime`/`LogicalTime` system; MVP instances cannot be created.

2. **Residual `Time` alias usage** (`573-807`, theorems at `876, 882, 900, 920`, and examples)
   - Large chunks of Part 1 still reference the removed `Time` alias in signatures, proofs, and helper code.
   - Without reintroducing the alias (which defeats the type-safety fix), the document’s code is invalid and implementers have no guidance on required types.

3. **`isSystemActive` mixes `WallTime` and `Nat`** (`375-383`)
   - Expression `tracker.wallTime - config.activityWindow` is ill-typed: no subtraction from `WallTime` to `Nat` is defined.
   - The quorum window pruning therefore cannot compile or be implemented as written.

4. **Outcome decay math still subtracts raw records** (`667-676`)
   - Lines such as `space'.currentTime - r.at` remain after switching to opaque time wrappers.
   - With `LogicalTime` now a structure, this subtraction no longer works; reinforcement decay and learning become undefined.

5. **Silent clock regression handling** (`485-511`)
   - `withTimeUpdate` and `withTimeUpdatePure` return the original space with `result := none` on clock regressions.
   - This hides critical invariant violations and leaves stale activity state; callers cannot detect the error.

6. **`SignalHold.baseInfluence` is unused** (`178-210`, `324-339`)
   - The enhanced hold structure stores `baseInfluence`, but `getCurrentInfluence` never consumes it.
   - The doc promises frozen base influence during holds, yet implementation recomputes from mutable state, undermining the “decay paused, learning active” objective.

7. **Examples still rely on unnamed placeholders** (`552-557`, `954-1013`)
   - Usage snippets use `currentTime`, `time1`, `processSignal`, `logError`, etc., without defining typed values or helpers.
   - Maintenance example still accepts `now : Time`, contradicting the new type guidance.

8. **Roadmap sections keep legacy `Time`** (`1224-1510`)
   - Future-phase designs continue to use the removed `Time` alias immediately after stressing distinct types.
   - Even though these are non-MVP, the inconsistency will derail prototypes unless updated.

## Next Steps for Future Session

- Update constructors and structure definitions to fully adopt `WallTime` / `LogicalTime`, supplying smart constructors where needed.
- Sweep Part 1 (code, proofs, examples) to replace lingering `Time` references with appropriate types.
- Define subtraction/comparison helpers for `WallTime` or adjust `isSystemActive` to operate purely on `Nat` deltas via `WallTime.toNat`.
- Fix subtraction/decay math (`space'.currentTime - r.at`, etc.) to operate on underlying `Nat` values.
- Decide on explicit error signalling for clock regressions in `withTimeUpdate` / `withTimeUpdatePure` (align with Except-wrapper behavior).
- Either remove or use `SignalHold.baseInfluence`; update design text accordingly.
- Flesh out example scaffolding so every symbol is defined and typed.
- Align roadmap sections with the dual-time model or add a note describing the necessary upgrades.

These notes capture the current review status so we can resume seamlessly next session.
