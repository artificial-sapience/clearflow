import Stigmergic.Meta.Decision

/-!
# Stigmergic Signal Module Normative Decisions

This file documents all normative (value-laden) decisions made in the design
and implementation of the Stigmergic Signal module. These decisions are
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

section SignalDecisions

/-- Signals are immutable after creation -/
def DC_STGM_TRACE_1 : NormativeDecision := {
  id := ⟨"DC-STGM-TRACE-1"⟩
  date := 1737500000  -- 2025-01-22 approximate
  type := .DC
  decision := "Signals are immutable after creation - any 'modification' creates a new signal"
  alternatives := [
    ("Mutable signals", "leads to race conditions and non-deterministic behavior"),
    ("Versioned signals", "adds complexity without clear benefit"),
    ("Update-in-place", "violates functional programming principles"),
    ("Event sourcing", "too complex for MVP")
  ]
  rationale := [
    "Immutability ensures deterministic stigmergic dynamics",
    "Simplifies reasoning about system state",
    "No race conditions or synchronization issues",
    "Signals represent historical facts that don't change",
    "Functional programming best practice"
  ]
  dependencies := [⟨"DC-STGM-PRIM-1"⟩]
  status := .Active
  context := some "This is why addMetadata creates a new signal rather than modifying existing"
  supersededBy := none
}

/-- SignalType as simple string -/
def DC_STGM_TRACE_2 : NormativeDecision := {
  id := ⟨"DC-STGM-TRACE-2"⟩
  date := 1737500000
  type := .DC
  decision := "SignalType is a string alias for flexibility and simplicity"
  alternatives := [
    ("Enumeration", "limits extensibility for domain-specific types"),
    ("Type class", "overengineered for current needs"),
    ("Complex type hierarchy", "premature abstraction"),
    ("No typing", "loses semantic categorization")
  ]
  rationale := [
    "Maximum flexibility for domain-specific signal types",
    "No need to modify core spec for new signal types",
    "Simple string comparison for filtering",
    "Can refine to enumeration later if needed",
    "Common types like 'pheromone', 'marker' are just conventions"
  ]
  dependencies := [⟨"AD-STGM-PRIM-1"⟩]
  status := .Superseded
  context := some "Allows users to define domain-specific signal types without modifying core specification"
  supersededBy := some ⟨"DC-STGM-TRACE-2-REV"⟩
}

/-- SignalType as structured type with custom escape hatch (REVISED) -/
def DC_STGM_TRACE_2_REV : NormativeDecision := {
  id := ⟨"DC-STGM-TRACE-2-REV"⟩
  date := 1737560000  -- 2025-01-23 approximate
  type := .DC
  decision := "SignalType as inductive type with standard cases and validated custom option"
  alternatives := [
    ("Keep as String", "creates type safety inconsistency with ID phantom types"),
    ("Pure enumeration", "limits extensibility for domain-specific types"),
    ("Type class", "overengineered for current needs"),
    ("Unvalidated custom", "allows invalid identifiers")
  ]
  rationale := [
    "Resolves tension with phantom type safety for IDs",
    "Provides type safety for common cases",
    "Maintains extensibility via custom with validation",
    "Smart constructor ensures valid custom type names",
    "Addresses correctness debt identified in review",
    "Cost is minimal, benefit is high consistency"
  ]
  dependencies := [⟨"DC-STGM-PRIM-3"⟩, ⟨"DC-STGM-TRACE-2"⟩]
  status := .Active
  context := some "Response to reviewer feedback about type safety inconsistency"
  supersededBy := none
}

/-- Minimal signal structure for MVP -/
def DC_STGM_TRACE_3 : NormativeDecision := {
  id := ⟨"DC-STGM-TRACE-3"⟩
  date := 1737500000
  type := .DC
  decision := "Signal structure contains only essential fields for stigmergic coordination"
  alternatives := [
    ("Include intensity field", "deferred - adds complexity to MVP"),
    ("Add decay parameters", "belongs in environment or as metadata"),
    ("Include visibility scope", "premature - can use metadata"),
    ("Add expiration time", "can compute from age and environment rules")
  ]
  rationale := [
    "MVP principle - start with minimal working system",
    "Every field has clear purpose and usage",
    "Can extend through metadata for special cases",
    "Intensity/decay deferred until proven necessary",
    "Simpler proofs and cleaner implementation"
  ]
  dependencies := [⟨"AD-STGM-PRIM-1"⟩, ⟨"DC-STGM-TRACE-1"⟩]
  status := .Active
  context := some "Removed intensity field after attempting complex decay proofs - not needed for MVP"
  supersededBy := none
}

/-- Invariants as documentation vs enforcement -/
def DC_STGM_TRACE_4 : NormativeDecision := {
  id := ⟨"DC-STGM-TRACE-4"⟩
  date := 1737500000
  type := .DC
  decision := "Document invariants that are enforced at environment level, not signal level"
  alternatives := [
    ("Smart constructor with proofs", "requires system time context"),
    ("Runtime validation", "not compile-time safe"),
    ("Ignore invariants", "loses important semantic information"),
    ("Dependent types for all invariants", "too complex for MVP")
  ]
  rationale := [
    "Some invariants require environmental context",
    "ID uniqueness is environment's responsibility",
    "Timestamp validation needs current system time",
    "Documentation preserves intent for implementers",
    "Clear documentation of enforcement level maintains transparency"
  ]
  dependencies := []
  status := .Active
  context := some "Updated after compliance audit: explicitly document WHERE invariants are enforced"
  supersededBy := none
}

/-- Properties focus on essential signal semantics -/
def OA_STGM_TRACE_1 : NormativeDecision := {
  id := ⟨"OA-STGM-TRACE-1"⟩
  date := 1737500000
  type := .OA
  decision := "Prove only essential properties about signals for MVP"
  alternatives := [
    ("Prove all conceivable properties", "diminishing returns on effort"),
    ("No proofs", "loses correctness guarantees"),
    ("Complex decay theorems", "not needed until decay is implemented"),
    ("Ordering properties", "not needed until search/filter implemented")
  ]
  rationale := [
    "Focus on properties that matter now",
    "Age properties essential for any time-based system",
    "Immutability properties prevent bugs",
    "Identity preservation ensures signal tracking",
    "Can add more theorems as features are added"
  ]
  dependencies := [⟨"OA-STGM-PRIM-2"⟩, ⟨"AD-STGM-PRIM-1"⟩]
  status := .Active
  context := some "This is why we proved age_monotonic but not complex decay properties"
  supersededBy := none
}

/-- Simple operations only -/
def AD_STGM_TRACE_1 : NormativeDecision := {
  id := ⟨"AD-STGM-TRACE-1"⟩
  date := 1737500000
  type := .AD
  decision := "Provide only essential operations: create, getAge, addMetadata"
  alternatives := [
    ("Full CRUD operations", "update/delete violate immutability"),
    ("Complex queries", "belongs in Environment module"),
    ("Decay operations", "deferred until intensity added"),
    ("Comparison operators", "not needed for MVP")
  ]
  rationale := [
    "Each operation has clear use case",
    "create: Make new signals",
    "getAge: Time-based filtering/decay",
    "addMetadata: Extensibility while preserving immutability",
    "Other operations belong in Environment or Agent modules"
  ]
  dependencies := [⟨"DC-STGM-TRACE-1"⟩, ⟨"DC-STGM-TRACE-3"⟩]
  status := .Active
  context := some "Removed applyDecay and isBelowThreshold operations after simplifying to MVP"
  supersededBy := none
}

/-- Age calculation as fundamental operation -/
def AD_STGM_TRACE_2 : NormativeDecision := {
  id := ⟨"AD-STGM-TRACE-2"⟩
  date := 1737500000
  type := .AD
  decision := "Age calculation is a fundamental signal operation, not derived"
  alternatives := [
    ("Let users compute age manually", "error-prone and repetitive"),
    ("Store age as field", "becomes stale, needs updating"),
    ("Age as environment query", "signals should know their own age"),
    ("No age concept", "essential for stigmergic decay")
  ]
  rationale := [
    "Age is universally needed for stigmergic systems",
    "Clean abstraction over Time.age function",
    "Enables time-based filtering and decay",
    "Simple operation with clear semantics",
    "Well-defined properties (monotonic, non-negative)"
  ]
  dependencies := [⟨"DC-STGM-PRIM-2"⟩]
  status := .Active
  context := some "Age is relative to 'now' parameter, not stored, ensuring freshness"
  supersededBy := none
}

/-- Metadata for extensibility -/
def AD_STGM_TRACE_3 : NormativeDecision := {
  id := ⟨"AD-STGM-TRACE-3"⟩
  date := 1737500000
  type := .AD
  decision := "Include metadata field for extensibility without modifying core structure"
  alternatives := [
    ("No extensibility", "too rigid for diverse domains"),
    ("Inheritance hierarchy", "complex and inflexible"),
    ("Generic type parameter", "complicates type signatures"),
    ("JSON field", "requires parsing and validation")
  ]
  rationale := [
    "Allows domain-specific information without core changes",
    "Simple key-value pairs are sufficient",
    "Preserves type safety of core fields",
    "addMetadata operation preserves immutability",
    "Can encode complex data as string values if needed"
  ]
  dependencies := [⟨"DC-STGM-PRIM-4"⟩, ⟨"DC-STGM-TRACE-1"⟩]
  status := .Active
  context := some "Metadata allows for future features like intensity, tags, etc. without breaking changes"
  supersededBy := none
}

/-- Preservation theorems for operations -/
def OA_STGM_TRACE_2 : NormativeDecision := {
  id := ⟨"OA-STGM-TRACE-2"⟩
  date := 1737550000  -- 2025-01-23 approximate
  type := .OA
  decision := "All operations must have preservation theorems proving field immutability"
  alternatives := [
    ("No preservation proofs", "allows hidden field mutations"),
    ("Documentation only", "not compiler-verified"),
    ("Implicit from implementation", "not explicit enough")
  ]
  rationale := [
    "Compliance requires preservation theorems for all operations",
    "Makes field preservation explicit and proven",
    "Prevents accidental field changes in future modifications",
    "Standard practice for verified specifications",
    "Added after compliance audit feedback"
  ]
  dependencies := [⟨"DC-STGM-TRACE-1"⟩, ⟨"OA-STGM-PRIM-2"⟩]
  status := .Active
  context := some "Added 5 preservation theorems for addMetadata operation after compliance review"
  supersededBy := none
}

/-- Collection of all signal decisions for easy access -/
def signalDecisions : List NormativeDecision := [
  DC_STGM_TRACE_1, DC_STGM_TRACE_2, DC_STGM_TRACE_2_REV, DC_STGM_TRACE_3, DC_STGM_TRACE_4,
  OA_STGM_TRACE_1, OA_STGM_TRACE_2,
  AD_STGM_TRACE_1, AD_STGM_TRACE_2, AD_STGM_TRACE_3
]

/-- Generate a decision log for the Signal module -/
def signalDecisionLog : String :=
  generateDecisionLog signalDecisions "Stigmergic Signal Module Normative Decisions"

end SignalDecisions

end Stigmergic.Foundation
