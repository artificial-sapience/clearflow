# Stigmergic Reinforcement Design - Implementation Plan

## Current Status
Removing audit system from `packages/stigmergic/docs/reinforcement-design.md` while preserving accounting infrastructure and fixing BAT-Lite time management.

## REVISED PLAN: Remove Audit System with Correct Activity Tracking

### Overview
The audit system adds unnecessary complexity. We'll remove it completely while:
1. Keeping the accounting system (essential for open economy model)
2. Fixing BAT-Lite to track activity directly without audit logs
3. Ensuring pruning happens even on failed operations
4. Fixing the critical timing bug where `timeDelta = 0` when quorum is reached

### Part 1: Core Architecture Changes

#### 1.1 New Result Types
Add these types to handle operation results while preserving maintenance:

```lean
/-- Result that always includes maintained space -/
structure TimeResult (� : Type) where
  space : MVPSignalSpace  -- Always has pruned writes & updated time
  result : Option �       -- Operation result (if successful)

/-- For Except operations -/
structure TimeResultExcept (� : Type) where
  space : MVPSignalSpace
  result : Except String �
```

#### 1.2 Fix updateActiveTime (Critical Bug Fix)
Replace the broken updateActiveTime at line 327 with:

```lean
def updateActiveTime (space : MVPSignalSpace) (wallClockNow : Time)
    (writer : Option AgentId) : MVPSignalSpace :=
  let prevWallTime := space.activityTracker.wallTime
  let timeDelta := wallClockNow - prevWallTime  -- COMPUTE BEFORE ANY UPDATES

  -- Prune stale writes
  let windowStart := if wallClockNow > space.config.activityWindow then
    wallClockNow - space.config.activityWindow else 0
  let prunedWrites := space.activityTracker.recentWrites.filter
    (fun (_, t) => t >= windowStart)

  -- Add new writer if provided
  let newWrites := match writer with
    | some agentId => (agentId, wallClockNow) :: prunedWrites
    | none => prunedWrites

  -- Check activity WITH potential new writer
  let distinctWriters := newWrites.map (�.1) |>.eraseDup
  let isActive := distinctWriters.length >= space.config.minWriters

  -- Advance logical time using PRE-COMPUTED delta
  let newLogicalTime := if isActive && timeDelta > 0 then
    space.activityTracker.logicalTime + timeDelta
  else
    space.activityTracker.logicalTime

  { space with
    activityTracker := { space.activityTracker with
      recentWrites := newWrites,
      wallTime := wallClockNow,  -- Update AFTER using old value
      logicalTime := newLogicalTime },
    currentTime := newLogicalTime }
```

Key fixes:
- Compute `timeDelta` BEFORE updating `wallTime`
- Prune stale writes on every call
- Include speculative writer when checking activity
- Update `wallTime` AFTER all calculations

#### 1.3 Time Update Wrappers
Add these wrappers that guarantee maintenance:

```lean
/-- For Option-returning operations - ALWAYS returns maintained space -/
def withTimeUpdate (space : MVPSignalSpace) (wallClockNow : Time)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace � Option (MVPSignalSpace � �))
    : TimeResult � :=
  -- Update time with speculative writer
  let speculativeSpace := updateActiveTime space wallClockNow agentId

  -- Try operation
  match operation speculativeSpace with
  | none =>
    -- Failed - return maintained space WITHOUT writer
    let maintainedSpace := updateActiveTime space wallClockNow none
    { space := maintainedSpace, result := none }
  | some (mutatedSpace, value) =>
    -- Success - return mutated space WITH writer
    { space := mutatedSpace, result := some value }

/-- For Except-returning operations -/
def withTimeUpdateExcept (space : MVPSignalSpace) (wallClockNow : Time)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace � Except String (MVPSignalSpace � �))
    : TimeResultExcept � :=
  -- Update time with speculative writer
  let speculativeSpace := updateActiveTime space wallClockNow agentId

  match operation speculativeSpace with
  | .error msg =>
    -- Failed - return maintained space WITHOUT writer
    let maintainedSpace := updateActiveTime space wallClockNow none
    { space := maintainedSpace, result := .error msg }
  | .ok (mutatedSpace, value) =>
    -- Success - return mutated space WITH writer
    { space := mutatedSpace, result := .ok value }

/-- For pure operations (always succeed) -/
def withTimeUpdatePure (space : MVPSignalSpace) (wallClockNow : Time)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace � MVPSignalSpace)
    : MVPSignalSpace :=
  let updatedSpace := updateActiveTime space wallClockNow agentId
  operation updatedSpace
```

### Part 2: Remove Audit Infrastructure

#### 2.1 Delete These Completely
- Lines 140-154: Remove entire `AuditEvent` inductive type
- Line 226: Remove `auditLog : List AuditEvent` field from MVPSignalSpace
- Lines 314-324: Remove entire `extractRecentWrites` function (no longer needed)

#### 2.2 Update MVPSignalSpace Structure
At line 221, update to remove auditLog:
```lean
structure MVPSignalSpace where
  signals : List MVPSignal
  reinforcements : List MVPReinforcement
  outcomes : List MVPOutcome
  agents : List MVPAgent
  -- auditLog removed
  totalProvisioned : AttentionMinutes
  totalNetAdjustments : Real
  totalReplenished : AttentionMinutes
  currentTime : Time
  nextSignalCounter : Nat
  config : ActiveTimeConfig
  activityTracker : ActivityTracker
```

### Part 3: Update All Operations

#### 3.1 emitSignal (lines 384-416)
Change signature and remove audit:
```lean
def emitSignal (space : MVPSignalSpace) (agentId : AgentId)
    (strength : AttentionMinutes) (wallClockNow : Time)
    : TimeResult SignalId :=
  withTimeUpdate space wallClockNow (some agentId) (fun s =>
    match s.agents.find? (�.id = agentId) with
    | none => none
    | some agent =>
      if strength d (agent.dailyBudget - agent.spent) then
        let (signalId, nextCounter) := generateUniqueId s agentId
        let signal := mkMVPSignal signalId agentId s.currentTime strength

        let updatedAgent := { agent with
          spent := agent.spent + strength,
          cumulativeSpent := agent.cumulativeSpent + strength }
        let updatedAgents := s.agents.map (fun a =>
          if a.id = agent.id then updatedAgent else a)

        -- No audit event creation
        let newSpace := { s with
          signals := signal :: s.signals,
          agents := updatedAgents,
          nextSignalCounter := nextCounter }

        some (newSpace, signalId)
      else none)
```

#### 3.2 applyReinforcement (lines 424-459)
Update similarly:
```lean
def applyReinforcement (space : MVPSignalSpace) (influence : Influence)
    (signalId : SignalId) (agentId : AgentId) (wallClockNow : Time)
    : TimeResult Unit :=
  withTimeUpdate space wallClockNow (some agentId) (fun s =>
    match s.signals.find? (�.id = signalId) with
    | none => none
    | some _ =>
      match s.agents.find? (�.id = agentId) with
      | none => none
      | some agent =>
        if canReinforce agent influence then
          let attentionCost := NNReal.ofReal (abs influence)
          let r := mkMVPReinforcement signalId agentId influence agent.credibility s.currentTime

          let updatedAgent := { agent with
            spent := agent.spent + attentionCost,
            cumulativeSpent := agent.cumulativeSpent + attentionCost }
          let updatedAgents := s.agents.map (fun a =>
            if a.id = agent.id then updatedAgent else a)

          -- No audit event
          let newSpace := { s with
            reinforcements := r :: s.reinforcements,
            agents := updatedAgents }

          some (newSpace, ())
        else none)
```

#### 3.3 processOutcome (lines 461-582)
Update to use withTimeUpdatePure:
```lean
def processOutcome (space : MVPSignalSpace) (outcome : MVPOutcome)
    (wallClockNow : Time) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow none (fun s =>
    -- Core outcome processing logic (unchanged except remove audit)
    let space' := if outcome.measuredAt > s.currentTime then
      { s with currentTime := outcome.measuredAt }
    else s

    -- ... rest of logic ...
    -- Remove: let auditEvent := AuditEvent.outcomeProcessed ...

    { space' with
      signals := updatedSignals,
      reinforcements := updatedReinforcements,
      agents := updatedAgents,
      outcomes := outcome :: space'.outcomes }
      -- No auditLog update
  )
```

#### 3.4 resetBudgets (lines 585-633)
Major refactor to remove audit accumulation:
```lean
def resetBudgets (space : MVPSignalSpace) (wallClockNow : Time) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow none (fun s =>
    -- Use foldr to avoid needing reverse
    let (updatedAgents, newReplenished, newAdjustments) :=
      s.agents.foldr
        (fun agent (agents, replenished, adjustments) =>
          if wallClockNow - agent.lastReset e Constants.DAY_IN_SECONDS then
            let prevBudget := agent.dailyBudget  -- Capture BEFORE mutation
            let unspent := prevBudget - agent.spent
            let unspentRatio := if prevBudget.val > 0 then
              unspent.val / prevBudget.val else 0
            let multiplier := 0.5 + 1.5 * unspentRatio
            let newBudget := NNReal.ofReal (agent.baselineBudget.val * multiplier)

            let resetAgent := { agent with
              dailyBudget := newBudget,
              spent := �0, by norm_num�,
              lastReset := wallClockNow }

            let replenishedAmount := agent.spent
            let netAdjustment := newBudget.val - prevBudget.val

            -- No audit event creation
            (resetAgent :: agents,
             replenished + replenishedAmount,
             adjustments + netAdjustment)
          else
            (agent :: agents, replenished, adjustments))
        ([], �0, by norm_num�, (0.0 : Real))

    { s with
      agents := updatedAgents,
      totalNetAdjustments := s.totalNetAdjustments + newAdjustments,
      totalReplenished := s.totalReplenished + newReplenished }
      -- No auditLog update
  )
```

#### 3.5 provisionAgent (lines 636-646)
Update to use withTimeUpdateExcept:
```lean
def provisionAgent (space : MVPSignalSpace)
    (agentData : AgentId � Credibility � AttentionMinutes)
    (wallClockNow : Time) : TimeResultExcept Unit :=
  withTimeUpdateExcept space wallClockNow none (fun s =>
    let (id, cred, baseline) := agentData
    match mkMVPAgent id cred baseline with
    | .error msg => .error msg
    | .ok agent =>
      -- No audit event
      let newSpace := { s with
        agents := agent :: s.agents,
        totalProvisioned := s.totalProvisioned + agent.baselineBudget }
      .ok (newSpace, ()))
```

#### 3.6 holdSignal (lines 352-361)
Add wallClockNow parameter and use wrapper:
```lean
def holdSignal (space : MVPSignalSpace) (signalId : SignalId)
    (agentId : AgentId) (wallClockNow : Time) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow (some agentId) (fun s =>
    let holdUntil := s.currentTime + s.config.holdDuration
    let currentInfluence := getCurrentInfluence s signalId s.currentTime
    { s with activityTracker :=
      { s.activityTracker with
        signalHolds := (signalId, holdUntil) :: s.activityTracker.signalHolds,
        influenceCache := (signalId, currentInfluence, s.currentTime) ::
                         s.activityTracker.influenceCache }})
```

#### 3.7 releaseExpiredHolds (lines 363-368)
Add wallClockNow parameter:
```lean
def releaseExpiredHolds (space : MVPSignalSpace) (wallClockNow : Time) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow none (fun s =>
    let activeHolds := s.activityTracker.signalHolds.filter
      (fun (_, holdUntil) => holdUntil > s.currentTime)
    { s with activityTracker :=
      { s.activityTracker with signalHolds := activeHolds }})
```

### Part 4: Update Proofs and Documentation

#### 4.1 Fix accounting_integrity theorem (lines 665-673)
Update proof sketch to not reference audit:
```lean
/-- Accounting Integrity: All spent attention is tracked -/
theorem accounting_integrity (space : MVPSignalSpace) :
  let totalCumulativeSpent := space.agents.map (�.cumulativeSpent) |>.sum
  let totalInSignals := space.signals.map (�.initialStrength) |>.sum
  let totalInReinforcements := space.reinforcements.map (�.attentionSpent) |>.sum
  totalCumulativeSpent = totalInSignals + totalInReinforcements := by
  -- Proof by structural induction on operation sequences:
  -- Base: Empty space has all zeros
  -- Inductive: For each operation type:
  --   - emitSignal: adds to both cumulativeSpent and signals
  --   - applyReinforcement: adds to both cumulativeSpent and reinforcements
  --   - processOutcome: preserves equality (no spending)
  --   - resetBudgets: preserves equality (resets spent, not cumulative)
  --   - provisionAgent: preserves equality (starts at 0)
  sorry
```

#### 4.2 Update Documentation
- Line 220: Change comment from "complete tracking and audit trail" to "complete tracking"
- Line 781: Remove "Complete audit:" bullet point
- Line 1261: Change "Via audit trail invariants" to "Via structural induction"
- Lines 370-377: Update BAT-Lite comment to mention direct activity tracking

### Part 5: Usage Patterns for New Result Types

Document how callers should handle the new result types:

```lean
-- Example: Handling TimeResult
def exampleUsage (space : MVPSignalSpace) : MVPSignalSpace :=
  let result := emitSignal space "agent1" �10, by norm_num� currentTime
  match result.result with
  | none =>
    -- Operation failed, but still use maintained space
    result.space
  | some signalId =>
    -- Operation succeeded
    processSignal result.space signalId

-- Example: Chaining operations
def chainedOps (space : MVPSignalSpace) : MVPSignalSpace :=
  let emit1 := emitSignal space "agent1" �10, by norm_num� time1
  let space1 := emit1.space  -- Always updated, even if failed

  let reinforce1 := applyReinforcement space1 5 "sig1" "agent2" time2
  reinforce1.space  -- Always has maintenance
```

#### CRITICAL: Space Threading Invariant

**NEVER keep the original space after an operation**. Always use `result.space`:

```lean
/-- CRITICAL: Always use result.space, never keep the original space -/
def correctPattern (space : MVPSignalSpace) : MVPSignalSpace :=
  let result := emitSignal space "agent1" ⟨10, by norm_num⟩ currentTime
  -- ALWAYS use result.space, regardless of success/failure
  result.space  -- ✓ Correct - maintains pruning
  -- space       -- ✗ WRONG - loses maintenance, causes stale writes

/-- Example showing failure still requires space threading -/
def handleFailure (space : MVPSignalSpace) : MVPSignalSpace :=
  let result := emitSignal space "agent1" ⟨1000, by norm_num⟩ currentTime
  match result.result with
  | none =>
    -- Even on failure, MUST use result.space
    logError "Emission failed due to budget exceeded"
    result.space  -- ✓ Has pruned writes and updated time
    -- space       -- ✗ WRONG - loses maintenance
  | some signalId =>
    logInfo s!"Created signal {signalId}"
    result.space  -- ✓ Correct

/-- Anti-pattern that MUST be avoided -/
def brokenPattern (space : MVPSignalSpace) : MVPSignalSpace :=
  let result := emitSignal space "agent1" ⟨10, by norm_num⟩ currentTime
  match result.result with
  | none =>
    space  -- ✗✗ BUG: Returns unpruned space, breaks BAT-Lite!
  | some _ =>
    result.space
```

This invariant is critical because:
1. **Pruning happens in every operation** - returning original space loses this
2. **Time maintenance is mandatory** - even failed ops must update wall clock
3. **Activity tracking depends on it** - stale writes break quorum detection

### Part 6: Activity Tracking Policy

Document which operations count as "writers" for BAT-Lite:

**Count as writers (human actions):**
- `emitSignal` - Agent creating a signal
- `applyReinforcement` - Agent reinforcing a signal
- `holdSignal` - Agent placing a hold (shows engagement)

**Don't count as writers (system/evaluator actions):**
- `processOutcome` - External evaluator action
- `resetBudgets` - Scheduled system maintenance
- `provisionAgent` - Administrative action
- `releaseExpiredHolds` - Automatic cleanup

### Part 7: Inner Helper Functions

All helper functions that modify space MUST go through wrappers to ensure maintenance:

```lean
-- ✓ CORRECT: Helper uses wrapper
def someComplexOperation (space : MVPSignalSpace) (wallClockNow : Time) : MVPSignalSpace :=
  -- First release expired holds
  let space1 := releaseExpiredHolds space wallClockNow  -- Goes through wrapper
  -- Then do main operation
  let result := emitSignal space1 agentId strength wallClockNow
  result.space

-- ✗ WRONG: Direct manipulation bypasses maintenance
def brokenHelper (space : MVPSignalSpace) : MVPSignalSpace :=
  -- DON'T directly manipulate activityTracker
  { space with activityTracker := ... }  -- ✗ Bypasses pruning!
```

**Verified Helper Functions:**
- `holdSignal` - Updated to use `withTimeUpdatePure` wrapper
- `releaseExpiredHolds` - Updated to use `withTimeUpdatePure` wrapper
- No other internal helpers found that bypass the wrapper pattern

### Critical Implementation Notes

1. **Time Delta Bug Fix**: The key fix is computing `timeDelta` BEFORE updating `wallTime`. This ensures logical time advances on the same tick that reaches quorum.

2. **Guaranteed Pruning**: Every operation calls updateActiveTime which prunes stale writes, preventing unbounded growth even during long failure sequences.

3. **Speculative Writer Pattern**: Writers are added speculatively for the operation, then rolled back (by calling updateActiveTime with `none`) if the operation fails.

4. **Result Types**: TimeResult and TimeResultExcept ensure callers always get an updated space with maintenance, even on failure.

5. **No Double Updates**: Each operation calls updateActiveTime exactly once (via the wrapper), avoiding the double-update bug.

### Summary

This plan:
1. Removes all audit infrastructure (~50 lines of code)
2. Fixes the critical BAT-Lite timing bug
3. Guarantees pruning on every operation
4. Preserves accounting for the open economy model
5. Provides clear activity tracking policy
6. Ensures type safety with result wrappers
7. Enforces space threading invariant to prevent stale tracker bugs
8. Ensures all helpers use wrappers for consistent maintenance

### Open Questions (RESOLVED)

**Q: How do we ensure callers always use `result.space`?**

A: Added explicit documentation with correct/incorrect patterns, anti-patterns to avoid, and clear explanation of why this invariant is critical. The examples make it unmistakable that `result.space` must always be threaded forward.

**Q: Do inner helpers need to use wrappers?**

A: Yes, verified that both `holdSignal` and `releaseExpiredHolds` are updated in the plan to use wrappers. No other helpers found that could bypass maintenance. Added documentation warning against direct activityTracker manipulation.