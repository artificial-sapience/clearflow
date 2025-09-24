import Stigmergic.Meta.NormativeDecision

open Stigmergic.Meta

/-!
# Normative Decisions for Safety Properties

This file documents design decisions made in Properties/Safety.lean.

## Overview

Safety properties ensure the system behaves predictably and within bounds.
These are essential properties, not optional design choices.

-/

namespace Stigmergic

/-- Focus on essential safety properties -/
def DC_STGM_017_EssentialSafetyOnly : NormativeDecision := {
  id := ⟨"DC_STGM_017"⟩
  date := 1737500000
  type := .DC
  decision := "Focus on fundamental safety properties, not implementation details"
  alternatives := [
    ("Prove all properties", "clutters spec with non-essential theorems"),
    ("No safety proofs", "loses important correctness guarantees")
  ]
  rationale := [
    "Properties like 'signals never have negative age' are fundamental",
    "properties like 'goals decay slower than tasks' are design choices"
  ]
  dependencies := [⟨"OA_STGM_015"⟩]
  status := .Active
  context := some "Distinguishes essential stigmergic properties from design choices"
  supersededBy := none
}

/-- SignalSpace.add not implemented -/
def AD_STGM_018_SpaceAddDeferred : NormativeDecision := {
  id := ⟨"AD_STGM_018"⟩
  date := 1737500000
  type := .AD
  decision := "Comment out space_add_increases_size theorem"
  alternatives := [
    ("Implement add", "requires significant SignalSpace refactoring"),
    ("Remove theorem", "loses documentation of expected property")
  ]
  rationale := [
    "SignalSpace currently uses functional representation without add operation",
    "adding would require refactoring to mutable or persistent data structure"
  ]
  dependencies := [⟨"AD_STGM_004"⟩]
  status := .Active
  context := some "Theorem documented but commented out for future implementation"
  supersededBy := none
}

end Stigmergic