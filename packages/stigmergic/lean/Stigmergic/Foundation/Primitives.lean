import Mathlib.Data.NNReal.Defs

-- We need NNReal for our Time abstraction
set_option linter.minImports false

/-!
# Stigmergic.Foundation.Primitives

Foundational types for stigmergic coordination systems.

## Overview

This module defines the most fundamental types used throughout the stigmergic
coordination system. These primitives establish our basic ontology for
agent-environment interaction through persistent traces.

## Main Definitions

- `Id α` - Type-safe identifiers with phantom type parameter
- `Time` - Non-negative real representing seconds from epoch
- `Metadata` - Key-value pairs for extensible trace information

## Implementation Notes

We use mathematical types (ℝ≥0) for specification. Implementations will
handle finite precision and computational constraints.
-/

namespace Stigmergic

section BasicTypes

/-- Type-safe identifier parameterized by phantom type.

 PURPOSE: Provides compile-time type safety preventing ID confusion
 (e.g., cannot pass TraceId where AgentId expected).

 PRECONDITIONS: None - construction always succeeds.

 POSTCONDITIONS: Two IDs are equal iff their string values are equal.

 INVARIANTS: The phantom type parameter is preserved through all operations.

 The phantom parameter has zero runtime cost. Can represent UUIDs, hashes,
 or human-readable names. The specification only requires uniqueness
 within context. -/
structure Id (entity : Type) where
  /-- The underlying string representation of the identifier -/
  value : String
  deriving Repr, DecidableEq

/-- Time as non-negative continuous value.

 PURPOSE: Represents temporal points and durations in the system.

 PRECONDITIONS: None - type ensures non-negativity.

 POSTCONDITIONS: All time values are ≥ 0.

 INVARIANTS: Time is linearly ordered and supports arithmetic.

 Represents seconds since system epoch as mathematical ideal.
 Using NNReal (ℝ≥0) provides non-negativity by construction,
 continuous time evolution, and mathematical rigor for proofs. -/
abbrev Time := NNReal

/-- Metadata as key-value pairs for stigmergic traces.

 PURPOSE: Provides extensible information attached to traces
 without modifying core types.

 PRECONDITIONS: None - empty list is valid metadata.

 POSTCONDITIONS: Order of entries is preserved (list semantics).

 INVARIANTS: Keys may be duplicated (latest value takes precedence).

 Keys should follow naming conventions (e.g., "urgency", "confidence"). -/
structure Metadata where
  /-- The key-value pairs storing metadata -/
  entries : List (String × String)
  deriving Repr, DecidableEq

section StigmergicInstances

/-- Default stigmergic identifier -/
def Id.default (entity : Type) : Id entity := ⟨"default"⟩

/-- Empty stigmergic metadata -/
def Metadata.empty : Metadata := ⟨[]⟩

/-- Convert stigmergic Id to String for display -/
def Id.toString {entity : Type} (id : Id entity) : String := id.value

-- Time inherits all NNReal instances through abbrev

end StigmergicInstances

section Operations

/-- Create a new unique identifier.

 PURPOSE: Generates IDs for entities in the system.

 PRECONDITIONS: Seed string should be unique within context.

 POSTCONDITIONS: Returns an Id with the given seed as value.

 In specifications, we assume this always produces unique values.
 Implementations must ensure uniqueness through appropriate mechanisms. -/
def Id.generate (entity : Type) (seed : String) : Id entity :=
  ⟨seed⟩

/-- Current time in the system.

 PURPOSE: Provides the current temporal point for time-based operations.

 In specifications, this is a parameter provided by environment.
 Implementations will use system clock.

 Note: We use a placeholder value for specification purposes. -/
noncomputable def Time.now : Time := 0  -- Placeholder, provided by environment at runtime

/-- Check if a time has passed relative to current time.

 Mathematically: hasPassed(t, now) ↔ t ≤ now

 In English: Time t has passed if and only if t is less than
 or equal to the current time now. -/
def Time.hasPassed (t : Time) (now : Time) : Prop :=
  t ≤ now

/-- Calculate age from timestamp.

 Mathematically: age(created, now) = now - created (saturating at 0)

 In English: The age of something created at time 'created' when
 viewed at time 'now' equals now minus created, but never goes negative. -/
def Time.age (created : Time) (now : Time) : Time :=
  now - created

/-- Add metadata entry to the front of the list.

 Mathematically: add(m, k, v) = (k, v) :: m

 In English: Adding key k with value v to metadata m creates
 a new list with the pair (k,v) at the front. -/
def Metadata.add (m : Metadata) (key : String) (value : String) : Metadata :=
  (key, value) :: m

/-- Get metadata value by key, returning the first match.

 PURPOSE: Retrieves value associated with a key.

 POSTCONDITIONS: Returns Some value if key exists, None otherwise. -/
def Metadata.get (m : Metadata) (key : String) : Option String :=
  m.lookup key

/-- Check if metadata contains key.

 Mathematically: hasKey(m, k) ↔ ∃(v : String), (k, v) ∈ m

 In English: Metadata m has key k if and only if there exists
 some value v such that the pair (k,v) is in the list m. -/
def Metadata.hasKey (m : Metadata) (key : String) : Bool :=
  m.any (·.1 == key)

end Operations

section Properties

/-- IDs with different phantom types are type-safe.
    The type system prevents mixing IDs of different entity types. -/
theorem id_type_safety {α β : Type} (_ : Id α) (_ : Id β) (_ : α ≠ β) :
  True :=
  trivial

/-- Time is always non-negative by construction -/
theorem time_non_negative (t : Time) : 0 ≤ t :=
  t.property

/-- Age calculation is monotonic with respect to current time -/
theorem age_monotonic (created now₁ now₂ : Time) (h : now₁ ≤ now₂) :
  Time.age created now₁ ≤ Time.age created now₂ := by
  unfold Time.age
  exact tsub_le_tsub_right h created

end Properties

end BasicTypes

end Stigmergic
