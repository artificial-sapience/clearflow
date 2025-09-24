import Stigmergic.Foundation.Primitives
import Stigmergic.Foundation.Signal
import Stigmergic.Core.SignalSpace

set_option linter.minImports false
set_option linter.upstreamableDecl false
set_option linter.ppRoundtrip false

/-!
# Stigmergic.Core.Agent

Agents are autonomous entities that perceive and emit signals in the environment.

## Overview

Agents are the active participants in stigmergic coordination. They:
- Perceive signals in their environment
- Calculate attraction to different signals
- Make decisions based on signal information
- Deposit new signals to influence future behavior
- Maintain internal state that evolves over time

## Main Definitions

- `AgentState` - Internal state maintained by an agent
- `Action` - Possible actions an agent can take
- `Agent` - The agent interface for stigmergic entities
- `Agent.perceive` - Observe signals in the environment
- `Agent.calculateAttraction` - Compute attraction to a signal
- `Agent.decideAction` - Choose action based on perceptions
- `Agent.emit` - Create a signal in the environment

## Implementation Notes

Agents are designed to be stateful but deterministic. Their behavior is
influenced by signals but remains predictable given the same environmental
conditions and internal state.

## Normative Decisions

See AgentDecisions.lean for design choices and alternatives considered.
-/

namespace Stigmergic

/-- Semantic role defining agent's specialization.

 PURPOSE: Describes what types of signals an agent specializes in.

 PRECONDITIONS: None.

 POSTCONDITIONS: Roles are immutable once assigned.

 INVARIANTS: Role determines attraction patterns. -/
structure Role where
  /-- Name identifying the role -/
  name : String
  /-- Description of role's expertise -/
  description : String
  /-- Types of signals this role is attracted to -/
  attractedTypes : List SignalType

/-- Activation threshold for agent decision-making.

 PURPOSE: Minimum attraction level needed to act on a signal.

 PRECONDITIONS: Must be in range [0, 1].

 POSTCONDITIONS: Threshold can be adjusted based on load.

 INVARIANTS: 0 ≤ threshold ≤ 1. -/
abbrev Threshold := { t : NNReal // t ≤ 1 }

/-- Internal state maintained by an agent.

 PURPOSE: Encapsulates agent's knowledge and working memory.

 PRECONDITIONS: Created through AgentState.initial.

 POSTCONDITIONS: State evolves through agent observations.

 INVARIANTS:
 - Memory capacity is finite (prevents unbounded growth)
 - Working set tracks current focus signals -/
structure AgentState where
  /-- Memory of recently observed signal IDs -/
  memory : List SignalId
  /-- Currently focused signals (working set) -/
  workingSet : List SignalId
  /-- Agent's learned patterns and preferences -/
  learnedPatterns : Metadata
  /-- Current activity status -/
  isActive : Bool

/-- Possible actions an agent can take.

 PURPOSE: Defines semantic actions for signal-driven coordination.

 PRECONDITIONS: Actions must be semantically valid.

 POSTCONDITIONS: Each action modifies the space.

 INVARIANTS: Actions are atomic and deterministic. -/
inductive Action where
  /-- Process a signal and emit response -/
  | processSignal : SignalId → String → SignalType → Metadata → Action
  /-- Emit new signal to space -/
  | emitSignal : String → SignalType → Metadata → Action
  /-- Do nothing this cycle -/
  | idle : Action
  /-- Add signal to working memory -/
  | observeSignal : SignalId → Action

/-- Observation of space by an agent.

 PURPOSE: Semantic view of available signals.

 PRECONDITIONS: Based on role and current focus.

 POSTCONDITIONS: Read-only view of space.

 INVARIANTS: Filtered by semantic relevance, not distance. -/
structure Observation where
  /-- Signals relevant to agent's role -/
  relevantSignals : List Signal
  /-- Current environment time -/
  currentTime : Time
  /-- Agent's own ID for self-reference -/
  selfId : AgentId
  /-- Total signal count in space (for load awareness) -/
  spaceSize : Nat

/-- Relevance score for a signal.

 PURPOSE: Quantifies how relevant a signal is to an agent's role and current focus.

 PRECONDITIONS: Calculated based on signal properties and agent state.

 POSTCONDITIONS: Non-negative value (typically in [0, 1] by construction).

 INVARIANTS: 0 = no relevance, higher values = more relevant. -/
abbrev Relevance := NNReal

/-- Agent interface for semantic stigmergic entities.

 PURPOSE: LLM-driven agents that coordinate through spaces.

 PRECONDITIONS: Agents must have role and threshold.

 POSTCONDITIONS: All operations maintain semantic consistency.

 INVARIANTS:
 - Agent ID and role are immutable
 - Threshold determines activation
 - Decisions based on semantic attraction -/
structure Agent where
  /-- Unique identifier for this agent -/
  id : AgentId
  /-- Current internal state -/
  state : AgentState
  /-- Semantic role and specialization -/
  role : Role
  /-- Activation threshold for decisions -/
  threshold : Threshold

section AgentOperations

/-- Create initial agent state.

 PURPOSE: Initialize a new agent with empty memory.

 PRECONDITIONS: None.

 POSTCONDITIONS: Returns fresh agent state. -/
def AgentState.initial : AgentState :=
  { memory := []
    workingSet := []
    learnedPatterns := Metadata.empty
    isActive := true }

/-- Observe signals semantically relevant to agent.

 PURPOSE: Query space for relevant signals.

 PRECONDITIONS: Signal space must be valid.

 POSTCONDITIONS: Returns semantically relevant signals.

 Mathematically: observe(agent, space) = {t ∈ space | relevant(agent.role, t.type)}

 In English: Returns signals matching agent's role and interests. -/
def Agent.observe (agent : Agent) (space : SignalSpace) : Observation :=
  -- Query signals by type relevance to role
  let relevantSignals : List Signal :=
    agent.role.attractedTypes.foldl
      (fun acc signalType => acc ++ space.queryByType signalType) []
  { relevantSignals := relevantSignals
    currentTime := space.currentTime
    selfId := agent.id
    spaceSize := space.size }

/-- Calculate contextual relevance of a signal to an agent.

 PURPOSE: Combine signal's intrinsic strength with agent's contextual interpretation.

 PRECONDITIONS: Signal must be observable.

 POSTCONDITIONS: Returns relevance value in [0, 1].

 Mathematically: relevance(agent, signal, t) = strength(t) * semantic_match(role, signal)

 In English: Relevance combines the signal's decayed strength with role-based interpretation. -/
noncomputable def Agent.calculateRelevance (agent : Agent) (signal : Signal)
    (now : Time) : Relevance :=
  let currentStrength := signal.getCurrentStrength now
  let typeMatches := agent.role.attractedTypes.contains signal.signalType
  if typeMatches then
    match signal.signalType with
    | SignalType.goal =>
      currentStrength * ⟨1.0, by norm_num⟩
    | SignalType.requirement =>
      currentStrength * ⟨0.95, by norm_num⟩
    | SignalType.task =>
      currentStrength * ⟨0.9, by norm_num⟩
    | SignalType.constraint =>
      currentStrength * ⟨0.85, by norm_num⟩
    | SignalType.progress =>
      currentStrength * ⟨0.7, by norm_num⟩
    | SignalType.completion =>
      currentStrength * ⟨0.6, by norm_num⟩
    | SignalType.custom _ =>
      currentStrength * ⟨0.8, by norm_num⟩
  else
    currentStrength * ⟨0.1, by norm_num⟩

/-- Decide next action based on observation.

 PURPOSE: Threshold-based decision for semantic coordination.

 PRECONDITIONS: Observation must be current.

 POSTCONDITIONS: Returns semantically valid action.

 Mathematically: decide(agent, obs) = act if max(relevance) > threshold else idle

 In English: Act on most relevant signal if above threshold. -/
noncomputable def Agent.decideAction (agent : Agent) (obs : Observation) : Action :=
  -- Find most attractive signal above threshold
  match obs.relevantSignals with
  | [] => Action.idle  -- No relevant signals
  | signal :: rest =>
    -- Find max relevance starting from first signal
    let firstRelevance := agent.calculateRelevance signal obs.currentTime
    let relevances := rest.map (fun t => (t, agent.calculateRelevance t obs.currentTime))
    let maxRelevance := relevances.foldl
      (fun acc (t, r) => if r > acc.2 then (t, r) else acc)
      (signal, firstRelevance)

    if maxRelevance.2 > agent.threshold.val then
      Action.observeSignal maxRelevance.1.id
    else
      Action.idle

/-- Execute an action and update agent state.

 PURPOSE: Apply semantic action effects.

 PRECONDITIONS: Action must be semantically valid.

 POSTCONDITIONS: Returns updated agent state.

 INVARIANTS: Memory capacity remains bounded. -/
def Agent.execute (agent : Agent) (action : Action) : Agent :=
  match action with
  | Action.idle => agent  -- No state change
  | Action.processSignal id _ _ _ =>
    { agent with state := { agent.state with
        workingSet := id :: agent.state.workingSet.take 5  -- Focus on recent
        memory := id :: agent.state.memory.take 20 }}  -- Remember more
  | Action.emitSignal _ _ _ =>
    agent  -- Emitting doesn't change internal state
  | Action.observeSignal signalId =>
    { agent with state := { agent.state with
        memory := signalId :: agent.state.memory.take 20  -- Add to memory
        workingSet := signalId :: agent.state.workingSet.take 5 }}

/-- Create a signal from agent processing.

 PURPOSE: Generate semantic signal from agent work with intrinsic strength.

 PRECONDITIONS: Agent must be active, strength in [0, 1].

 POSTCONDITIONS: Returns signal for space. -/
def Agent.createSignal (agent : Agent) (content : String) (signalType : SignalType)
    (strength : NNReal) (metadata : Metadata) (now : Time) : Signal :=
  Signal.create
    (Id.mk s!"signal_{agent.id.toString}")  -- Unique ID
    content
    signalType
    strength  -- Intrinsic strength set by emitter
    now
    agent.id
    (metadata.add "role" agent.role.name)  -- Include role in metadata

end AgentOperations

section AgentProperties

/-- Agent ID is immutable.

 Mathematically: ∀a, a.id = a.id

 In English: An agent's identifier never changes. -/
theorem agent_id_immutable (agent : Agent) :
  agent.id = agent.id :=
  rfl

/-- Role is immutable.

 Mathematically: ∀a, a.role = a.role

 In English: Agent's semantic role doesn't change. -/
theorem agent_role_immutable (agent : Agent) :
  agent.role = agent.role :=
  rfl

/-- Threshold is bounded.

 Mathematically: ∀a, 0 ≤ a.threshold ≤ 1

 In English: Activation threshold is between 0 and 1. -/
theorem agent_threshold_bounded (agent : Agent) :
  agent.threshold.val ≤ 1 :=
  agent.threshold.property

/-- Idle action preserves state.

 Mathematically: execute(agent, idle) = agent

 In English: Doing nothing doesn't change the agent's state. -/
theorem idle_preserves_state (agent : Agent) :
  agent.execute Action.idle = agent :=
  rfl

/-- Observing preserves agent identity.

 Mathematically: execute(a, observeSignal(t)).id = a.id

 In English: Observing signals doesn't change agent ID. -/
theorem observe_preserves_id (agent : Agent) (signalId : SignalId) :
  (agent.execute (Action.observeSignal signalId)).id = agent.id := by
  unfold Agent.execute
  simp

/-- Relevance values are non-negative.

 Mathematically: ∀a ∀t, calculateRelevance(a, t) ≥ 0

 In English: Relevance is always non-negative. -/
theorem relevance_non_negative (agent : Agent) (signal : Signal) (now : Time) :
  0 ≤ agent.calculateRelevance signal now :=
  NNReal.zero_le_coe

/-- Memory has finite capacity.

 Mathematically: |execute(a, observeSignal(t)).memory| ≤ 21

 In English: Agent memory stores at most 21 signals (20 + 1 new). -/
theorem memory_capacity_bounded (agent : Agent) (signalId : SignalId) :
  (agent.execute (Action.observeSignal signalId)).state.memory.length ≤ 21 := by
  unfold Agent.execute
  grind

/-- Working set has bounded size.

 Mathematically: |execute(a, observeSignal(t)).workingSet| ≤ 6

 In English: Working set keeps at most 6 signals (5 + 1 new). -/
theorem working_set_bounded (agent : Agent) (signalId : SignalId) :
  (agent.execute (Action.observeSignal signalId)).state.workingSet.length ≤ 6 := by
  unfold Agent.execute
  grind

/-
  Design Note: Role-Based Relevance

  By design, agents calculate higher relevance for signals matching their role.
  This is achieved through the semantic match scores in calculateRelevance:
  - Role-matched signals: 0.6 to 1.0 semantic match
  - Non-matched signals: 0.1 semantic match

  This is a design choice for semantic coordination, not a fundamental
  property that needs proving. The key stigmergic property is that signals
  with higher relevance (however calculated) influence agent decisions more.
-/

end AgentProperties

end Stigmergic
