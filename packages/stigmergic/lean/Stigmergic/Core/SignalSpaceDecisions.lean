import Stigmergic.Meta.Decision

/-!
# Stigmergic.Core.Space - Normative Decisions

This file documents the normative decisions made in the Space module design.

## Overview

The Space module defines the shared semantic signal space for signal-driven coordination.
Key decisions involve signal handling, semantic querying, and LLM agent coordination.

## Categories

- DC_STGM_SPACE_* : Definitional choices (what constitutes a signal space)
- OA_STGM_SPACE_* : Ontological assumptions (agent-space relationship)
- AD_STGM_SPACE_* : Architectural decisions (implementation approach)
-/

namespace Stigmergic.Core

open Stigmergic.Meta

section SpaceDefinitionalChoices

/-- DC_STGM_SPACE_1: Signal-based coordination model.

 DECISION: Coordination through persistent signal signals, not spatial proximity.

 ALTERNATIVES:
 - Spatial environment: Physical distance-based
 - Shared memory: Direct memory access
 - Event bus: Transient events

 RATIONALE:
 - Matches LLM agent capabilities (semantic understanding)
 - No physical constraints (energy, position)
 - Persistent signals enable learning

 DEPENDENCIES: Affects all agent interactions.

 STATUS: Active -/
def DC_STGM_SPACE_1 : NormativeDecision := {
  id := ⟨"DC-STGM-SPACE-1"⟩
  date := 1737500000  -- 2025-01-22 approximate
  type := .DC
  decision := "Coordination through persistent signal signals"
  alternatives := [
    ("Spatial environment", "doesn't match LLM capabilities"),
    ("Shared memory", "lacks emergence properties"),
    ("Event bus", "transient, no persistence")
  ]
  rationale := [
    "Matches LLM semantic capabilities",
    "No physical constraints",
    "Persistent signals enable learning"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Signal-based coordination"
}

/-- DC_STGM_SPACE_2: Semantic querying over spatial indexing.

 DECISION: Agents query by type, content, and recency, not location.

 ALTERNATIVES:
 - Distance-based: Query within radius
 - Graph-based: Network topology queries
 - Random sampling: Stochastic discovery

 RATIONALE:
 - Semantic relevance matters, not proximity
 - Type-based queries match role specialization
 - Content queries enable semantic search

 DEPENDENCIES: Affects Agent.observe operation.

 STATUS: Active -/
def DC_STGM_SPACE_2 : NormativeDecision := {
  id := ⟨"DC-STGM-SPACE-2"⟩
  date := 1737500000
  type := .DC
  decision := "Semantic querying by type, content, and recency"
  alternatives := [
    ("Distance-based queries", "irrelevant for messages"),
    ("Graph topology", "adds unnecessary complexity"),
    ("Random sampling", "inefficient discovery")
  ]
  rationale := [
    "Semantic relevance over proximity",
    "Type queries match role specialization",
    "Content queries enable semantic search"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Query model"
}

/-- DC_STGM_SPACE_3: Immutable signals with unique IDs.

 DECISION: Signals are immutable once published, identified uniquely.

 ALTERNATIVES:
 - Mutable signals: Can edit after publish
 - Version-based: Track signal versions
 - Content-addressed: Use content hash as ID

 RATIONALE:
 - Immutability ensures consistency
 - Unique IDs enable precise reference
 - Simple model for MVP

 DEPENDENCIES: Affects signal lifecycle.

 STATUS: Active -/
def DC_STGM_SPACE_3 : NormativeDecision := {
  id := ⟨"DC-STGM-SPACE-3"⟩
  date := 1737500000
  type := .DC
  decision := "Immutable signals with unique IDs"
  alternatives := [
    ("Mutable signals", "consistency issues"),
    ("Version tracking", "adds complexity"),
    ("Content-addressed", "harder to reference")
  ]
  rationale := [
    "Immutability ensures consistency",
    "Unique IDs enable precise reference",
    "Simple model for MVP"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Signal immutability"
}

end SpaceDefinitionalChoices

section SpaceOntologicalAssumptions

/-- OA_STGM_SPACE_1: Asynchronous agent interaction.

 DECISION: Agents interact asynchronously through the signal space.

 ALTERNATIVES:
 - Synchronous: Agents wait for responses
 - Turn-based: Agents take turns
 - Real-time: Continuous interaction

 RATIONALE:
 - Natural for distributed systems
 - No coordination overhead
 - Scales with agent count

 DEPENDENCIES: Affects system architecture.

 STATUS: Active -/
def OA_STGM_SPACE_1 : NormativeDecision := {
  id := ⟨"OA-STGM-SPACE-1"⟩
  date := 1737500000
  type := .OA
  decision := "Asynchronous agent interaction through signal space"
  alternatives := [
    ("Synchronous interaction", "creates bottlenecks"),
    ("Turn-based", "artificial constraint"),
    ("Real-time", "complex synchronization")
  ]
  rationale := [
    "Natural for distributed systems",
    "No coordination overhead",
    "Scales with agent count"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Interaction model"
}

/-- OA_STGM_SPACE_2: No global view requirement.

 DECISION: Agents don't need complete signal space visibility.

 ALTERNATIVES:
 - Global view: All agents see everything
 - Hierarchical: Different visibility levels
 - Privileged: Some agents see more

 RATIONALE:
 - Realistic bounded perception
 - Reduces information overload
 - Enables specialization

 DEPENDENCIES: Affects observation operations.

 STATUS: Active -/
def OA_STGM_SPACE_2 : NormativeDecision := {
  id := ⟨"OA-STGM-SPACE-2"⟩
  date := 1737500000
  type := .OA
  decision := "Agents have partial signal space visibility"
  alternatives := [
    ("Global visibility", "information overload"),
    ("Hierarchical views", "adds complexity"),
    ("Privileged agents", "breaks emergence")
  ]
  rationale := [
    "Realistic bounded perception",
    "Reduces information overload",
    "Enables specialization"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Visibility model"
}

end SpaceOntologicalAssumptions

section SpaceArchitecturalDecisions

/-- AD_STGM_SPACE_1: Simple list-based queries for MVP.

 DECISION: Use list operations for queries initially.

 ALTERNATIVES:
 - Vector database: Semantic similarity
 - Graph database: Relationship queries
 - Full-text search: Advanced text matching

 RATIONALE:
 - Simple to implement and verify
 - Can upgrade to vector search later
 - Focus on correctness over performance

 DEPENDENCIES: Affects query implementations.

 STATUS: Active -/
def AD_STGM_SPACE_1 : NormativeDecision := {
  id := ⟨"AD-STGM-SPACE-1"⟩
  date := 1737500000
  type := .AD
  decision := "List-based queries for MVP"
  alternatives := [
    ("Vector database", "complex for MVP"),
    ("Graph database", "overkill initially"),
    ("Full-text search", "not needed yet")
  ]
  rationale := [
    "Simple to implement and verify",
    "Can upgrade to vector search later",
    "Focus on correctness first"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Query implementation"
}

/-- AD_STGM_SPACE_2: Optional signal consumption.

 DECISION: Signals can be removed when consumed.

 ALTERNATIVES:
 - Persistent only: Never remove signals
 - Decay-based: Remove old signals
 - Flag-based: Mark as consumed

 RATIONALE:
 - Allows both persistent and consumable patterns
 - Simple removal semantics
 - Signal space doesn't grow unbounded

 DEPENDENCIES: Affects signal space size management.

 STATUS: Active -/
def AD_STGM_SPACE_2 : NormativeDecision := {
  id := ⟨"AD-STGM-SPACE-2"⟩
  date := 1737500000
  type := .AD
  decision := "Optional signal removal on consumption"
  alternatives := [
    ("Never remove", "unbounded growth"),
    ("Time decay", "loses valid signals"),
    ("Consumption flags", "more complex")
  ]
  rationale := [
    "Flexible consumption patterns",
    "Simple removal semantics",
    "Bounded signal space growth"
  ]
  dependencies := []
  status := .Active
  supersededBy := none
  context := some "Signal lifecycle"
}

end SpaceArchitecturalDecisions

end Stigmergic.Core
