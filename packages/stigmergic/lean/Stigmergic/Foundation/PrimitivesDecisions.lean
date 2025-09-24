import Stigmergic.Meta.NormativeDecision

/-!
# Stigmergic Primitives Module Normative Decisions

This file documents all normative (value-laden) decisions made in the design
and implementation of the Stigmergic Primitives module. These decisions are
first-class specification objects that can be versioned, tracked, and evolved.

## Overview

Each decision captures:
- The choice made
- Alternatives considered
- Rationale for the decision
- Dependencies on other decisions
- Historical context

## Main Categories

- **DC (Definitional Commitments)**: Core ontological choices
- **OA (Ontological Assumptions)**: What exists in our model
- **AD (Architectural Decisions)**: System design choices
-/

namespace Stigmergic.Foundation

open Stigmergic.Meta

section PrimitivesDecisions

/-- Use Lean 4 for formal specification with MVP focus -/
def DC_STGM_PRIM_1 : NormativeDecision := {
  id := ⟨"DC-STGM-PRIM-1"⟩
  date := 1737500000  -- 2025-01-22 approximate
  type := .DC
  decision := "Use Lean 4 for formal specification with MVP focus on stigmergic coordination"
  alternatives := [
    ("Informal specification only", "lacks mathematical rigor and machine verification"),
    ("Coq", "steeper learning curve, less modern tooling"),
    ("TLA+", "less suited for type-driven development"),
    ("Python type hints only", "insufficient for formal verification")
  ]
  rationale := [
    "Lean 4 provides executable specifications with proofs",
    "Type-driven development ensures correctness by construction",
    "MVP approach allows incremental formalization",
    "Strong mathlib support for mathematical foundations",
    "Clear path from specification to implementation"
  ]
  dependencies := []
  status := .Active
  context := some "Starting with minimal viable primitives for stigmergic systems, adding complexity only as needed"
  supersededBy := none
}

/-- Model time as continuous non-negative reals -/
def DC_STGM_PRIM_2 : NormativeDecision := {
  id := ⟨"DC-STGM-PRIM-2"⟩
  date := 1737500000
  type := .DC
  decision := "Model time as continuous non-negative real values (NNReal)"
  alternatives := [
    ("Discrete time steps", "artificial discretization of natural processes"),
    ("Integer timestamps", "insufficient precision for decay calculations"),
    ("Complex time with uncertainty", "premature complexity for MVP"),
    ("No time model", "essential for signal aging and decay")
  ]
  rationale := [
    "Continuous time allows smooth decay functions",
    "NNReal ensures non-negativity by construction",
    "Mathematical rigor through Mathlib types",
    "Natural representation of temporal processes",
    "Avoids discretization artifacts"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "Time is fundamental to stigmergic systems where signals decay over time"
  supersededBy := none
}

/-- Use phantom types for ID type safety -/
def DC_STGM_PRIM_3 : NormativeDecision := {
  id := ⟨"DC-STGM-PRIM-3"⟩
  date := 1737500000
  type := .DC
  decision := "Use phantom type parameters for compile-time ID type safety"
  alternatives := [
    ("Single ID type", "allows mixing different ID types at runtime"),
    ("String prefixes", "runtime checking only, not compile-time safe"),
    ("Separate types", "code duplication without benefit"),
    ("Numeric IDs", "loses semantic meaning and flexibility")
  ]
  rationale := [
    "Zero runtime cost with compile-time safety",
    "Cannot accidentally pass SignalId where AgentId expected",
    "Phantom types are erased at runtime",
    "Clean, type-safe API",
    "Standard functional programming pattern"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "This pattern prevents entire classes of bugs where wrong ID types are passed"
  supersededBy := none
}

/-- Metadata as simple key-value pairs -/
def DC_STGM_PRIM_4 : NormativeDecision := {
  id := ⟨"DC-STGM-PRIM-4"⟩
  date := 1737500000
  type := .DC
  decision := "Metadata as simple key-value pairs with last-write-wins semantics"
  alternatives := [
    ("Complex metadata schema", "premature complexity for MVP"),
    ("Fixed fields only", "insufficient flexibility"),
    ("JSON objects", "requires parsing and validation"),
    ("No metadata", "needed for extensibility")
  ]
  rationale := [
    "Simple and sufficient for MVP",
    "List of pairs preserves order",
    "Last-write-wins is predictable",
    "Easy to extend later if needed",
    "No parsing or schema validation needed"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "Can be extended to more sophisticated metadata models as requirements evolve"
  supersededBy := none
}

/-- DecayFactor as constrained type -/
def DC_STGM_PRIM_5 : NormativeDecision := {
  id := ⟨"DC-STGM-PRIM-5"⟩
  date := 1737500000
  type := .DC
  decision := "DecayFactor as a constrained type with proofs (0 < factor ≤ 1)"
  alternatives := [
    ("Unconstrained float", "allows invalid values like negative or > 1"),
    ("No decay model", "essential for stigmergic signal weakening"),
    ("Discrete decay levels", "loses precision in decay calculations"),
    ("Time-based removal only", "too coarse, loses gradual weakening")
  ]
  rationale := [
    "Constraints enforced by type system",
    "Mathematical proofs of decay properties",
    "Cannot create invalid decay factors",
    "Smart constructor validates input",
    "Exponential decay is standard model"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩, ⟨"DC-STGM-PRIM-2"⟩]
  status := .Active
  context := some "DecayFactor.standard (0.95) removed temporarily due to proof complexity, but pattern established"
  supersededBy := none
}

/-- Signals, Agents, and Environments as core entities -/
def OA_STGM_PRIM_1 : NormativeDecision := {
  id := ⟨"OA-STGM-PRIM-1"⟩
  date := 1737500000
  type := .OA
  decision := "Signals, Agents, and Environments exist as fundamental stigmergic entities"
  alternatives := [
    ("Only agents and messages", "misses environmental persistence"),
    ("Just environment state", "loses signal identity and history"),
    ("Agents only", "no indirect communication mechanism"),
    ("Events instead of signals", "events are transient, signals persist")
  ]
  rationale := [
    "Signals enable indirect communication",
    "Agents are the active entities",
    "Environments hold and manage signals",
    "This trinity is fundamental to stigmergy",
    "Each has distinct identity via phantom types"
  ]
  dependencies := [⟨"DC-STGM-PRIM-3"⟩]
  status := .Active
  context := some "This ontology directly reflects stigmergic theory from biology and complex systems"
  supersededBy := none
}

/-- Properties must be proven, not assumed -/
def OA_STGM_PRIM_2 : NormativeDecision := {
  id := ⟨"OA-STGM-PRIM-2"⟩
  date := 1737500000
  type := .OA
  decision := "All operation properties must have proven theorems"
  alternatives := [
    ("Documentation only", "not machine-checkable"),
    ("Runtime assertions", "catches bugs too late"),
    ("Unit tests only", "not exhaustive"),
    ("No property specification", "loses correctness guarantees")
  ]
  rationale := [
    "If a property matters, the compiler must check it",
    "Theorems provide mathematical certainty",
    "Proofs catch errors at specification time",
    "Properties compose through proven preservation",
    "Documentation can lie, proofs cannot"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "This is why we prove age_monotonic, metadata_add_get, decay_non_increasing, etc."
  supersededBy := none
}

/-- Defer complex features until needed -/
def AD_STGM_PRIM_1 : NormativeDecision := {
  id := ⟨"AD-STGM-PRIM-1"⟩
  date := 1737500000
  type := .AD
  decision := "Defer complex features until actually needed (MVP principle)"
  alternatives := [
    ("Build everything upfront", "premature complexity"),
    ("Anticipate all future needs", "YAGNI - You Aren't Gonna Need It"),
    ("Complex type hierarchies", "overengineering for current needs")
  ]
  rationale := [
    "Start with minimal working system",
    "Add complexity only when requirements demand it",
    "Easier to extend simple system than simplify complex one",
    "Faster iteration and learning",
    "Focus on core stigmergic mechanisms first"
  ]
  dependencies := []
  status := .Active
  context := some "This is why we removed complex theorem proofs that aren't immediately needed"
  supersededBy := none
}

/-- Use linter suppressions minimally -/
def AD_STGM_PRIM_2 : NormativeDecision := {
  id := ⟨"AD-STGM-PRIM-2"⟩
  date := 1737500000
  type := .AD
  decision := "Use linter suppressions only when absolutely necessary"
  alternatives := [
    ("Disable all linters", "loses valuable correctness checks"),
    ("Suppress warnings liberally", "hides potential issues"),
    ("Custom linter configuration", "maintenance burden")
  ]
  rationale := [
    "Linters catch real issues",
    "Only suppress with clear justification",
    "Currently only minImports and upstreamableDecl suppressed",
    "upstreamableDecl temporary until domain-specific coupling added",
    "Warnings as errors ensures clean code"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "Plan to remove upstreamableDecl suppression by adding more domain-specific theorems"
  supersededBy := none
}

/-- Collection of all primitives decisions for easy access -/
def primitivesDecisions : List NormativeDecision := [
  DC_STGM_PRIM_1, DC_STGM_PRIM_2, DC_STGM_PRIM_3, DC_STGM_PRIM_4, DC_STGM_PRIM_5,
  OA_STGM_PRIM_1, OA_STGM_PRIM_2,
  AD_STGM_PRIM_1, AD_STGM_PRIM_2
]

/-- Generate a decision log for the Primitives module -/
def primitivesDecisionLog : String :=
  generateDecisionLog primitivesDecisions "Stigmergic Primitives Module Normative Decisions"

end PrimitivesDecisions

end Stigmergic.Foundation
