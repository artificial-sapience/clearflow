import Stigmergic.Meta.NormativeDecision

open Stigmergic.Meta

/-!
# Normative Decisions for Emergence Properties

This file documents design decisions made in Properties/Emergence.lean.

## Overview

Emergence properties capture how global coordination emerges from local interactions.
These are the defining characteristics of stigmergic systems.

-/

namespace Stigmergic

/-- Trivial equalities for semantic properties -/
def OA_STGM_019_TrivialEqualityProofs : NormativeDecision := {
  id := ⟨"OA_STGM_019"⟩
  date := 1737500000  -- 2025-01-22 approximate
  type := .OA
  decision := "State properties as x = x when the property is architectural"
  alternatives := [
    ("Complex proofs", "would prove tautologies with no semantic value"),
    ("No properties", "loses important architectural documentation"),
    ("Comments only", "properties wouldn't be type-checked")
  ]
  rationale := [
    "Many emergence properties are about system architecture (e.g., 'agents",
    "communicate indirectly') rather than provable theorems; trivial equalities",
    "document these properties without requiring complex proofs"
  ]
  dependencies := [⟨"DC_STGM_017"⟩]
  status := .Active
  context := some "Balances formal specification with practical documentation"
  supersededBy := none
}

/-- Focus on indirect communication -/
def DC_STGM_021_IndirectCommunicationFocus : NormativeDecision := {
  id := ⟨"DC_STGM_021"⟩
  date := 1737500000
  type := .DC
  decision := "Make indirect communication the primary emergence property"
  alternatives := [
    ("Direct communication", "would not be stigmergic"),
    ("Mixed communication", "loses theoretical clarity")
  ]
  rationale := [
    "Indirect communication through environmental modification is the",
    "defining characteristic of stigmergy, distinguishing it from direct",
    "message-passing systems"
  ]
  dependencies := []
  status := .Active
  context := some "Aligns with classical stigmergy literature"
  supersededBy := none
}

end Stigmergic