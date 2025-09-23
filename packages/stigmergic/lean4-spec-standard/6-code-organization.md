# 6. Code Organization

> Version: 0.1.0-draft
> Status: Section 1 Draft for Review
> Part of: Lean 4 Specification Standard

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section establishes patterns for organizing large formal specifications to ensure maintainability, clear dependencies, and systematic growth.

## 6.1 Layer Dependencies

**Requirement**: Code MUST be organized into strict dependency layers where each layer can only depend on layers below it.

**Rationale**: Layered architecture prevents circular dependencies, ensures modular reasoning, and enables independent evolution of components. Lower layers provide foundations that higher layers build upon.

**Standard Layer Hierarchy**:

```lean
/-
 Properties (Proofs about the system)
 ↑
 Meta (Reflection and meta-programming)
 ↑
 Network (Distributed operations)
 ↑
 Core (Domain objects)
 ↑
 Foundation (Mathematical primitives)
-/
```

**Example - Layer Organization**:

```lean
-- Foundation/Time.lean
import Mathlib.Data.Real.Basic

/-- Time as a non-negative real number -/
def Time := {t : ℝ // 0 ≤ t}

-- Core/Entity.lean
import .Foundation.Time -- Depends on Foundation layer

/-- Core domain object depending on Foundation -/
structure Entity where
 id : Id
 createdAt : Time -- Uses Foundation layer

-- Network/Consensus.lean
import .Core.Entity -- Depends on Core layer

/-- Network operation depending on Core -/
def consensusRequired (entities : List Entity) : Bool :=
 entities.length ≥ 3 -- Uses Core layer

-- Properties/Safety.lean
import .Network.Consensus -- Depends on Network layer

/-- Property about the system -/
theorem consensus_requires_multiple :
 ∀ es, consensusRequired es → es.length > 1 := by
 intro es h
 unfold consensusRequired at h
 linarith
```

## 6.2 Module Structure

**Requirement**: Each module MUST have a clear, single purpose and explicit dependencies.

**Module Organization Patterns**:

```text
/
├── Foundation/
│ ├── Time.lean -- Temporal primitives
│ ├── Space.lean -- Spatial primitives
│ ├── Algebra.lean -- Algebraic structures
│ ├── Primitives.lean -- Basic types
│ └── PrimitivesDecisions.lean -- Normative decisions for Primitives
├── Core/
│ ├── Entity.lean -- Basic entities
│ ├── EntityDecisions.lean -- Normative decisions for Entity
│ ├── Knowledge.lean -- Knowledge representation
│ ├── KnowledgeDecisions.lean -- Normative decisions for Knowledge
│ └── Resources.lean -- Resource management
├── Network/
│ ├── Consensus.lean -- Consensus mechanisms
│ ├── Communication.lean -- Message passing
│ └── Synchronization.lean -- Time sync
├── Meta/
│ ├── Decision.lean -- Normative decision framework
│ ├── AllDecisions.lean -- Decision aggregator (optional)
│ ├── Governance.lean -- Meta-governance
│ └── Evolution.lean -- System evolution
└── Properties/
 ├── Safety.lean -- Safety proofs
 ├── Liveness.lean -- Liveness proofs
 └── Fairness.lean -- Fairness proofs
```

**Decision File Pattern**: Each major module has an associated `*Decisions.lean` file that captures all normative (value-laden) choices as typed values. This co-locates decisions with the code they affect and enables version tracking, dependency analysis, and machine processing of design rationale.

**Import Discipline**:

```lean
-- Good: Minimal, explicit imports
import .Foundation.Time
import .Core.Entity
import Mathlib.Data.List.Basic

-- Bad: Wildcard imports
import .Core -- Imports everything!
import Mathlib -- Far too much!
```

**Linter Compliance**:

- **Requirement**: Linter checks MUST NOT be disabled. The use of `set_option` to suppress warnings (e.g., `set_option linter.minImports false`) is forbidden as is any other linter suppression.
- **Rationale**: Linters are a core part of our automated compliance verification. Disabling them introduces blind spots and undermines the goal of creating provably correct specifications. If a linter raises an issue, the code MUST be fixed to satisfy the check.

## 6.3 Naming Conventions

**Requirement**: Names MUST be consistent, descriptive, and follow Lean 4 conventions.

**Naming Patterns**:

```lean
-- Types: UpperCamelCase
structure ProposalVote where ...
inductive ConsentState where ...
class Measurable (α : Type) where ...

-- Functions/Values: lowerCamelCase
def calculateMetric : Entity → ℝ := ...
def minVotingThreshold : ℚ := 2/3

-- Theorems: snake_case describing the property
theorem vote_count_bounded : ...
theorem consensus_implies_quorum : ...

-- Type classes: Adjective form
class Decidable (p : Prop) where ...
class Measurable (α : Type) where ...

-- Namespaces: Match module structure
namespace .Core.Entity
 def update : Entity → Entity := ...
end .Core.Entity

-- Constants for system parameters: UPPER_SNAKE_CASE
abbrev MAX_PROPOSAL_SIZE : ℕ := 10000
abbrev DEFAULT_VOTING_WINDOW : Duration := ⟨259200⟩
```

## 6.4 Import Discipline

**Requirement**: Imports MUST be minimal, explicit, and organized.

**Import Organization**:

```lean
/-!
Import sections in order:
1. Mathlib imports (sorted alphabetically)
2. Project foundation imports
3. Project layer imports (by dependency)
4. Local module imports
-/

-- Example: Well-organized imports
import Mathlib.Algebra.Group.Defs
import Mathlib.Data.Real.Basic
import Mathlib.Order.Lattice

import .Foundation.Time
import .Foundation.Space

import .Core.Entity
import .Core.Knowledge

import .Network.Messages

-- Bad: Disorganized imports
import .Core.Entity
import Mathlib.Data.Real.Basic
import .Foundation.Time
import Mathlib.Algebra.Group.Defs
```

**Avoiding Import Cycles**:

```lean
-- Problem: Circular dependency
-- A.lean
import B
structure A where
 b : B

-- B.lean
import A -- Cycle!
structure B where
 a : A

-- Solution: Extract common interface
-- Common.lean
structure AInterface where ...
structure BInterface where ...

-- A.lean
import Common
structure A extends AInterface where
 b : BInterface

-- B.lean
import Common
structure B extends BInterface where
 a : AInterface
```

## 6.5 File Organization

**Requirement**: Each file MUST be focused on a single concept with related definitions grouped logically.

**File Structure Template**:

```lean
import Mathlib.Data.Real.Basic
import .Foundation.Time

/-!
# File Title

One-line description of file purpose.

## Main Results

- `mainDefinition` - What it defines
- `mainTheorem` - What it proves

## Implementation Notes

Any important implementation details.

## References

- [Ref2024] Academic reference
-/

namespace .Layer.Module

open OtherNamespace -- If needed

section Definitions
 -- Core type definitions
end Definitions

section Operations
 -- Functions operating on the types
end Operations

section Properties
 -- Theorems about the definitions
end Properties

end .Layer.Module
```

## 6.6 Visibility and Encapsulation

**Requirement**: Expose only what is necessary. Use visibility modifiers to enforce encapsulation.

**Visibility Patterns**:

```lean
namespace .Core

-- Private implementation detail: pure calculation
private def calculateWeight (e : Entity) : ℚ :=
 -- Complex internal logic that should not be exposed
 (e.reputation * e.stake) / 100

-- Public API: visible outside namespace
/-- Public function to get an entity's voting power -/
def votingPower (e : Entity) : ℚ :=
 let weight := calculateWeight e
 -- Additional public logic
 if e.isActive then weight else weight / 2

-- Protected pattern using sections
section InternalHelpers
 -- These are only for this file
 private def validateName (n : String) : Bool :=
 n.length > 0 ∧ n.all Char.isAlphanum
end InternalHelpers

-- Opaque types hide implementation
opaque ResourceImpl : Type := List Resource

-- Public interface to opaque type
def Resources := ResourceImpl

def Resources.empty : Resources :=
 cast (by rfl) []

end .Core
```

## Summary of Code Organization

These patterns ensure that:

- Dependencies form a clear hierarchy without cycles
- Modules have single, clear purposes
- Names are consistent and meaningful
- Imports are minimal and organized
- Implementation details are properly encapsulated

Good organization is not just about aesthetics - it's about creating specifications that can grow and evolve while maintaining mathematical rigor. This implements our core philosophy by making the structure itself a form of verification.
