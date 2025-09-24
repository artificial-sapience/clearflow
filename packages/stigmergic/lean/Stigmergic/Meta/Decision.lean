/-!
# Stigmergic.Meta.Decision

Normative decisions as first-class specification objects.

## Overview

This module defines normative decisions as data, not just documentation.
By treating decisions as Lean types, we can:
- Version and track decision evolution
- Generate documentation from code
- Ensure consistency between decisions
- Reference decisions in proofs and specifications

## Main Definitions

- `DecisionType` - Classification of decisions (DC, OA, AD, PD)
- `DecisionStatus` - Lifecycle status (Draft, Active, Superseded, Rejected)
- `NormativeDecision` - Complete decision with rationale and alternatives

## Implementation Notes

Decisions are living knowledge that evolve through use, maintain their
history, and can be reasoned about formally. The structure mirrors what
an agent proposal might contain in the running system.
-/

namespace Stigmergic.Meta

-- Basic types for self-containment (avoids circular imports)
/-- Unique identifier for decisions and other meta objects -/
structure Id where
  /-- The string value of the identifier -/
  value : String
  deriving Repr, BEq, DecidableEq

/-- Convert an Id to its string representation -/
def Id.toString (id : Id) : String := id.value

/-- Simplified time as natural numbers (epoch seconds) for meta tracking -/
abbrev Time := Nat

section DecisionTypes

/-- Type of normative decision in the specification.

 PURPOSE: Classify decisions for organization and signalability.

 INVARIANTS: Each type has specific documentation requirements. -/
inductive DecisionType where
  /-- Definitional Commitment: Core ontological choices -/
  | DC
  /-- Ontological Assumption: What exists in our model -/
  | OA
  /-- Architectural Decision: System design choices -/
  | AD
  /-- Process Decision: How we develop the specification -/
  | PD
  deriving Repr, BEq, DecidableEq

/-- Status of a decision in its lifecycle.

 PURPOSE: Track whether decisions are active or historical.

 INVARIANTS: Only Active decisions apply to current specification. -/
inductive DecisionStatus where
  /-- Under consideration -/
  | Draft
  /-- Currently in force -/
  | Active
  /-- Replaced by another decision -/
  | Superseded
  /-- Considered but not adopted -/
  | Rejected
  deriving Repr, BEq, DecidableEq

/-- A normative decision in the specification's development.

 PURPOSE: Capture the full context of a decision including
 alternatives and rationale.

 PRECONDITIONS: ID should be unique within the specification.

 POSTCONDITIONS: Provides signalable record of design choices.

 INVARIANTS: Superseded decisions must reference their replacement. -/
structure NormativeDecision where
  /-- Unique identifier (e.g., "DC-PRIM-1") -/
  id : Id

  /-- When this decision was made -/
  date : Time

  /-- Classification of the decision -/
  type : DecisionType

  /-- The actual decision statement -/
  decision : String

  /-- Alternative approaches considered (alternative, rejection reason) -/
  alternatives : List (String × String)

  /-- Why this decision was made (list of reasons) -/
  rationale : List String

  /-- Other decisions this depends on -/
  dependencies : List Id

  /-- Lifecycle status -/
  status : DecisionStatus

  /-- Additional context or philosophy -/
  context : Option String

  /-- If superseded, which decision replaces this -/
  supersededBy : Option Id
  deriving Repr

end DecisionTypes

section DecisionOperations

/-- Check if a decision is currently active -/
def NormativeDecision.isActive (d : NormativeDecision) : Bool :=
  d.status == DecisionStatus.Active

/-- Find all decisions that depend on a given decision -/
def findDependents (decisions : List NormativeDecision) (id : Id) : List NormativeDecision :=
  decisions.filter (fun d => d.dependencies.contains id)

/-- Convert a decision to human-readable markdown format -/
def NormativeDecision.toMarkdown (d : NormativeDecision) : String :=
  let typeStr := match d.type with
    | .DC => "DC (Definitional Commitment)"
    | .OA => "OA (Ontological Assumption)"
    | .AD => "AD (Architectural Decision)"
    | .PD => "PD (Process Decision)"

  let statusStr := match d.status with
    | .Draft => "DRAFT"
    | .Active => "ACTIVE"
    | .Superseded => "SUPERSEDED"
    | .Rejected => "REJECTED"

  let altStr := String.intercalate "\n" (d.alternatives.map (fun (alt, reason) =>
    s!"  - {alt} (rejected: {reason})"))

  let rationaleStr := String.intercalate "\n" (d.rationale.map (fun r =>
    s!"  - {r}"))

  let depStr := if d.dependencies.isEmpty then "None"
    else String.intercalate ", " (d.dependencies.map Id.toString)

  let contextStr := d.context.getD ""

  let supersededStr := match d.supersededBy with
    | some id => s!"\n- **Superseded By**: {id.toString}"
    | none => ""

  s!"### {d.id.toString}: {d.decision}

- **Date**: {d.date}
- **Type**: {typeStr}
- **Status**: {statusStr}
- **Decision**: {d.decision}
- **Alternatives**:
{altStr}
- **Rationale**:
{rationaleStr}
- **Dependencies**: {depStr}{supersededStr}
{if contextStr.isEmpty then "" else s!"- **Context**: {contextStr}"}
"

/-- Generate a markdown document from a list of decisions -/
def generateDecisionLog (decisions : List NormativeDecision) (title : String) : String :=
  let activeDecisions := decisions.filter (·.isActive)
  let historicalDecisions := decisions.filter (fun d => !d.isActive)

  s!"# {title}

## Active Decisions

{String.intercalate "\n" (activeDecisions.map (·.toMarkdown))}

## Historical Decisions

{if historicalDecisions.isEmpty then "None yet."
 else String.intercalate "\n" (historicalDecisions.map (·.toMarkdown))}
"

end DecisionOperations

end Stigmergic.Meta
