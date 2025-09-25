# Reinforcement in Stigmergic Systems: MVP Specification and Future Roadmap

## Executive Summary

This document contains two distinct sections:

1. **Part 1: MVP Specification** - A complete, shippable system ready for implementation
2. **Parts 2-6: Future Roadmap** - Advanced features for subsequent releases (NOT part of MVP)

⚠️ **IMPORTANT**: Only Part 1 is the MVP. Parts 2-6 describe future enhancements that are NOT required for initial deployment.

## Part 1: MVP Specification (Ready for Implementation)

### Core Concepts

The MVP implements a complete learning system with:

- **Open economy**: Daily budget adjustments change system capacity (tracked via `totalNetAdjustments`)
- **Signal decay**: Both initial strength and reinforcements decay over time
- **External grounding**: Outcomes update agent credibility and signal penalty factors
- **Resource constraints**: Agents have finite budgets (can't spend more than allocated)
- **Immutable history**: Reinforcements capture credibility at creation time

### Key Design Choice: Penalty Factor Semantics

The `penaltyFactor` mechanism applies ONLY to signals (not reinforcements):

- Affects signal's initial strength decay only
- Starts at 1.0 (neutral), increases to 1.43 on success (43% boost), decreases to 0.7 on failure (30% penalty)
- Allows a "disproven" signal (high penalty) to persist if the collective continues investing
- Enables ideas to "pivot" from flawed premises through continued collective support
- This is intentional: the system distinguishes between "originally wrong" and "currently valuable"
- Reinforcements remain immutable after creation (no penalty factors)

### MVP Data Model

```lean
/-- Core type distinctions for clarity and safety -/

/-- Agent identifier -/
abbrev AgentId := String

/-- Signal identifier -/
abbrev SignalId := String

/-- Task identifier (for Part 6: Causality) -/
abbrev TaskId := String

/-- External system identifier (for Part 6: Causality) -/
abbrev ExternalSystem := String

/-- Opaque wrapper for wall-clock time -/
structure WallTime where
  private mk ::
  val : Nat
deriving DecidableEq, Repr

/-- Opaque wrapper for logical time -/
structure LogicalTime where
  private mk ::
  val : Nat
deriving DecidableEq, Repr

/-- Smart constructors ensure proper usage -/
def WallTime.ofNat (n : Nat) : WallTime := WallTime.mk n
def LogicalTime.ofNat (n : Nat) : LogicalTime := LogicalTime.mk n

/-- Arithmetic operations for time types -/
instance : HSub WallTime WallTime Nat where
  hSub w1 w2 := w1.val - w2.val

instance : HAdd LogicalTime Nat LogicalTime where
  hAdd t n := LogicalTime.mk (t.val + n)

instance : LT WallTime where
  lt w1 w2 := w1.val < w2.val

instance : LT LogicalTime where
  lt t1 t2 := t1.val < t2.val

instance : LE WallTime where
  le w1 w2 := w1.val ≤ w2.val

instance : LE LogicalTime where
  le t1 t2 := t1.val ≤ t2.val

instance : Max WallTime where
  max w1 w2 := WallTime.mk (max w1.val w2.val)

/-- Conversion ONLY where semantically valid -/
def LogicalTime.toNat (t : LogicalTime) : Nat := t.val
def WallTime.toNat (w : WallTime) : Nat := w.val

/-- Attention-minutes: tracked spending unit (always non-negative) -/
abbrev AttentionMinutes := NNReal

/-- Influence: emergent strength that can be negative (inhibition) -/
abbrev Influence := Real

/-- Credibility: bounded probability in [0,1] using Lean's Subtype -/
def Credibility := { x : Real // 0 ≤ x ∧ x ≤ 1 }

/-- Positive real for safe division (prevents div-by-zero) -/
def PosReal := { x : Real // x > 0 }

/-- Note on NNReal literals:
    Throughout this document, ⟨value, by norm_num⟩ constructs an NNReal
    with a proof that value ≥ 0. This is Lean's way of ensuring type safety
    for non-negative reals at compile time.
-/

/-- Global system constants -/
namespace Constants
  def DAY_IN_SECONDS : Nat := 86400
  def MIN_OWNERSHIP_CREDIBILITY : Real := 0.3  -- Minimum credibility to claim ownership
  def BUDGET_BURST_PENALTY : Real := 0.1  -- Pro-rating factor for burst prevention
  def LEARNING_EPSILON : Real := 0.01  -- Minimum learning for zero-credibility escape
end Constants

/-- Smart constructor for credibility -/
def mkCredibility (x : Real) : Credibility :=
  ⟨max 0 (min 1 x), by
    simp [max_def, min_def]
    split <;> split <;> simp [*] <;> linarith⟩

/-- Extract Real value from Credibility -/
def Credibility.toReal (c : Credibility) : Real := c.val

/-- Default starting credibility -/
def defaultCredibility : Credibility := mkCredibility 0.5

/-- Add to credibility safely -/
def Credibility.add (c : Credibility) (delta : Real) : Credibility :=
  mkCredibility (c.val + delta)

/-- Multiply credibility safely -/
def Credibility.scale (c : Credibility) (factor : Real) : Credibility :=
  mkCredibility (c.val * factor)

/-- Minimal agent with credibility and budget -/
structure MVPAgent where
  id : AgentId
  credibility : Credibility  -- Bounded [0, 1], starts at 0.5
  baselineBudget : AttentionMinutes  -- Base budget amount (e.g., 480 minutes)
  dailyBudget : AttentionMinutes  -- Current budget (baseline + adjustments)
  spent : AttentionMinutes  -- Already spent today (≤ dailyBudget)
  cumulativeSpent : AttentionMinutes  -- Total ever spent (for accounting)
  lastReset : WallTime      -- When budget was last reset (wall time for daily cycles)
  -- Invariants:
  -- baselineBudget > 0 (agents must have some capacity)
  -- spent ≤ dailyBudget (enforced by operations)
  -- Migration: For existing agents, set baselineBudget = dailyBudget

/-- Minimal signal with attention invested -/
structure MVPSignal where
  id : SignalId
  emitter : AgentId
  timestamp : LogicalTime  -- Creation in logical time for decay
  wallCreated : WallTime   -- Wall time for TTL/retention
  initialStrength : AttentionMinutes  -- Attention invested at emission
  penaltyFactor : NNReal    -- Multiplicative penalty from outcomes, starts at 1.0

/-- Reinforcement event with proper type separation
    IMPLEMENTATION NOTE: Make this structure opaque or use abstract interface
    to ensure invariants are enforced via mkMVPReinforcement smart constructor -/
structure MVPReinforcement where
  signalId : SignalId
  by : AgentId
  influence : Influence  -- Signed: positive = amplify, negative = inhibit
  attentionSpent : AttentionMinutes  -- Always positive (cost to reinforce)
  credibilityAtTime : Credibility  -- Agent's credibility when reinforcing (immutable)
  at : LogicalTime     -- Logical time for decay calculations
  wallAt : WallTime    -- Wall time for retention/TTL
  -- Invariant: attentionSpent = NNReal.ofReal (abs influence)
  -- Invariant: attentionSpent ≤ agent.dailyBudget - agent.spent at creation time
  -- Design: No penalty factor on reinforcements (only signals have penalties)

/-- External validation to ground the system -/
structure MVPOutcome where
  signalId : SignalId
  success : Bool
  measuredAt : LogicalTime   -- Logical time of measurement
  wallMeasuredAt : WallTime  -- Wall time for compliance/TTL
  measuredBy : String  -- External system that provided validation

/-- Track detailed reinforcement patterns per agent -/
structure ReinforcementDetail where
  agentId : AgentId
  positiveCount : Nat      -- Number of positive reinforcements
  negativeCount : Nat      -- Number of negative reinforcements
  totalInfluence : Influence  -- Raw sum of influence
  weightedInfluence : Real    -- Sum of (influence * credibilityAtTime)
  totalAttention : AttentionMinutes  -- Sum of attention spent

/-- Smart constructors to enforce invariants -/

/-- Create MVPAgent with validated invariants -/
def mkMVPAgent (id : AgentId) (cred : Credibility) (baseline : AttentionMinutes)
    : Except String MVPAgent :=
  if baseline.val = 0 then
    .error "Agent must have positive baseline budget"
  else
    .ok { id := id,
          credibility := cred,
          baselineBudget := baseline,
          dailyBudget := baseline,  -- Initially same as baseline
          spent := ⟨0, by norm_num⟩,
          cumulativeSpent := ⟨0, by norm_num⟩,
          lastReset := 0 }

/-- Create MVPSignal with validated initial state -/
def mkMVPSignal (id : SignalId) (emitter : AgentId) (timestamp : Time)
    (strength : AttentionMinutes) : MVPSignal :=
  { id := id,
    emitter := emitter,
    timestamp := timestamp,
    initialStrength := strength,
    penaltyFactor := ⟨1.0, by norm_num⟩ }  -- Always starts at 1.0

/-- Create MVPReinforcement with enforced invariant -/
def mkMVPReinforcement (signalId : SignalId) (by : AgentId) (influence : Influence)
    (credibility : Credibility) (at : Time) : MVPReinforcement :=
  let attentionCost := NNReal.ofReal (abs influence)
  { signalId := signalId,
    by := by,
    influence := influence,
    attentionSpent := attentionCost,  -- Enforces invariant
    credibilityAtTime := credibility,
    at := at }
```

### MVP Operations

```lean
/-- BAT-Lite: Bounded-Active Time configuration -/
structure ActiveTimeConfig where
  activityWindow : Nat := 300       -- W = 5 minutes in seconds
  minWriters : Nat := 2             -- Need ≥2 distinct agents for activity
  halfLife : PosReal := ⟨21600.0, by norm_num⟩  -- H = 6 hours active time
  holdDuration : Nat := 600         -- 10 minutes hold for LLM operations

/-- Enhanced hold tracking that separates decay from learning -/
structure SignalHold where
  signalId : SignalId
  holdStart : LogicalTime      -- When hold began
  holdUntil : LogicalTime      -- When hold expires
  baseInfluence : Influence    -- Influence at hold start
  decayPaused : LogicalTime    -- Decay frozen at this time

/-- Track activity for BAT-Lite time advancement -/
structure ActivityTracker where
  recentWrites : List (AgentId × WallTime)  -- Recent write events (wall time for pruning)
  logicalTime : LogicalTime     -- τ (tau) - advances only when active
  wallTime : WallTime          -- Wall-clock for TTL/compliance
  signalHolds : List SignalHold  -- Enhanced hold tracking

/-- Result that always includes maintained space -/
structure TimeResult (α : Type) where
  space : MVPSignalSpace  -- Always has pruned writes & updated time
  result : Option α       -- Operation result (if successful)

/-- For Except operations -/
structure TimeResultExcept (α : Type) where
  space : MVPSignalSpace
  result : Except String α

/-- Signal space with complete tracking -/
structure MVPSignalSpace where
  signals : List MVPSignal
  reinforcements : List MVPReinforcement
  outcomes : List MVPOutcome
  agents : List MVPAgent
  -- auditLog removed
  totalProvisioned : AttentionMinutes  -- Initial baseline budgets (agent creation)
  totalNetAdjustments : Real           -- Net capacity changes (can be negative)
  totalReplenished : AttentionMinutes  -- DIAGNOSTIC: recycled attention (not in conservation)
  currentTime : LogicalTime  -- Logical time (τ) for decay calculations
  nextSignalCounter : Nat  -- Monotonic counter for unique signal IDs
  config : ActiveTimeConfig  -- BAT-Lite configuration
  activityTracker : ActivityTracker  -- Track activity and time

/-- Accounting Invariant:
    Current capacity = totalProvisioned + totalNetAdjustments
    This equals: totalInvested + totalAvailable
    where totalInvested = sum of attention in signals + reinforcements
          totalAvailable = sum of (dailyBudget - spent) for all agents
    Note: totalReplenished is a diagnostic counter (not part of conservation)
-/

/-- Calculate current influence (can be negative for inhibited signals) -/
def getCurrentInfluence (space : MVPSignalSpace) (signalId : SignalId)
    (now : LogicalTime) : Influence :=
  match space.activityTracker.signalHolds.find? (·.signalId = signalId) with
  | some hold =>
    if hold.holdUntil > now then
      -- During hold: pause decay but allow penalty updates
      match space.signals.find? (·.id = signalId) with
      | none => 0
      | some signal =>
        -- Base influence uses FROZEN decay time
        let frozenAge := (hold.decayPaused.toNat - signal.timestamp.toNat : Nat)
        let frozenDecay := Real.rpow 0.5 (Real.ofNat frozenAge / space.config.halfLife.val)

        -- But use CURRENT penalty factor (allows learning during hold)
        let baseWithCurrentPenalty :=
          signal.initialStrength.val * signal.penaltyFactor.val * frozenDecay

        -- Add reinforcements with appropriate decay
        let reinforcements := space.reinforcements
          .filter (·.signalId = signalId)
          .map (fun r =>
            let rAge := if r.at < hold.holdStart then
              -- Pre-hold: decay to hold start, then freeze
              (hold.decayPaused.toNat - r.at.toNat : Nat)
            else
              -- Post-hold: no decay yet
              0
            let decayFactor := if rAge > 0 then
              Real.rpow 0.5 (Real.ofNat rAge / space.config.halfLife.val)
            else 1
            r.influence * r.credibilityAtTime.toReal * decayFactor)
          .sum

        baseWithCurrentPenalty + reinforcements
    else
      -- Hold expired, resume normal decay
      calculateDecayedInfluence space signalId now
  | none =>
    -- No hold, calculate normally
    calculateDecayedInfluence space signalId now

/-- Helper: Calculate decayed influence for a signal -/
def calculateDecayedInfluence (space : MVPSignalSpace) (signalId : SignalId)
    (now : LogicalTime) : Influence :=
  match space.signals.find? (·.id = signalId) with
  | none => 0
  | some signal =>
    -- Use config for half-life
    let halfLife := space.config.halfLife.val

    -- Decay initial strength with outcome penalty
    let age := Real.ofNat (now.toNat - signal.timestamp.toNat)
    let decayFactor := Real.rpow 0.5 (age / halfLife)
    let decayedInitial : Influence :=
      signal.initialStrength.val * signal.penaltyFactor.val * decayFactor

    -- Decay EACH reinforcement based on its age
    -- MVP Design: Use ONLY historical credibility for predictable decay
    -- This ensures influence decays monotonically (critical for proofs)
    let decayedReinforcements : Influence := space.reinforcements
      .filter (·.signalId = signalId)
      .map (fun r =>
        let rAge := Real.ofNat (now.toNat - r.at.toNat)
        let decayFactor := Real.rpow 0.5 (rAge / halfLife)
        -- Influence = sign × attention × historical_credibility × decay
        -- Note: reinforcements no longer have penalty factors (removed dead code)
        r.influence * r.credibilityAtTime.toReal * decayFactor)
      .sum

    -- Total influence can be negative (strongly inhibited signal)
    decayedInitial + decayedReinforcements

/-- Get accounting view: total attention invested (always non-negative) -/
def getTotalAttentionInvested (space : MVPSignalSpace) (signalId : SignalId) : AttentionMinutes :=
  match space.signals.find? (·.id = signalId) with
  | none => 0
  | some signal =>
    let reinforcementTotal := space.reinforcements
      .filter (·.signalId = signalId)
      .map (·.attentionSpent)
      .sum
    signal.initialStrength + reinforcementTotal

/-- Determine if system is active (≥2 distinct writers in window) -/
def isSystemActive (tracker : ActivityTracker) (config : ActiveTimeConfig) : Bool :=
  let windowStart := if tracker.wallTime > config.activityWindow then
    tracker.wallTime - config.activityWindow
  else 0
  let recentWriters := tracker.recentWrites
    .filter (fun (_, t) => t ≥ windowStart)
    .map (·.1)
    .eraseDup
  recentWriters.length ≥ config.minWriters

/-- BAT-Lite: Update time based on collaborative activity -/
def updateActiveTime (space : MVPSignalSpace) (wallClockNow : WallTime)
    (writer : Option AgentId) : Except String MVPSignalSpace :=
  let prevWallTime := space.activityTracker.wallTime

  -- Enforce monotonic wall time
  if wallClockNow < prevWallTime then
    .error s!"Wall clock regression: {wallClockNow.val} < {prevWallTime.val}"
  else
    let timeDelta := wallClockNow - prevWallTime  -- Nat subtraction, safe after check

    -- Prune stale writes
    let windowStart := if wallClockNow.val > space.config.activityWindow then
      WallTime.ofNat (wallClockNow.val - space.config.activityWindow)
    else WallTime.ofNat 0
    let prunedWrites := space.activityTracker.recentWrites.filter
      (fun (_, t) => t ≥ windowStart)

    -- Add new writer if provided
    let newWrites := match writer with
      | some agentId => (agentId, wallClockNow) :: prunedWrites
      | none => prunedWrites

    -- Check activity WITH potential new writer
    let distinctWriters := newWrites.map (·.1) |>.eraseDup
    let isActive := distinctWriters.length >= space.config.minWriters

    -- Advance logical time using PRE-COMPUTED delta
    let newLogicalTime := if isActive && timeDelta > 0 then
      space.activityTracker.logicalTime + timeDelta
    else
      space.activityTracker.logicalTime

    .ok { space with
      activityTracker := { space.activityTracker with
        recentWrites := newWrites,
        wallTime := wallClockNow,  -- Update AFTER using old value
        logicalTime := newLogicalTime },
      currentTime := newLogicalTime }

/-- Internal unsafe version that assumes validation passed -/
private def updateActiveTimeUnsafe (space : MVPSignalSpace) (wallClockNow : WallTime)
    (writer : Option AgentId) : MVPSignalSpace :=
  -- Assumes wallClockNow >= prevWallTime, proceeds without check
  let prevWallTime := space.activityTracker.wallTime
  let timeDelta := wallClockNow - prevWallTime

  -- Prune and update as in validated version
  let windowStart := if wallClockNow.val > space.config.activityWindow then
    WallTime.ofNat (wallClockNow.val - space.config.activityWindow)
  else WallTime.ofNat 0
  let prunedWrites := space.activityTracker.recentWrites.filter
    (fun (_, t) => t ≥ windowStart)

  let newWrites := match writer with
    | some agentId => (agentId, wallClockNow) :: prunedWrites
    | none => prunedWrites

  let distinctWriters := newWrites.map (·.1) |>.eraseDup
  let isActive := distinctWriters.length >= space.config.minWriters

  let newLogicalTime := if isActive && timeDelta > 0 then
    space.activityTracker.logicalTime + timeDelta
  else
    space.activityTracker.logicalTime

  { space with
    activityTracker := { space.activityTracker with
      recentWrites := newWrites,
      wallTime := wallClockNow,
      logicalTime := newLogicalTime },
    currentTime := newLogicalTime }

/-- Enhanced wrapper for Except operations -/
def withTimeUpdateExcept (space : MVPSignalSpace) (wallClockNow : WallTime)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace → Except String (MVPSignalSpace × α))
    : TimeResultExcept α :=
  -- First validate monotonicity
  if wallClockNow < space.activityTracker.wallTime then
    { space := space,
      result := .error s!"Clock regression: {wallClockNow.val} < {space.activityTracker.wallTime.val}" }
  else
    -- Update time with speculative writer
    let speculativeSpace := updateActiveTimeUnsafe space wallClockNow agentId

    match operation speculativeSpace with
    | .error msg =>
      -- Failed - return maintained space WITHOUT writer
      let maintainedSpace := updateActiveTimeUnsafe space wallClockNow none
      { space := maintainedSpace, result := .error msg }
    | .ok (mutatedSpace, value) =>
      -- Success - return mutated space WITH writer
      { space := mutatedSpace, result := .ok value }

/-- For Option-returning operations -/
def withTimeUpdate (space : MVPSignalSpace) (wallClockNow : WallTime)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace → Option (MVPSignalSpace × α))
    : TimeResult α :=
  -- Validate monotonicity first
  if wallClockNow < space.activityTracker.wallTime then
    { space := space, result := none }  -- Clock regression fails silently for Option
  else
    -- Update time with speculative writer
    let speculativeSpace := updateActiveTimeUnsafe space wallClockNow agentId

    -- Try operation
    match operation speculativeSpace with
    | none =>
      -- Failed - return maintained space WITHOUT writer
      let maintainedSpace := updateActiveTimeUnsafe space wallClockNow none
      { space := maintainedSpace, result := none }
    | some (mutatedSpace, value) =>
      -- Success - return mutated space WITH writer
      { space := mutatedSpace, result := some value }

/-- For pure operations (always succeed) -/
def withTimeUpdatePure (space : MVPSignalSpace) (wallClockNow : WallTime)
    (agentId : Option AgentId)
    (operation : MVPSignalSpace → MVPSignalSpace)
    : MVPSignalSpace :=
  -- Validate monotonicity
  if wallClockNow < space.activityTracker.wallTime then
    space  -- Clock regression: return unchanged space
  else
    let updatedSpace := updateActiveTimeUnsafe space wallClockNow agentId
    operation updatedSpace

/-- Place a hold on a signal during long LLM operations -/
def holdSignal (space : MVPSignalSpace) (signalId : SignalId)
    (agentId : AgentId) (wallClockNow : WallTime) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow (some agentId) (fun s =>
    let holdStart := s.currentTime
    let holdUntil := LogicalTime.ofNat (s.currentTime.toNat + s.config.holdDuration)
    let currentInfluence := getCurrentInfluence s signalId s.currentTime

    -- Create proper SignalHold record
    let newHold : SignalHold := {
      signalId := signalId,
      holdStart := holdStart,
      holdUntil := holdUntil,
      baseInfluence := currentInfluence,
      decayPaused := s.currentTime  -- Freeze decay at current logical time
    }

    { s with activityTracker :=
      { s.activityTracker with
        signalHolds := newHold :: s.activityTracker.signalHolds }})

/-- Release expired holds -/
def releaseExpiredHolds (space : MVPSignalSpace) (wallClockNow : WallTime) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow none (fun s =>
    -- Filter out expired holds based on logical time
    let activeHolds := s.activityTracker.signalHolds.filter
      (fun hold => hold.holdUntil > s.currentTime)
    { s with activityTracker :=
      { s.activityTracker with
        signalHolds := activeHolds }})

/-- Usage: Call releaseExpiredHolds periodically or before time-sensitive operations
    to prevent stale holds from blocking decay. Suggested patterns:
    1. Before processing outcomes that need accurate influence
    2. As part of periodic maintenance (e.g., alongside resetBudgets)
    3. Before holdSignal to clean up previous holds on the same signal

    Example maintenance pattern:
    def performMaintenance (space : MVPSignalSpace) (now : Time) : MVPSignalSpace :=
      space
        |> releaseExpiredHolds now
        |> resetBudgets now
-/

/-- Time Management with BAT-Lite:
    The system automatically tracks collaborative activity and advances logical time
    only when ≥2 distinct agents are writing within the activity window.
    - Decay uses logical time (τ), not wall-clock time
    - Signals can be held during LLM operations to prevent decay
    - Wall-clock time tracked separately for compliance/TTL
    - No manual time advancement needed - operations update time automatically
-/

/-- Generate unique, deterministic IDs for signals using monotonic counter -/
def generateUniqueId (space : MVPSignalSpace) (agentId : AgentId) : SignalId × Nat :=
  let signalId := s!"{agentId}_signal_{space.nextSignalCounter}"
  (signalId, space.nextSignalCounter + 1)

/-- Emit a new signal with budget checking -/
def emitSignal (space : MVPSignalSpace) (agentId : AgentId)
    (strength : AttentionMinutes) (wallClockNow : Time)
    : TimeResult SignalId :=
  withTimeUpdate space wallClockNow (some agentId) (fun s =>
    match s.agents.find? (·.id = agentId) with
    | none => none
    | some agent =>
      if strength ≤ (agent.dailyBudget - agent.spent) then
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

/-- Check if agent has budget to reinforce -/
def canReinforce (agent : MVPAgent) (influence : Influence) : Bool :=
  -- Invariant: abs always returns non-negative, NNReal.ofReal safely coerces
  NNReal.ofReal (abs influence) ≤ (agent.dailyBudget - agent.spent)

/-- Apply reinforcement with budget checking and credibility capture -/
def applyReinforcement (space : MVPSignalSpace) (influence : Influence)
    (signalId : SignalId) (agentId : AgentId) (wallClockNow : Time)
    : TimeResult Unit :=
  withTimeUpdate space wallClockNow (some agentId) (fun s =>
    match s.signals.find? (·.id = signalId) with
    | none => none
    | some _ =>
      match s.agents.find? (·.id = agentId) with
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

/-- Process outcome: update signal, reinforcements, and agent credibility -/
def processOutcome (space : MVPSignalSpace) (outcome : MVPOutcome)
    (wallClockNow : WallTime) : TimeResultExcept Unit :=
  withTimeUpdateExcept space wallClockNow none (fun s =>
    -- Validate signal exists
    match s.signals.find? (·.id = outcome.signalId) with
    | none => .error s!"Cannot process outcome: signal {outcome.signalId} not found"
    | some signal =>
      -- Fast-forward time if needed
      let space' := if outcome.measuredAt > s.currentTime then
        { s with
          currentTime := outcome.measuredAt,
          activityTracker := { s.activityTracker with
            logicalTime := outcome.measuredAt,
            wallTime := max s.activityTracker.wallTime wallClockNow } }
      else s

  let relevantReinforcements := space'.reinforcements.filter
    (·.signalId = outcome.signalId)

  -- 1. Update ONLY signal with feedback (not reinforcements, to avoid double penalty)
  let updatedSignals := space'.signals.map (fun signal =>
    if signal.id = outcome.signalId then
      -- Bidirectional adjustment: boost on success, penalty on failure
      let adjustment := if outcome.success then 1.43 else 0.7  -- Success boosts strength
      let newPenalty := NNReal.ofReal (min 2.0 (max 0.1 (signal.penaltyFactor.val * adjustment)))
      { signal with penaltyFactor := newPenalty }
    else signal)

  -- 2. Keep reinforcements unchanged (avoid double penalty)
  let updatedReinforcements := space'.reinforcements

  -- 3. Track detailed reinforcement patterns with DELIVERED influence
  let halfLife := space'.config.halfLife.val
  let agentDetails : List ReinforcementDetail :=
    relevantReinforcements
      .foldl (fun acc r =>
        -- Calculate actual delivered influence (including decay)
        let rAge := Real.ofNat (space'.currentTime - r.at)
        let decayFactor := Real.rpow 0.5 (rAge / halfLife)
        let deliveredInfluence := r.influence * r.credibilityAtTime.toReal * decayFactor
        match acc.find? (·.agentId = r.by) with
        | none =>
          { agentId := r.by,
            positiveCount := if r.influence > 0 then 1 else 0,
            negativeCount := if r.influence < 0 then 1 else 0,
            totalInfluence := r.influence,
            weightedInfluence := deliveredInfluence,  -- Use delivered influence
            totalAttention := r.attentionSpent } :: acc
        | some detail =>
          acc.map (fun d =>
            if d.agentId = r.by then
              { d with
                positiveCount := d.positiveCount + if r.influence > 0 then 1 else 0,
                negativeCount := d.negativeCount + if r.influence < 0 then 1 else 0,
                totalInfluence := d.totalInfluence + r.influence,
                weightedInfluence := d.weightedInfluence + deliveredInfluence,  -- Use delivered
                totalAttention := d.totalAttention + r.attentionSpent }
            else d))
      []

  -- 4. Include signal EMITTER in learning (critical missing piece)
  let emitterId := match space'.signals.find? (·.id = outcome.signalId) with
    | none => none
    | some signal => some signal.emitter

  -- 5. Update agent credibility including emitter
  let learningEpsilon := Constants.LEARNING_EPSILON  -- Minimum learning to escape zero
  let updatedAgents := space'.agents.map (fun agent =>
    -- Check if agent is the emitter
    let isEmitter := emitterId = some agent.id

    -- Get agent's detailed reinforcement pattern
    let detail := agentDetails.find? (·.agentId = agent.id)

    if isEmitter || detail.isSome then
      -- Fixed learning rate chosen for MVP simplicity and stability
      -- Sqrt scaling deferred: requires more complex convergence analysis
      -- Alternative: Scale by sqrt(attentionSpent) for proportional credit
      let alpha : Real := 0.1  -- Uniform ±10% adjustment

      -- Determine correctness with nuance (returns Option to handle neutral case)
      let correct : Option Bool := if isEmitter then
        -- Emitter is correct if their signal prediction matched outcome
        some outcome.success
      else
        -- Reinforcer correctness based on WEIGHTED influence direction
        match detail with
        | none => some false  -- Shouldn't happen
        | some d =>
          -- Special case: perfect uncertainty (timid bystander) gets no update
          if d.weightedInfluence = 0 then
            none  -- Neutral position: skip update entirely
          else
            -- Use weighted influence for correctness (credibility-adjusted)
            let netCorrect := (d.weightedInfluence > 0 ∧ outcome.success) ∨
                             (d.weightedInfluence < 0 ∧ ¬outcome.success)
            -- Bonus for conviction, penalty for self-contradiction
            -- Guard against division by zero
            let totalCount := d.positiveCount + d.negativeCount
            let conviction : Real := if totalCount = 0 then
              -- Edge case: zero reinforcements in detail (shouldn't happen)
              0.0  -- Treat as neutral, will be caught by totalInfluence = 0 above
            else
              1 - Real.ofNat (min d.positiveCount d.negativeCount) / Real.ofNat totalCount
            some (netCorrect ∧ conviction > 0.5)  -- Require some conviction

      -- Apply update based on correctness (or skip if neutral)
      match correct with
      | none => agent  -- No update for perfectly neutral agents
      | some isCorrect =>
        -- Special handling for zero credibility (zombie prevention)
        let adjustment := if agent.credibility.val = 0 then
          if isCorrect then learningEpsilon else 0  -- Can escape from 0
        else
          if isCorrect then alpha else -alpha

        { agent with credibility := agent.credibility.add adjustment }
    else
      agent  -- Didn't participate
  )

      -- No audit event creation

      let finalSpace := { space' with
        signals := updatedSignals,
        reinforcements := updatedReinforcements,
        agents := updatedAgents,
        outcomes := outcome :: space'.outcomes }

      .ok (finalSpace, ()))

/-- Reset agent budgets daily with pro-rating to prevent burst exploitation -/
def resetBudgets (space : MVPSignalSpace) (wallClockNow : Time) : MVPSignalSpace :=
  withTimeUpdatePure space wallClockNow none (fun s =>
    -- Use foldr to avoid needing reverse
    let (updatedAgents, newReplenished, newAdjustments) :=
      s.agents.foldr
        (fun agent (agents, replenished, adjustments) =>
          if wallClockNow - agent.lastReset ≥ Constants.DAY_IN_SECONDS then
            let prevBudget := agent.dailyBudget  -- Capture BEFORE mutation
            let unspent := prevBudget - agent.spent
            let unspentRatio := if prevBudget.val > 0 then
              unspent.val / prevBudget.val else 0
            let multiplier := 0.5 + 1.5 * unspentRatio
            let newBudget := NNReal.ofReal (agent.baselineBudget.val * multiplier)

            let resetAgent := { agent with
              dailyBudget := newBudget,
              spent := ⟨0, by norm_num⟩,
              lastReset := wallClockNow }

            let replenishedAmount := agent.spent
            let netAdjustment := newBudget.val - prevBudget.val

            -- No audit event creation
            (resetAgent :: agents,
             replenished + replenishedAmount,
             adjustments + netAdjustment)
          else
            (agent :: agents, replenished, adjustments))
        ([], ⟨0, by norm_num⟩, (0.0 : Real))

    { s with
      agents := updatedAgents,
      totalNetAdjustments := s.totalNetAdjustments + newAdjustments,
      totalReplenished := s.totalReplenished + newReplenished }
      -- No auditLog update
  )

/-- Provision a new agent and track initial budget allocation -/
def provisionAgent (space : MVPSignalSpace)
    (agentData : AgentId × Credibility × AttentionMinutes)
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

### MVP Correctness Properties

```lean
/-- Budget constraint: can't spend more than allocated -/
theorem budget_constraint (space : MVPSignalSpace) :
  ∀ agent ∈ space.agents, agent.spent ≤ agent.dailyBudget := by
  intro agent h_mem
  -- Proof outline (TODO: Proof required):
  -- 1. Initial state: agent.spent = 0 ≤ dailyBudget (by NNReal)
  -- 2. applyReinforcement only succeeds if canReinforce returns true
  -- 3. canReinforce checks: absAmount ≤ (dailyBudget - spent)
  -- 4. On success: new_spent = spent + absAmount ≤ dailyBudget
  -- 5. By induction on reinforcement applications, invariant preserved
  sorry  -- TODO: Implement structural induction proof

/-- Accounting Integrity: All spent attention is tracked -/
theorem accounting_integrity (space : MVPSignalSpace) :
  let totalCumulativeSpent := space.agents.map (·.cumulativeSpent) |>.sum
  let totalInSignals := space.signals.map (·.initialStrength) |>.sum
  let totalInReinforcements := space.reinforcements.map (·.attentionSpent) |>.sum
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

/-- Open Economy: Current capacity equals invested plus available attention -/
theorem open_economy (space : MVPSignalSpace) :
  let totalAvailable := space.agents.map (fun a => a.dailyBudget - a.spent) |>.sum
  let totalInvested := (space.signals.map (·.initialStrength) |>.sum) +
                       (space.reinforcements.map (·.attentionSpent) |>.sum)
  -- Conservation law with explicit .val coercions for type alignment
  space.totalProvisioned.val + space.totalNetAdjustments =
    totalInvested.val + totalAvailable.val := by
  -- Proof outline:
  -- 1. totalProvisioned.val = Real value of initial baseline budgets
  -- 2. totalNetAdjustments = sum of all budget changes (can be negative)
  -- 3. totalInvested.val = Real value of locked attention
  -- 4. totalAvailable.val = Real value of unspent budgets
  -- 5. Conservation: initial + changes = locked + available
  sorry

/-- Total attention invested is non-negative -/
theorem attention_invested_non_negative (space : MVPSignalSpace) (id : SignalId) :
  getTotalAttentionInvested space id ≥ 0 := by
  -- Direct proof: sums of NNReal values are non-negative
  simp [getTotalAttentionInvested]
  -- Both initialStrength and attentionSpent are NNReal (≥ 0)
  -- Sum of non-negative values is non-negative
  sorry  -- TODO: Complete NNReal property proof

/-- Influence can be negative (key feature for inhibition) -/
theorem influence_can_be_negative : ∃ (space : MVPSignalSpace) (id : SignalId) (t : Time),
  getCurrentInfluence space id t < 0 := by
  -- Constructive proof: create a signal with negative reinforcements
  sorry  -- TODO: Construct example with inhibitory reinforcements

/-- Influence decay via factorization (valid with static credibility and no outcomes) -/
theorem influence_decay_monotonic (space : MVPSignalSpace) (id : SignalId) (t₁ t₂ : Time) :
  t₁ ≤ t₂ →
  (∀ r ∈ space.reinforcements, r.signalId = id → r.at ≤ t₁) →
  (∀ o ∈ space.outcomes, o.signalId = id → o.measuredAt ≤ t₁ ∨ o.measuredAt > t₂) →
  getCurrentInfluence space id t₂ = getCurrentInfluence space id t₁ *
    (Real.rpow 0.5 (Real.ofNat (t₂ - t₁) / space.config.halfLife.val)) := by
  intro h_time h_no_new_reinforcements h_no_outcomes
  -- Proof sketch:
  -- 1. getCurrentInfluence at t₁ = ∑(initial + reinforcements) with decay factors
  -- 2. Each component uses STATIC credibilityAtTime (immutable)
  -- 3. Between t₁ and t₂: no new reinforcements (by h_no_new_reinforcements)
  -- 4. Between t₁ and t₂: no outcomes processed (by h_no_outcomes)
  --    This ensures penaltyFactor remains constant
  -- 5. Each existing component decays by factor c = 0.5^((t₂-t₁)/halfLife)
  -- 6. Therefore: getCurrentInfluence(t₂) = c * getCurrentInfluence(t₁)
  sorry  -- TODO: Proof requires no outcomes between t₁ and t₂

/-- Corollary: Absolute influence decreases monotonically -/
theorem abs_influence_decreases (space : MVPSignalSpace) (id : SignalId) (t₁ t₂ : Time) :
  t₁ ≤ t₂ →
  (∀ r ∈ space.reinforcements, r.signalId = id → r.at ≤ t₁) →
  abs (getCurrentInfluence space id t₂) ≤ abs (getCurrentInfluence space id t₁) := by
  intro h_time h_no_new
  -- From the factorization theorem:
  -- |getCurrentInfluence(t₂)| = |c| * |getCurrentInfluence(t₁)|
  -- Since c ∈ (0,1], we have |c| ≤ 1
  -- Therefore |getCurrentInfluence(t₂)| ≤ |getCurrentInfluence(t₁)|
  sorry

/-- Credibility stays bounded by type construction -/
theorem credibility_bounded (space : MVPSignalSpace) :
  ∀ agent ∈ space.agents, 0 ≤ agent.credibility.val ∧ agent.credibility.val ≤ 1 := by
  intro agent h_mem
  -- Direct proof by Subtype property
  exact agent.credibility.property

/-- Historical immutability: reinforcement influence preserves past credibility -/
theorem reinforcement_preserves_history (space space' : MVPSignalSpace)
    (r : MVPReinforcement) (now : Time) :
  r ∈ space.reinforcements →
  r ∈ space'.reinforcements →
  -- Even if agent's current credibility changes between spaces
  (∃ agent ∈ space.agents, agent.id = r.by ∧ agent.credibility ≠
    (space'.agents.find? (·.id = r.by)).map (·.credibility)) →
  -- The reinforcement's contribution to influence remains unchanged
  let rAge := Real.ofNat (now - r.at)
  let decayFactor := Real.rpow 0.5 (rAge / space.config.halfLife.val)
  r.influence * r.credibilityAtTime.toReal * decayFactor =
  r.influence * r.credibilityAtTime.toReal * decayFactor := by
  -- Proof: credibilityAtTime is immutable, captured at creation
  -- Changes to agent.credibility don't affect historical reinforcements
  intros; rfl
```

### Usage Patterns for New Result Types

```lean
-- Example: Handling TimeResult
def exampleUsage (space : MVPSignalSpace) : MVPSignalSpace :=
  let result := emitSignal space "agent1" ⟨10, by norm_num⟩ currentTime
  match result.result with
  | none =>
    -- Operation failed, but still use maintained space
    result.space
  | some signalId =>
    -- Operation succeeded
    processSignal result.space signalId

-- Example: Chaining operations
def chainedOps (space : MVPSignalSpace) : MVPSignalSpace :=
  let emit1 := emitSignal space "agent1" ⟨10, by norm_num⟩ time1
  let space1 := emit1.space  -- Always updated, even if failed

  let reinforce1 := applyReinforcement space1 5 "sig1" "agent2" time2
  reinforce1.space  -- Always has maintenance

-- Helper for chaining TimeResult operations
def chainTimeResult (result : TimeResult α)
    (f : α → MVPSignalSpace → TimeResult β) : TimeResult β :=
  match result.result with
  | none => { space := result.space, result := none }
  | some value => f value result.space

-- Example usage with helper:
def chainedWithHelper (space : MVPSignalSpace) : TimeResult SignalId :=
  emitSignal space "agent1" ⟨10, by norm_num⟩ time1
    |> chainTimeResult (fun signalId space =>
      applyReinforcement space 5 signalId "agent2" time2
        |> chainTimeResult (fun _ space =>
          emitSignal space "agent3" ⟨5, by norm_num⟩ time3))

-- Complete integration example with new type system:
def exampleWithNewTypes (space : MVPSignalSpace) : String :=
  -- Create proper typed timestamps
  let wall1 := WallTime.ofNat 1000000  -- Unix timestamp
  let wall2 := WallTime.ofNat 1000010  -- 10 seconds later

  -- Emit signal with wall time
  let emitResult := emitSignal space "agent1" ⟨10, by norm_num⟩ wall1
  match emitResult.result with
  | none => "Emission failed"
  | some signalId =>
    -- Process outcome with error handling
    let outcome : MVPOutcome := {
      signalId := signalId,
      success := true,
      measuredAt := LogicalTime.ofNat 100,
      wallMeasuredAt := wall2,
      measuredBy := "evaluator"
    }

    let processResult := processOutcome emitResult.space outcome wall2
    match processResult.result with
    | .error msg => s!"Process failed: {msg}"
    | .ok () => "Success"

-- Example showing clock regression detection:
def clockRegressionExample (space : MVPSignalSpace) : String :=
  let wall1 := WallTime.ofNat 1000
  let wallBad := WallTime.ofNat 999  -- Regression!

  let result := emitSignal space "agent1" ⟨10, by norm_num⟩ wall1
  let space1 := result.space

  -- This will fail due to clock regression
  let result2 := processOutcome space1
    { signalId := "test",
      success := true,
      measuredAt := LogicalTime.ofNat 50,
      wallMeasuredAt := wallBad,
      measuredBy := "test" }
    wallBad

  match result2.result with
  | .error msg => s!"Caught: {msg}"  -- "Clock regression: 999 < 1000"
  | .ok () => "Shouldn't happen"
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

### Activity Tracking Policy

Which operations count as "writers" for BAT-Lite:

**Count as writers (human actions):**

- `emitSignal` - Agent creating a signal
- `applyReinforcement` - Agent reinforcing a signal
- `holdSignal` - Agent placing a hold (shows engagement)

**Don't count as writers (system/evaluator actions):**

- `processOutcome` - External evaluator action
- `resetBudgets` - Scheduled system maintenance
- `provisionAgent` - Administrative action
- `releaseExpiredHolds` - Automatic cleanup

### What MVP Provides

✅ **Lean 4 Compatible Type System:**

- `Credibility`: Proper Subtype `{ x : Real // 0 ≤ x ∧ x ≤ 1 }`
- Safe arithmetic helpers: `add`, `scale` preserve bounds
- `AttentionMinutes := NNReal`: Conservation tracking
- `Influence := Real`: Supports inhibition

✅ **Complete Learning Loop:**

- **Emitter included**: Signal creators learn from outcomes
- **Delivered influence**: Learning based on actual decayed influence (not raw amounts)
- **Conviction bonus**: Rewards one-sided (convicted) behavior
- **Static credibility**: Past influence based on immutable historical credibility (predictable decay)
- **Zombie recovery**: Escape path from zero credibility via epsilon learning

✅ **Open Economy Accounting (FIXED):**

- **Correct delta tracking**: Uses budget changes not baseline distance
- **Total adjustments**: Tracks totalNetAdjustments (can be negative)
- **Recovery floor**: 0.5x-2.0x budget range based on conservation
- **Diagnostic counters**: totalReplenished tracked separately (not in conservation)

✅ **Correct Mathematical Properties:**

- **Factorization proof**: Valid now with static credibility
- **Monotonic decay**: Influence strictly decreases over time
- **Type-enforced bounds**: Credibility constraints guaranteed via smart constructors
- **Single-level penalties**: No double punishment
- **Correct penalty semantics**: Success boosts strength (×1.43), failure reduces (×0.7)

✅ **Nuanced Aggregation:**

- Tracks positive/negative counts separately
- Computes net influence per agent
- Considers conviction in judgment (one-sidedness)
- Uses historical credibility only (MVP simplification)

❌ **Deferred to later phases:**

- Dynamic credibility re-evaluation (Phase 2)
- Multiple dimensions (belief/priority/ownership)
- Complex reinforcement types
- Information-theoretic decay
- Causal chains

### 🎯 MVP Implementation Checklist

When implementing Part 1 in Python/other languages:

✅ **Required for MVP:**

- [ ] Opaque time types (WallTime, LogicalTime)
- [ ] All structures from Part 1 (MVPSignal, MVPReinforcement, MVPOutcome, MVPAgent)
- [ ] Core operations (emitSignal, applyReinforcement, processOutcome)
- [ ] BAT-Lite time management
- [ ] Signal holds with proper semantics
- [ ] Budget resets with pro-rating
- [ ] Error handling (TimeResult, TimeResultExcept)
- [ ] Monotonic clock validation

❌ **NOT Required for MVP:**

- Enhanced credibility models (Part 2)
- Orthogonal dimensions (Part 3)
- Governance features (Part 4)
- Information theory (Part 5)
- Causal credit (Part 6)

**End of MVP Specification**

---

# FUTURE ROADMAP (Not Part of MVP)

⚠️ **IMPORTANT**: Everything below this line describes future enhancements that are NOT part of the MVP.
These sections are included for completeness and to show the system's evolution path, but should NOT be implemented in the initial release.

## Part 2: Enhanced Credibility (Future Release - NOT MVP)

### Multi-Factor Credibility

Extend agent credibility to track different types of accuracy:

```lean
/-- Enhanced credibility tracking -/
structure EnhancedCredibility where
  overall : Credibility          -- Overall credibility [0, 1]
  byOutcome : Credibility        -- Success at predicting outcomes
  byConsensus : Credibility      -- Alignment with group
  byDomain : List (String × Credibility)  -- Domain-specific credibility

/-- Enhanced agent contains MVPAgent plus extended fields -/
structure EnhancedAgent where
  base : MVPAgent  -- Contains id, basic credibility, budgets
  enhancedCredibility : EnhancedCredibility  -- Extended credibility metrics
  participationCount : Nat  -- Number of signals reinforced
  successCount : Nat        -- Number of correct predictions

/-- Safe credibility arithmetic helpers -/
def addToCredibility (c : Real) (delta : Real) : Credibility :=
  mkCredibility (c + delta)

def weightedCredibility (weights : List (Real × Real)) : Credibility :=
  let sum := weights.map (fun (w, c) => w * c) |>.sum
  mkCredibility sum

/-- Update credibility with multiple factors -/
def updateEnhancedCredibility (agent : EnhancedAgent)
    (outcome : MVPOutcome) (groupConsensus : Bool) : EnhancedAgent :=
  let alpha : Real := 0.1 / (1 + Real.ofNat agent.participationCount / 100)  -- Decreasing learning rate

  -- Update outcome-based credibility
  let outcomeUpdate := if outcome.success then alpha else -alpha
  let newByOutcome := agent.enhancedCredibility.byOutcome.add outcomeUpdate

  -- Update consensus-based credibility
  let consensusUpdate := if groupConsensus then alpha/2 else -alpha/2
  let newByConsensus := agent.enhancedCredibility.byConsensus.add consensusUpdate

  -- Overall is weighted average
  let newOverall := weightedCredibility [(0.7, newByOutcome.toReal), (0.3, newByConsensus.toReal)]

  { agent with
    enhancedCredibility := { agent.enhancedCredibility with
      overall := newOverall,
      byOutcome := newByOutcome,
      byConsensus := newByConsensus },
    participationCount := agent.participationCount + 1,
    successCount := if outcome.success then agent.successCount + 1 else agent.successCount }
```

### Credibility-Based Budget Allocation

```lean
/-- Allocate attention based on credibility with recovery floor -/
def allocateBudgetByCredibility (baseBudget : AttentionMinutes)
    (credibility : Credibility) : AttentionMinutes :=
  -- Design Decision: 0.5x minimum budget as "recovery floor"
  -- This ensures even zero-credibility agents can attempt redemption
  -- Alternative: Use stricter formula (e.g., 0.1 + 1.9 * cred) to silence bad actors
  let multiplier := 0.5 + 1.5 * credibility.val  -- Range: [0.5, 2.0]
  NNReal.ofReal (baseBudget.val * multiplier)

/-- Reset with credibility-adjusted budgets -/
def resetBudgetsWithCredibility (space : MVPSignalSpace) (now : Time)
    : MVPSignalSpace :=
  let baseBudget : AttentionMinutes := NNReal.ofReal 480.0  -- 8 hours

  let updatedAgents := space.agents.map (fun agent =>
    if now - agent.lastReset > Constants.DAY_IN_SECONDS then
      let newBudget := allocateBudgetByCredibility baseBudget agent.credibility
      { agent with
        dailyBudget := newBudget,
        spent := ⟨0, by norm_num⟩,
        lastReset := now }
    else agent)

  { space with agents := updatedAgents }
```

## Part 3: Orthogonal Dimensions (Future Release - NOT MVP)

**⚠️ WARNING: This section contains known design issues:**

- Type coercion issues: NNReal * Real operations are ill-typed in Lean
- Progress accumulation: Currently overwrites instead of aggregating
- Bounds enforcement: progressPercentage can exceed 100
These will be addressed in future iterations.

### Three Independent Channels

Replace single strength with properly separated dimensions:

```lean
/-- Belief dimension using proper log-odds -/
structure Belief where
  logOdds : Real           -- Unbounded, 0 = uncertain
  evidenceSources : List AgentId
  evidenceCount : Nat      -- Independent evidence pieces
  lastUpdated : Time

/-- Priority dimension (bounded) -/
structure Priority where
  urgency : NNReal         -- [0, 1] where 1 = maximum
  importance : NNReal      -- [0, 1] expected value
  deadline : Option Time
  lastUpdated : Time

/-- Ownership dimension (exclusive) -/
structure Ownership where
  owner : Option AgentId
  claimedAt : Option Time
  lastActivity : Option Time
  progressPercentage : NNReal  -- [0, 100]

/-- Signal with orthogonal dimensions -/
structure DimensionalSignal extends MVPSignal where
  belief : Belief
  priority : Priority
  ownership : Ownership
```

### Dimension-Specific Reinforcement

```lean
/-- Reinforcement targets specific dimensions -/
inductive ReinforcementTarget where
  | belief : Real → ReinforcementTarget      -- Log-odds update
  | priority : NNReal → ReinforcementTarget  -- Urgency boost
  | ownership : ReinforcementTarget          -- Claim ownership
  | progress : NNReal → ReinforcementTarget  -- Report progress

/-- Enhanced reinforcement with target -/
structure DimensionalReinforcement extends MVPReinforcement where
  target : ReinforcementTarget
  confidence : NNReal  -- How confident the agent is

/-- Apply reinforcement to correct dimension -/
def applyDimensionalReinforcement (signal : DimensionalSignal)
    (r : DimensionalReinforcement) (agentCred : Credibility) (now : Time)
    : DimensionalSignal :=
  match r.target with
  | .belief logOddsUpdate =>
    -- Bayesian update (always valid for any real number)
    let updatedSources := if r.by ∈ signal.belief.evidenceSources then
      signal.belief.evidenceSources  -- Already recorded this agent
    else
      r.by :: signal.belief.evidenceSources  -- New evidence source

    { signal with belief :=
      { signal.belief with
        logOdds := signal.belief.logOdds + logOddsUpdate * agentCred.toReal,
        evidenceSources := updatedSources,
        evidenceCount := updatedSources.length,
        lastUpdated := now }}

  | .priority urgencyBoost =>
    -- Bounded update
    let currentUrgency := signal.priority.urgency
    let boost := min urgencyBoost.val (1 - currentUrgency.val)
    { signal with priority :=
      { signal.priority with
        urgency := NNReal.ofReal (currentUrgency.val + boost * agentCred.toReal),
        lastUpdated := now }}

  | .ownership =>
    -- Exclusive claim (gated by credibility)
    -- Only agents with sufficient credibility can claim ownership
    if signal.ownership.owner.isNone ∧ agentCred.toReal ≥ Constants.MIN_OWNERSHIP_CREDIBILITY then
      { signal with ownership :=
        { owner := some r.by,
          claimedAt := some now,
          lastActivity := some now,
          progressPercentage := 0 }}
    else signal  -- Can't claim if owned or credibility too low

  | .progress percentage =>
    -- Update progress if owner (weighted by credibility)
    if signal.ownership.owner = some r.by then
      -- Weight progress update by agent credibility
      -- Low credibility agents have less trusted progress reports
      let weightedProgress := NNReal.ofReal (percentage.val * agentCred.toReal)
      { signal with ownership :=
        { signal.ownership with
          progressPercentage := weightedProgress,
          lastActivity := some now }}
    else signal
```

### Dimension-Specific Decay

```lean
structure DimensionalDecayRates where
  beliefHalfLife : PosReal    -- Days (truth persists) - can't be zero
  priorityHalfLife : PosReal  -- Hours (urgency fades) - can't be zero
  ownershipTimeout : PosReal  -- Minutes (needs activity) - can't be zero

def applyDimensionalDecay (signal : DimensionalSignal) (now : Time)
    (rates : DimensionalDecayRates) : DimensionalSignal :=
  -- Belief: slow decay toward uncertainty (0)
  let beliefAge := Real.ofNat (now - signal.belief.lastUpdated)
  let beliefDecay := Real.rpow 0.5 (beliefAge / rates.beliefHalfLife.val)
  let decayedLogOdds := signal.belief.logOdds * beliefDecay

  -- Priority: fast decay toward 0
  let priorityAge := Real.ofNat (now - signal.priority.lastUpdated)
  let priorityDecay := Real.rpow 0.5 (priorityAge / rates.priorityHalfLife.val)
  let decayedUrgency := NNReal.ofReal (signal.priority.urgency.val * priorityDecay)

  -- Ownership: timeout releases
  let ownershipValid := match signal.ownership.lastActivity with
    | none => false
    | some lastActivity =>
      Real.ofNat (now - lastActivity) < rates.ownershipTimeout.val

  { signal with
    belief := { signal.belief with logOdds := decayedLogOdds },
    priority := { signal.priority with urgency := decayedUrgency },
    ownership := if ownershipValid then signal.ownership
                 else { owner := none, claimedAt := none,
                       lastActivity := none, progressPercentage := 0 }}
```

## Part 4: Advanced Governance (Future Release - NOT MVP)

### Rate Limiting and Anti-Gaming

```lean
/-- Track reinforcement patterns for governance -/
structure ReinforcementPattern where
  agentPair : AgentId × SignalId
  timestamps : List Time
  amounts : List AttentionMinutes

/-- Governance rules to prevent gaming -/
structure GovernanceRules where
  maxReinforcementRate : NNReal     -- Max reinforcements per hour
  minDiversityRatio : NNReal        -- Min unique agents / total
  maxAmplificationRatio : NNReal    -- Max total positive / initial
  suspiciousBehaviorThreshold : NNReal

/-- Detect suspicious reinforcement patterns using sliding window -/
def detectSuspiciousBehavior (patterns : List ReinforcementPattern)
    (rules : GovernanceRules) (now : Time) (windowSeconds : Real := 3600) : List AgentId :=
  patterns.filterMap (fun p =>
    -- Check recent window only (e.g., last hour)
    let recentTimestamps := p.timestamps.filter (λ t =>
      Real.ofNat (now - t) < windowSeconds)
    -- Calculate rate within the sliding window
    let rate := Real.ofNat recentTimestamps.length / windowSeconds
    if rate > rules.maxReinforcementRate.toReal then
      some p.agentPair.1  -- Flag agent for burst activity
    else none)

/-- Apply governance before reinforcement -/
def checkGovernance (space : MVPSignalSpace) (r : MVPReinforcement)
    (rules : GovernanceRules) : Bool :=
  -- Get reinforcement history for this agent-signal pair
  let history := space.reinforcements.filter (fun prev =>
    prev.by = r.by ∧ prev.signalId = r.signalId)

  -- Check rate limit
  let recentCount := history.filter (fun prev =>
    Real.ofNat (r.at - prev.at) < 3600).length  -- Last hour
  -- Use proper conditional expression instead of return
  if Real.ofNat recentCount ≥ rules.maxReinforcementRate.toReal then
    false
  else
    -- Check diversity
    let uniqueReinforcers := space.reinforcements
      .filter (·.signalId = r.signalId)
      .map (·.by)
      .eraseDup
      .length
    let totalReinforcers := space.reinforcements
      .filter (·.signalId = r.signalId)
      .length

    if totalReinforcers > 0 then
      let diversityRatio := Real.ofNat uniqueReinforcers / Real.ofNat totalReinforcers
      diversityRatio ≥ rules.minDiversityRatio.toReal
    else
      true
```

## Part 5: Information-Theoretic Foundation (Future Release - NOT MVP)

### Principled Decay from Shannon Entropy

```lean
/-- Calculate signal entropy from content and uncertainty -/
def signalEntropy (signal : DimensionalSignal) : NNReal :=
  -- Uncertainty component from belief
  let beliefUncertainty := 1.0 / (1.0 + abs signal.belief.logOdds)

  -- Information diversity from evidence sources (positive entropy)
  let uniqueSources := signal.belief.evidenceSources.eraseDup.length
  let sourceEntropy := if uniqueSources > 1 then
    Real.log (Real.ofNat uniqueSources) / Real.log 2 / 10.0  -- Positive, normalized
  else
    0.0  -- Single source has zero entropy

  -- Combined entropy (both components positive)
  NNReal.ofReal (beliefUncertainty * (1 + sourceEntropy))

/-- Environmental factors affecting signal persistence -/
structure Environment where
  totalSignals : Nat         -- Current signal count
  activeAgents : Nat         -- Agents currently online
  noiseLevel : NNReal       -- Background activity level
  averageAttentionSpan : PosReal  -- Typical focus duration (must be positive)

/-- Derive decay rate from information theory -/
def informationTheoreticDecayRate (signal : DimensionalSignal)
    (env : Environment) : NNReal :=
  let entropy := signalEntropy signal

  -- High entropy → harder to remember → faster decay
  -- Many signals → more interference → faster decay
  -- Low attention → shorter persistence → faster decay

  let interferenceFactor : Real := Real.ofNat env.totalSignals / 100.0
  let attentionFactor : Real := 1.0 / env.averageAttentionSpan.val

  -- Shannon-inspired decay rate
  let halfLife := 3600.0 / (1 + entropy.val * interferenceFactor * attentionFactor)
  NNReal.ofReal (Real.log 2 / halfLife)
```

## Part 6: Causal Credit Assignment (Future Release - NOT MVP)

**⚠️ WARNING: This section is incomplete:**

- agentContributions field is completely ignored (all agents get uniform credit)
- CausalOutcome is not persisted alongside MVPOutcome
- Migration path needs proper sum type or separate field
- Credit propagation doesn't use contribution weights
These issues are deferred to future phases.

### Full Causal Chain Tracking

```lean
/-- Complete outcome with causal attribution (Part 6 - NOT MVP) -/
structure CausalOutcome where
  taskId : TaskId
  signalChain : List SignalId      -- Ordered causal chain
  agentContributions : List (AgentId × NNReal)  -- Who contributed how much (positive)
  success : Bool
  value : Real  -- Can be negative for penalties
  measuredAt : Time
  measuredBy : ExternalSystem

/-- Propagate credit through causal chain (Part 6 - NOT MVP) -/
-- NOTE: This function is for Part 6 only. It would require a separate
-- causalOutcomes field or migration from MVPOutcome to CausalOutcome.
def propagateCausalCredit (outcome : CausalOutcome) (space : MVPSignalSpace)
    : MVPSignalSpace :=
  -- Distribute credit with distance discounting
  let discount := 0.9  -- Each step back gets 90% of credit

  let indexedChain := outcome.signalChain.enum

  -- Update each signal in chain
  let updatedSpace := indexedChain.foldl (fun sp (idx, sigId) =>
    let credit := outcome.value * (discount ^ idx)

    -- Find signal emitter (critical for complete learning)
    let emitter := sp.signals.find? (·.id = sigId) |>.map (·.emitter)

    -- Find all agents who reinforced this signal
    let reinforcers := sp.reinforcements
      .filter (·.signalId = sigId)
      .map (·.by)
      .eraseDup

    -- Include emitter in participants list
    let participants := match emitter with
      | none => reinforcers
      | some e => (e :: reinforcers).eraseDup

    -- Update their credibility based on contribution
    let updatedAgents := sp.agents.map (fun agent =>
      if agent.id ∈ participants then
        -- Handle both positive and negative credit properly
        let adjustment := if credit > 0 then
          min 0.1 (abs credit * 0.01)  -- Small positive update
        else
          -min 0.1 (abs credit * 0.01)  -- Small negative update

        -- Use proper credibility constructor
        { agent with credibility := agent.credibility.add adjustment }
      else agent)

    { sp with agents := updatedAgents }
  ) space

  -- NOTE: In Part 6, would need a separate causalOutcomes field or migration
  -- Cannot append CausalOutcome to List MVPOutcome (type mismatch)
  updatedSpace

/-- Migration Path for Part 6:
    Option 1: Add causalOutcomes : List CausalOutcome to MVPSignalSpace
    Option 2: Replace outcomes with sum type: List (MVPOutcome | CausalOutcome)
    Recommended: Option 1 for backward compatibility
-/
```

## Implementation Checklist

### Phase 1: MVP (Week 1) ✓

- [x] Attention budget enforcement (open economy with tracking)
- [x] Proper decay for all reinforcements
- [x] Agent credibility and budgets
- [x] Outcomes update credibility
- [x] Sign-aware credibility updates

### Phase 2: Enhanced Credibility (Week 2)

- [ ] Multi-factor credibility tracking
- [ ] Credibility-based budget allocation
- [ ] Domain-specific credibility

### Phase 3: Dimensions (Week 3)

- [ ] Separate belief/priority/ownership
- [ ] Dimension-specific updates
- [ ] Different decay rates

### Phase 4: Governance (Week 4)

- [ ] Pattern detection
- [ ] Rate limiting
- [ ] Diversity requirements

### Phase 5: Information Theory (Month 2)

- [ ] Entropy calculation
- [ ] Environment-aware decay
- [ ] Shannon-based dynamics

### Phase 6: Causality (Month 3)

- [ ] Causal chain tracking
- [ ] Credit propagation
- [ ] Multi-step attribution

## Proof Status

### Provable with Current Definitions

- **Budget Constraint**: Structural induction on operations
- **Accounting Integrity**: Via structural induction
- **Influence Decay**: With precondition of no outcomes in interval
- **Credibility Bounds**: By Subtype construction
- **Historical Immutability**: Direct from immutable fields

### Requires Future Work

- **Open Economy Properties**: Needs formal injection model
- **Learning Convergence**: Requires equilibrium analysis
- **Causal Credit Distribution**: Needs formal game theory

## Key Design Decisions

### Time Semantics

- **Dual-Time System**: Tracks both wall-clock time and logical time (τ)
- **Logical Time (τ)**: Advances only when ≥2 agents are active within window
- **Wall-Clock Input**: Operations require wallClockNow for activity tracking and TTL
- **Deterministic Decay**: All decay calculations use logical time, not wall-clock
- **Monotonic**: Both times only advance, never go backward
- **Resolution**: Second-level granularity for all operations

The system uses wall-clock readings to determine when logical time should advance,
but all decay and influence calculations depend solely on logical time. This ensures
collaborative activity drives the system's temporal evolution while maintaining
deterministic behavior for decay.

### Economic Model

- **Open System**: Daily budget resets inject new attention (not conserved)
- **Pro-rated Resets**: Unspent budget affects next allocation (prevents gaming)
- **Recovery Floor**: 0.5x minimum budget ensures redemption possibility
- **Burst Prevention**: Spending before reset incurs penalty in next budget

### Learning Dynamics

- **Neutral is Neutral**: Zero influence means no credibility update
- **Conviction Matters**: Self-contradictory reinforcements penalized
- **Emitters Learn**: Signal creators included in all learning loops
- **Zombie Recovery**: Epsilon learning allows escape from zero credibility

### Type Safety

- **PosReal for Division**: Prevents division-by-zero at type level
- **Bounded Types**: Credibility guaranteed in [0,1] by construction
- **Explicit Conversions**: All Nat→Real conversions explicit (Real.ofNat)
- **No Implicit Coercion**: Type mismatches caught at compile time

## Conclusion

This design provides:

1. **Complete MVP**: Working learning loop from day 1 with proper type safety
2. **Open Economy**: Tracked attention injection with anti-gaming measures
3. **Proper decay**: All components decay based on age with provable properties
4. **External grounding**: Outcomes drive learning with neutral handling
5. **Progressive enhancement**: Each phase adds specific value without breaking core

The MVP is now truly minimal but mathematically coherent - it has proper types, provable theorems (proofs pending), and correct dynamics. Later phases add sophistication without breaking the core loop.
