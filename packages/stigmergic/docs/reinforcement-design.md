# Reinforcement in Stigmergic Systems: From MVP to First Principles

## Executive Summary

This document presents a progressive design for reinforcement in stigmergic systems, starting with the simplest possible MVP and building toward a complete, first-principles grounded system. Each enhancement layer adds specific capabilities while maintaining backward compatibility.

## Part 1: MVP Design (Week 1)

### Core Concept

The MVP implements the absolute minimum: signals have strength that can be reinforced or inhibited, with external validation to prevent self-referential loops.

### MVP Data Model

```lean
/-- Minimal signal with single strength value -/
structure MVPSignal where
  id : SignalId
  emitter : AgentId
  timestamp : Time
  initialStrength : NNReal  -- Set once when emitted

/-- Simple reinforcement event -/
structure MVPReinforcement where
  signalId : SignalId
  by : AgentId
  amount : Real  -- Positive for support, negative for objection
  at : Time

/-- External validation to ground the system -/
structure MVPOutcome where
  signalId : SignalId
  success : Bool
  measuredAt : Time
```

### MVP Operations

```lean
/-- Signal space with minimal functionality -/
structure MVPSignalSpace where
  signals : List MVPSignal
  reinforcements : List MVPReinforcement
  outcomes : List MVPOutcome

/-- Calculate current strength with decay and reinforcements -/
def getCurrentStrength (space : MVPSignalSpace) (signalId : SignalId) (now : Time) : NNReal :=
  match space.signals.find? (·.id = signalId) with
  | none => 0
  | some signal =>
    -- Simple exponential decay
    let age := (now - signal.timestamp).toSeconds
    let decayedInitial := signal.initialStrength * (0.5 ^ (age / 3600))  -- 1hr half-life

    -- Sum all reinforcements
    let totalReinforcement := space.reinforcements
      .filter (·.signalId = signalId)
      .map (·.amount)
      .sum

    -- Ensure non-negative
    max 0 (decayedInitial + totalReinforcement)

/-- Record external outcome for validation -/
def recordOutcome (space : MVPSignalSpace) (outcome : MVPOutcome) : MVPSignalSpace :=
  { space with outcomes := outcome :: space.outcomes }
```

### MVP Invariants

```lean
theorem mvp_strength_non_negative (space : MVPSignalSpace) (id : SignalId) (t : Time) :
  getCurrentStrength space id t ≥ 0 := by sorry

theorem mvp_decay_monotonic (space : MVPSignalSpace) (id : SignalId) (t₁ t₂ : Time) :
  t₁ ≤ t₂ → (no_reinforcements_between t₁ t₂) →
  getCurrentStrength space id t₂ ≤ getCurrentStrength space id t₁ := by sorry
```

### What MVP Provides

✅ **Includes:**
- Basic signal strength management
- Simple reinforcement mechanism
- External outcome recording
- Time-based decay

❌ **Excludes:**
- Multiple dimensions (belief/priority/ownership)
- Agent learning
- Resource constraints
- Complex reinforcement types

## Part 2: Agent Credibility (Week 2)

### Enhancement: Learning from Outcomes

Add agent credibility that updates based on prediction accuracy:

```lean
/-- Agent state with credibility -/
structure AgentState where
  id : AgentId
  credibility : NNReal  -- [0, 1], starts at 0.5
  reinforcementHistory : List (SignalId × Bool)  -- (signal, was_correct)

/-- Update credibility based on outcome -/
def updateCredibility (agent : AgentState) (outcome : MVPOutcome) : AgentState :=
  let wasCorrect := agent.reinforcementHistory.any (·.1 = outcome.signalId)
  let alpha := 0.1  -- Learning rate

  let newCredibility :=
    if wasCorrect ∧ outcome.success then
      min 1.0 (agent.credibility + alpha)
    else if wasCorrect ∧ ¬outcome.success then
      max 0.0 (agent.credibility - alpha)
    else
      agent.credibility  -- No change if didn't participate

  { agent with
    credibility := newCredibility,
    reinforcementHistory := (outcome.signalId, outcome.success) :: agent.reinforcementHistory }

/-- Weight reinforcements by agent credibility -/
def getWeightedStrength (space : MVPSignalSpace) (agents : List AgentState)
    (signalId : SignalId) (now : Time) : NNReal :=
  match space.signals.find? (·.id = signalId) with
  | none => 0
  | some signal =>
    let age := (now - signal.timestamp).toSeconds
    let decayedInitial := signal.initialStrength * (0.5 ^ (age / 3600))

    -- Weight each reinforcement by agent credibility
    let weightedReinforcement := space.reinforcements
      .filter (·.signalId = signalId)
      .map (fun r =>
        let agentCred := (agents.find? (·.id = r.by)).map (·.credibility) |>.getD 0.5
        r.amount * agentCred)
      .sum

    max 0 (decayedInitial + weightedReinforcement)
```

## Part 3: Orthogonal Dimensions (Week 3)

### Enhancement: Separate Belief, Priority, and Ownership

Replace single strength with three independent dimensions:

```lean
/-- Epistemic dimension: What we believe -/
structure Belief where
  logOdds : Real  -- Unbounded, 0 = uncertain
  evidenceSources : List AgentId
  lastUpdated : Time

/-- Priority dimension: How urgent -/
structure Priority where
  urgency : NNReal  -- [0, 1]
  deadline : Option Time
  value : NNReal  -- Expected value if addressed

/-- Coordination dimension: Who owns it -/
structure Ownership where
  owner : Option AgentId
  claimedAt : Option Time
  lastActivity : Option Time

/-- Enhanced signal with orthogonal dimensions -/
structure EnhancedSignal extends MVPSignal where
  belief : Belief
  priority : Priority
  ownership : Ownership
```

### Dimension-Specific Reinforcement

```lean
/-- Reinforcement reasons affect different dimensions -/
inductive ReinforcementReason where
  | evidence : ReinforcementReason      -- Updates belief
  | urgency : ReinforcementReason       -- Updates priority
  | claiming : ReinforcementReason      -- Updates ownership
  | objection : ReinforcementReason     -- Negative on belief/priority

/-- Enhanced reinforcement with typed reason -/
structure EnhancedReinforcement extends MVPReinforcement where
  reason : ReinforcementReason
  confidence : NNReal

/-- Apply reinforcement to appropriate dimension -/
def applyReinforcementByDimension (signal : EnhancedSignal)
    (r : EnhancedReinforcement) (agentCred : NNReal) : EnhancedSignal :=
  match r.reason with
  | .evidence =>
    -- Update belief using log-odds
    let update := r.amount * r.confidence * agentCred
    { signal with
      belief.logOdds := signal.belief.logOdds + Real.log (1 + update) }

  | .urgency =>
    -- Update priority (bounded)
    let boost := min r.amount (1 - signal.priority.urgency)
    { signal with
      priority.urgency := signal.priority.urgency + boost * agentCred }

  | .claiming =>
    -- Update ownership (exclusive)
    if signal.ownership.owner.isNone then
      { signal with
        ownership := { owner := some r.by, claimedAt := some r.at,
                      lastActivity := some r.at }}
    else signal

  | .objection =>
    -- Reduce both belief and priority
    { signal with
      belief.logOdds := signal.belief.logOdds - r.amount * agentCred,
      priority.urgency := max 0 (signal.priority.urgency - r.amount * agentCred) }
```

### Dimension-Specific Decay

```lean
/-- Different decay rates for different dimensions -/
structure DecayRates where
  beliefHalfLife : NNReal   -- Truth decays slowly (days)
  priorityHalfLife : NNReal -- Urgency decays fast (hours)
  ownershipTimeout : NNReal -- Ownership expires if inactive

def applyDimensionalDecay (signal : EnhancedSignal) (now : Time)
    (rates : DecayRates) : EnhancedSignal :=
  let age := (now - signal.timestamp).toSeconds

  -- Belief decays slowly
  let beliefDecay := 0.5 ^ (age / rates.beliefHalfLife)
  let newLogOdds := signal.belief.logOdds * beliefDecay

  -- Priority decays fast
  let priorityDecay := 0.5 ^ (age / rates.priorityHalfLife)
  let newUrgency := signal.priority.urgency * priorityDecay

  -- Ownership times out
  let ownershipValid := match signal.ownership.lastActivity with
    | none => true
    | some last => (now - last).toSeconds < rates.ownershipTimeout

  { signal with
    belief.logOdds := newLogOdds,
    priority.urgency := newUrgency,
    ownership := if ownershipValid then signal.ownership
                 else { owner := none, claimedAt := none, lastActivity := none }}
```

## Part 4: Resource Constraints (Week 4)

### Enhancement: Attention as Conserved Quantity

Add resource constraints to prevent unbounded growth:

```lean
/-- Attention is the scarce resource -/
structure AttentionBudget where
  total : NNReal        -- Total attention-minutes per period
  allocated : NNReal    -- Already spent
  remaining : NNReal    -- Available
  inv : remaining = total - allocated

/-- Agent with attention budget -/
structure ResourcedAgent extends AgentState where
  attentionBudget : AttentionBudget
  lastResetTime : Time

/-- Spend attention to reinforce -/
def spendAttention (agent : ResourcedAgent) (amount : NNReal) : Option ResourcedAgent :=
  if amount ≤ agent.attentionBudget.remaining then
    some { agent with
      attentionBudget.allocated := agent.attentionBudget.allocated + amount,
      attentionBudget.remaining := agent.attentionBudget.remaining - amount }
  else
    none  -- Insufficient attention

/-- Reset budgets periodically -/
def resetBudgetIfNeeded (agent : ResourcedAgent) (now : Time)
    (resetPeriod : NNReal) : ResourcedAgent :=
  if (now - agent.lastResetTime).toSeconds > resetPeriod then
    { agent with
      attentionBudget := { total := agent.attentionBudget.total,
                          allocated := 0, remaining := agent.attentionBudget.total },
      lastResetTime := now }
  else agent
```

### Rate Limiting and Governance

```lean
/-- Governance constraints -/
structure GovernanceRules where
  maxReinforcementPerSignal : NNReal    -- Cap total reinforcement
  cooldownPeriod : NNReal               -- Minimum time between reinforcements
  diversityRequirement : Nat            -- Minimum unique reinforcers

/-- Check if reinforcement is allowed -/
def checkGovernance (space : MVPSignalSpace) (r : MVPReinforcement)
    (rules : GovernanceRules) : Bool :=
  -- Check cooldown
  let lastReinforcement := space.reinforcements
    .filter (fun prev => prev.signalId = r.signalId ∧ prev.by = r.by)
    .map (·.at)
    .maximum?

  let cooldownOk := match lastReinforcement with
    | none => true
    | some last => (r.at - last).toSeconds > rules.cooldownPeriod

  -- Check total cap
  let totalReinforcement := space.reinforcements
    .filter (·.signalId = r.signalId)
    .map (·.amount.natAbs)
    .sum

  let capOk := totalReinforcement + r.amount.natAbs ≤ rules.maxReinforcementPerSignal

  cooldownOk ∧ capOk
```

## Part 5: Information-Theoretic Foundation

### Enhancement: Principled Decay from First Principles

Replace arbitrary decay with information-theoretic model:

```lean
/-- Signal entropy determines memorability -/
def signalEntropy (signal : EnhancedSignal) : NNReal :=
  -- High entropy = harder to remember = faster decay
  let textComplexity := signal.belief.evidenceSources.length.toNNReal
  let uncertaintyFactor := 1.0 - abs (signal.belief.logOdds / (1 + abs signal.belief.logOdds))
  textComplexity * uncertaintyFactor

/-- Environment noise affects signal persistence -/
structure EnvironmentFactors where
  noiseLevel : NNReal      -- Background interference
  competingSignals : Nat   -- Number of other signals
  agentLoad : NNReal       -- Average agent utilization

/-- Derive decay rate from information theory -/
def informationTheoreticDecay (signal : EnhancedSignal)
    (env : EnvironmentFactors) (agentAttentionSpan : NNReal) : NNReal :=
  -- Shannon entropy meets stigmergic dynamics
  let entropy := signalEntropy signal
  let interference := env.noiseLevel * env.competingSignals.toNNReal
  let halfLife := agentAttentionSpan / (1 + entropy * interference)
  NNReal.log 2 / halfLife
```

## Part 6: Complete First-Principles System

### Full Credit Assignment

```lean
/-- Complete outcome with causal chain -/
structure CompleteOutcome where
  taskId : TaskId
  signalChain : List SignalId    -- Full causal path
  success : Bool
  value : Real                    -- Magnitude of outcome
  measuredAt : Time
  measuredBy : ExternalSystem     -- External validation source

/-- Propagate credit through causal chain -/
def propagateCredit (outcome : CompleteOutcome) (space : SignalSpace)
    (agents : List ResourcedAgent) : (SignalSpace × List ResourcedAgent) :=
  -- Update beliefs based on outcome
  let updatedSignals := outcome.signalChain.foldl (fun signals sigId =>
    updateSignalBelief signals sigId outcome) space.signals

  -- Update agent credibility
  let updatedAgents := agents.map (fun agent =>
    let participated := agent.reinforcementHistory.any (·.1 ∈ outcome.signalChain)
    if participated then
      updateAgentCredibility agent outcome
    else agent)

  ({ space with signals := updatedSignals }, updatedAgents)

/-- Bayesian belief update -/
def updateSignalBelief (signals : List EnhancedSignal) (sigId : SignalId)
    (outcome : CompleteOutcome) : List EnhancedSignal :=
  signals.map (fun s =>
    if s.id = sigId then
      let likelihoodRatio := if outcome.success then 2.0 else 0.5
      { s with belief.logOdds := s.belief.logOdds + Real.log likelihoodRatio }
    else s)
```

### System Invariants

```lean
/-- Complete system invariants -/
structure SystemInvariants where
  -- Conservation of attention
  attentionConserved : ∀ (agents : List ResourcedAgent),
    (agents.map (·.attentionBudget.allocated)).sum ≤
    (agents.map (·.attentionBudget.total)).sum

  -- Belief coherence
  beliefMonotonic : ∀ (s : EnhancedSignal) (t₁ t₂ : Time),
    t₁ < t₂ → (noReinforcementsBetween t₁ t₂) →
    abs (getBeliefAt s t₂) ≤ abs (getBeliefAt s t₁)

  -- Priority bounds
  priorityBounded : ∀ (s : EnhancedSignal),
    0 ≤ s.priority.urgency ∧ s.priority.urgency ≤ 1

  -- Ownership exclusivity
  ownershipExclusive : ∀ (signals : List EnhancedSignal),
    ∀ (s₁ s₂ : EnhancedSignal), s₁ ∈ signals → s₂ ∈ signals →
    s₁.id ≠ s₂.id → s₁.ownership.owner ≠ s₂.ownership.owner

  -- External grounding requirement
  outcomesExternal : ∀ (o : CompleteOutcome),
    o.measuredBy ≠ InternalSystem
```

## Implementation Roadmap

### Phase 1: MVP (Week 1)
- ✅ Single strength scalar
- ✅ Basic reinforcement (+/-)
- ✅ Simple exponential decay
- ✅ External outcome recording

### Phase 2: Learning (Week 2)
- ⬜ Agent credibility tracking
- ⬜ Update credibility from outcomes
- ⬜ Weight reinforcements by credibility

### Phase 3: Dimensions (Week 3)
- ⬜ Split into belief/priority/ownership
- ⬜ Dimension-specific update rules
- ⬜ Different decay rates per dimension

### Phase 4: Resources (Week 4)
- ⬜ Attention budgets
- ⬜ Rate limiting
- ⬜ Governance rules

### Phase 5: Information Theory (Month 2)
- ⬜ Entropy-based decay
- ⬜ Environmental factors
- ⬜ Principled dynamics

### Phase 6: Complete System (Month 3)
- ⬜ Full causal credit assignment
- ⬜ Comprehensive invariants
- ⬜ Production-ready implementation

## Conclusion

This progressive design allows you to:

1. **Start simple**: MVP can be built in one week
2. **Validate early**: Test core concepts with minimal code
3. **Enhance gradually**: Each phase adds specific capabilities
4. **Maintain compatibility**: Later phases extend, not replace
5. **Reach correctness**: Eventually achieve full first-principles design

The MVP provides immediate value while the complete system represents the theoretical ideal. Choose your implementation depth based on your timeline and requirements.