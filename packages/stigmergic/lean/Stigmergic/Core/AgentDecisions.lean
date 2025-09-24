import Stigmergic.Meta.NormativeDecision

/-!
# Stigmergic.Core.Agent - Normative Decisions

This file documents the normative decisions made in the Agent module design.

## Overview

The Agent module defines autonomous entities that perceive and emit signals.
Key decisions involve state management, action space, perception model, and
attraction calculation mechanisms.

## Categories

- DC_STGM_AGENT_* : Definitional choices (what constitutes an agent)
- OA_STGM_AGENT_* : Ontological assumptions (agent-environment relationship)
- AD_STGM_AGENT_* : Architectural decisions (implementation approach)
-/

namespace Stigmergic.Core

open Stigmergic.Meta

section AgentDefinitionalChoices

/-- DC_STGM_AGENT_1: Spatial positioning model.

 DECISION: Agents have explicit 2D positions using NNReal coordinates.

 ALTERNATIVES:
 - Graph-based: Nodes and edges instead of continuous space
 - Grid-based: Discrete integer coordinates
 - Abstract: No spatial model, pure signal-based

 RATIONALE:
 - 2D continuous space matches biological stigmergic systems
 - NNReal ensures non-negative coordinates
 - Supports distance-based perception naturally

 DEPENDENCIES: Affects perception range and signal visibility calculations.

 STATUS: Active -/
def DC_STGM_AGENT_1 : NormativeDecision := {
  id := ⟨"DC-STGM-AGENT-1"⟩
  date := 1737500000  -- 2025-01-22 approximate
  type := .DC
  decision := "Agents have explicit 2D positions using NNReal coordinates"
  alternatives := [
    ("Graph-based positions", "less natural for continuous space"),
    ("Grid coordinates", "artificially discrete"),
    ("No spatial model", "loses biological realism")
  ]
  rationale := [
    "Matches biological stigmergic systems",
    "Supports distance-based perception naturally",
    "NNReal ensures non-negative coordinates"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Spatial positioning model"
}

/-- DC_STGM_AGENT_2: Energy model for action costs.

 DECISION: All actions except idle consume energy from a finite space.

 ALTERNATIVES:
 - No energy: Unlimited actions
 - Time-based: Actions take time instead of energy
 - Resource-specific: Different resources for different actions

 RATIONALE:
 - Creates realistic constraints on agent behavior
 - Prevents infinite action loops
 - Simple unified resource model

 DEPENDENCIES: Affects action execution and agent lifecycle.

 STATUS: Active -/
def DC_STGM_AGENT_2 : NormativeDecision := {
  id := ⟨"DC-STGM-AGENT-2"⟩
  date := 1737500000
  type := .DC
  decision := "All actions except idle consume energy from finite space"
  alternatives := [
    ("No energy constraints", "unrealistic unlimited actions"),
    ("Time-based costs", "more complex scheduling"),
    ("Multiple resources", "unnecessary complexity for MVP")
  ]
  rationale := [
    "Creates realistic constraints on agent behavior",
    "Prevents infinite action loops",
    "Simple unified resource model"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Energy model for actions"
}

/-- DC_STGM_AGENT_3: Memory as signal ID list.

 DECISION: Agent memory stores a list of recently encountered signal IDs.

 ALTERNATIVES:
 - Full signals: Store complete signal objects
 - Summary statistics: Aggregate information only
 - No memory: Purely reactive agents

 RATIONALE:
 - Lightweight memory model (just IDs)
 - Supports learning from past encounters
 - Bounded size prevents unbounded growth

 DEPENDENCIES: Affects decision-making and learning capabilities.

 STATUS: Active -/
def DC_STGM_AGENT_3 : NormativeDecision := {
  id := ⟨"DC-STGM-AGENT-3"⟩
  date := 1737500000
  type := .DC
  decision := "Memory stores list of recently encountered signal IDs"
  alternatives := [
    ("Store full signals", "higher memory overhead"),
    ("Summary statistics", "loses specific signal info"),
    ("No memory", "purely reactive behavior")
  ]
  rationale := [
    "Lightweight memory model (just IDs)",
    "Supports learning from past encounters",
    "Bounded size prevents unbounded growth"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Memory model"
}

/-- DC_STGM_AGENT_4: Attraction as bounded NNReal.

 DECISION: Attraction values are NNReal values bounded to [0, 1].

 ALTERNATIVES:
 - Unbounded: Any positive real number
 - Discrete: Fixed levels (low/medium/high)
 - Vector: Multi-dimensional attraction

 RATIONALE:
 - Normalized values simplify comparison
 - NNReal ensures non-negative attraction
 - Single value keeps model simple

 DEPENDENCIES: Affects calculateAttraction and decision logic.

 STATUS: Active -/
def DC_STGM_AGENT_4 : NormativeDecision := {
  id := ⟨"DC-STGM-AGENT-4"⟩
  date := 1737500000
  type := .DC
  decision := "Attraction as NNReal bounded to [0, 1]"
  alternatives := [
    ("Unbounded values", "difficult to compare"),
    ("Discrete levels", "loses granularity"),
    ("Vector attraction", "too complex for MVP")
  ]
  rationale := [
    "Normalized values simplify comparison",
    "NNReal ensures non-negative attraction",
    "Single value keeps model simple"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Attraction value model"
}

end AgentDefinitionalChoices

section AgentOntologicalAssumptions

/-- OA_STGM_AGENT_1: Deterministic behavior.

 DECISION: Agent decisions are deterministic given state and perception.

 ALTERNATIVES:
 - Stochastic: Probabilistic action selection
 - Learning: Behavior changes over time
 - Hybrid: Mix of deterministic and random

 RATIONALE:
 - Simplifies reasoning and proofs
 - Reproducible behavior for testing
 - Emergent complexity from interactions

 DEPENDENCIES: Affects all agent operations and theorems.

 STATUS: Active -/
def OA_STGM_AGENT_1 : NormativeDecision := {
  id := ⟨"OA-STGM-AGENT-1"⟩
  date := 1737500000
  type := .OA
  decision := "Agent decisions are deterministic given state and perception"
  alternatives := [
    ("Stochastic behavior", "harder to reason about"),
    ("Learning agents", "more complex state"),
    ("Hybrid approach", "unclear semantics")
  ]
  rationale := [
    "Simplifies reasoning and proofs",
    "Reproducible behavior for testing",
    "Emergent complexity from interactions"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Behavioral determinism"
}

/-- OA_STGM_AGENT_2: Local perception only.

 DECISION: Agents can only perceive signals within their perception range.

 ALTERNATIVES:
 - Global perception: See all signals
 - Type-filtered: See all signals of certain types globally
 - Network-based: Perception through agent connections

 RATIONALE:
 - Realistic bounded rationality
 - Enables local coordination patterns
 - Scalable to large environments

 DEPENDENCIES: Affects perceive operation and decision-making.

 STATUS: Active -/
def OA_STGM_AGENT_2 : NormativeDecision := {
  id := ⟨"OA-STGM-AGENT-2"⟩
  date := 1737500000
  type := .OA
  decision := "Agents only perceive signals within perception range"
  alternatives := [
    ("Global perception", "unrealistic omniscience"),
    ("Type-filtered global", "still too powerful"),
    ("Network perception", "adds complexity")
  ]
  rationale := [
    "Realistic bounded rationality",
    "Enables local coordination patterns",
    "Scalable to large environments"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Perception locality"
}

/-- OA_STGM_AGENT_3: Immutable agent identity.

 DECISION: Agent IDs are immutable throughout agent lifecycle.

 ALTERNATIVES:
 - Mutable IDs: Can change identity
 - Anonymous: No persistent identity
 - Hierarchical: IDs encode relationships

 RATIONALE:
 - Enables tracking agent behavior
 - Simplifies signal attribution
 - Clear ownership of signals

 DEPENDENCIES: Affects signal creation and agent tracking.

 STATUS: Active -/
def OA_STGM_AGENT_3 : NormativeDecision := {
  id := ⟨"OA-STGM-AGENT-3"⟩
  date := 1737500000
  type := .OA
  decision := "Agent IDs are immutable throughout lifecycle"
  alternatives := [
    ("Mutable identity", "tracking becomes complex"),
    ("Anonymous agents", "no accountability"),
    ("Hierarchical IDs", "unnecessary structure")
  ]
  rationale := [
    "Enables tracking agent behavior",
    "Simplifies signal attribution",
    "Clear ownership of signals"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Identity persistence"
}

end AgentOntologicalAssumptions

section AgentArchitecturalDecisions

/-- AD_STGM_AGENT_1: Simplified action space.

 DECISION: Limited to move, emit, idle, and follow actions.

 ALTERNATIVES:
 - Rich actions: Many specialized action types
 - Compositional: Combine primitive actions
 - Programmable: User-defined action types

 RATIONALE:
 - MVP focuses on core stigmergic behavior
 - Sufficient for demonstrating coordination
 - Easy to extend later

 DEPENDENCIES: Affects execute operation and energy costs.

 STATUS: Active -/
def AD_STGM_AGENT_1 : NormativeDecision := {
  id := ⟨"AD-STGM-AGENT-1"⟩
  date := 1737500000
  type := .AD
  decision := "Limited to move, emit, idle, follow actions"
  alternatives := [
    ("Rich action set", "too complex for MVP"),
    ("Compositional actions", "harder to analyze"),
    ("User-defined actions", "loses formal properties")
  ]
  rationale := [
    "MVP focuses on core stigmergic behavior",
    "Sufficient for demonstrating coordination",
    "Easy to extend later"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Action space design"
}

/-- AD_STGM_AGENT_2: Manhattan distance for MVP.

 DECISION: Use Manhattan distance instead of Euclidean for simplicity.

 ALTERNATIVES:
 - Euclidean: True geometric distance
 - Chebyshev: Max of coordinate differences
 - Custom: Domain-specific distance metrics

 RATIONALE:
 - Avoids square root computation
 - Sufficient for MVP demonstration
 - Can upgrade to Euclidean later

 DEPENDENCIES: Affects Position.distance and perception range.

 STATUS: Active -/
def AD_STGM_AGENT_2 : NormativeDecision := {
  id := ⟨"AD-STGM-AGENT-2"⟩
  date := 1737500000
  type := .AD
  decision := "Manhattan distance for position calculations"
  alternatives := [
    ("Euclidean distance", "requires sqrt computation"),
    ("Chebyshev distance", "less intuitive"),
    ("Custom metrics", "too flexible")
  ]
  rationale := [
    "Computational simplicity for MVP",
    "Avoids square root computation",
    "Can upgrade to Euclidean later"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Distance metric"
}

/-- AD_STGM_AGENT_3: Fixed energy costs.

 DECISION: Hard-coded energy costs for each action type.

 ALTERNATIVES:
 - Dynamic costs: Based on environment state
 - Configurable: User-specified costs
 - Learning: Agents learn optimal energy use

 RATIONALE:
 - Simple and predictable
 - Easy to reason about
 - Can make configurable later

 DEPENDENCIES: Affects Agent.execute and energy management.

 STATUS: Active -/
def AD_STGM_AGENT_3 : NormativeDecision := {
  id := ⟨"AD-STGM-AGENT-3"⟩
  date := 1737500000
  type := .AD
  decision := "Fixed hard-coded costs per action type"
  alternatives := [
    ("Dynamic costs", "harder to predict"),
    ("Configurable costs", "more complex API"),
    ("Learned costs", "non-deterministic")
  ]
  rationale := [
    "Simplicity and predictability for MVP",
    "Easy to reason about",
    "Can make configurable later"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Energy cost model"
}

/-- AD_STGM_AGENT_4: Type-based attraction.

 DECISION: Base attraction primarily on signal type with age decay.

 ALTERNATIVES:
 - Content-based: Parse signal content for attraction
 - Learning: Agents learn what to be attracted to
 - Multi-factor: Complex attraction function

 RATIONALE:
 - Simple type-based model for MVP
 - Age decay adds temporal dynamics
 - Foundation for more complex models

 DEPENDENCIES: Affects calculateAttraction implementation.

 STATUS: Active -/
def AD_STGM_AGENT_4 : NormativeDecision := {
  id := ⟨"AD-STGM-AGENT-4"⟩
  date := 1737500000
  type := .AD
  decision := "Type-based attraction with age decay"
  alternatives := [
    ("Content analysis", "requires parsing"),
    ("Learned attraction", "non-deterministic"),
    ("Complex multi-factor", "hard to tune")
  ]
  rationale := [
    "Simple MVP model with temporal dynamics",
    "Age decay adds realism",
    "Foundation for more complex models"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Attraction calculation"
}

/-- AD_STGM_AGENT_5: Memory capacity limit.

 DECISION: Agent memory limited to 10 most recent signal IDs.

 ALTERNATIVES:
 - Unlimited: Unbounded memory
 - Time-based: Forget after time period
 - Importance-based: Keep most important

 RATIONALE:
 - Prevents unbounded growth
 - Simple FIFO replacement
 - Sufficient for local coordination

 DEPENDENCIES: Affects memory management in followSignal action.

 STATUS: Active -/
def AD_STGM_AGENT_5 : NormativeDecision := {
  id := ⟨"AD-STGM-AGENT-5"⟩
  date := 1737500000
  type := .AD
  decision := "Limited to 10 most recent signal IDs"
  alternatives := [
    ("Unlimited memory", "unbounded growth"),
    ("Time-based forgetting", "more complex"),
    ("Importance-based", "requires ranking")
  ]
  rationale := [
    "Bounded growth with simple FIFO",
    "Sufficient for coordination",
    "Easy to understand and implement"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Memory capacity"
}

end AgentArchitecturalDecisions

end Stigmergic.Core
