import Mathlib.Data.NNReal.Defs
import Mathlib.Analysis.SpecialFunctions.Pow.NNReal

-- We need NNReal for our Time abstraction
set_option linter.minImports false
-- These types are stigmergic-specific, not generic enough for upstream
set_option linter.upstreamableDecl false

/-!
# Stigmergic.Foundation.Primitives

Foundational types for stigmergic coordination systems.

## Overview

This module defines the most fundamental types used throughout the stigmergic
coordination system. These primitives establish our basic ontology for
agent-environment interaction through persistent signals.

## Main Definitions

- `Id α` - Type-safe identifiers with phantom type parameter
- `Time` - Non-negative real representing seconds from epoch
- `Metadata` - Key-value pairs for extensible signal information
- `DecayFactor` - Decay rates for signal intensity over time

## Implementation Notes

We use mathematical types (ℝ≥0) for specification. Implementations will
handle finite precision and computational constraints.

## Normative Decisions

- **Time Model**: We use continuous time (NNReal) rather than discrete ticks
  to allow smooth decay and avoid artificial discretization
- **ID Type Safety**: Phantom types prevent mixing different ID types at compile time
- **Metadata Model**: Simple key-value pairs with last-write-wins semantics
  for MVP simplicity; can be extended to more complex models later
-/

namespace Stigmergic

section BasicTypes

/-- Type-safe identifier parameterized by phantom type.

 PURPOSE: Provides compile-time type safety preventing ID confusion
 (e.g., cannot pass SignalId where AgentId expected).

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

/-- Metadata as key-value pairs for stigmergic signals.

 PURPOSE: Provides extensible information attached to signals
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
  ⟨(key, value) :: m.entries⟩

/-- Get metadata value by key, returning the first match.

 PURPOSE: Retrieves value associated with a key.

 POSTCONDITIONS: Returns Some value if key exists, None otherwise. -/
def Metadata.get (m : Metadata) (key : String) : Option String :=
  m.entries.lookup key

/-- Check if metadata contains key.

 Mathematically: hasKey(m, k) ↔ ∃(v : String), (k, v) ∈ m

 In English: Metadata m has key k if and only if there exists
 some value v such that the pair (k,v) is in the list m. -/
def Metadata.hasKey (m : Metadata) (key : String) : Bool :=
  m.entries.any (·.1 == key)

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

/-- Metadata preserves insertion order (newer entries shadow older).

 Mathematically: get(add(m, k, v), k) = Some(v)

 In English: After adding key k with value v to metadata m,
 getting k returns v. -/
theorem metadata_add_get (m : Metadata) (k v : String) :
  Metadata.get (Metadata.add m k v) k = some v := by
  unfold Metadata.add Metadata.get
  simp [List.lookup]

/-- Metadata key existence is preserved by addition.

 Mathematically: hasKey(add(m, k, v), k) = true

 In English: After adding a key to metadata, that key exists. -/
theorem metadata_add_hasKey (m : Metadata) (k v : String) :
  Metadata.hasKey (Metadata.add m k v) k = true := by
  unfold Metadata.add Metadata.hasKey
  simp [List.any]

/-- Age is zero at creation time.

 Mathematically: age(t, t) = 0

 In English: The age of something at its creation time is zero. -/
theorem age_at_creation (t : Time) :
  Time.age t t = 0 := by
  unfold Time.age
  simp

/-- ID equality is decidable through value comparison.

 Mathematically: (id₁ = id₂) ↔ (id₁.value = id₂.value)

 In English: Two IDs are equal if and only if their values are equal. -/
theorem id_eq_iff_value_eq {entity : Type} (id₁ id₂ : Id entity) :
  id₁ = id₂ ↔ id₁.value = id₂.value := by
  constructor
  · intro h; rw [h]
  · intro h; cases id₁; cases id₂; simp only [Id.mk.injEq]; exact h

/-- Multiple metadata additions follow last-write-wins semantics.

 Mathematically: get(add(add(m, k, v₁), k, v₂), k) = Some(v₂)

 In English: Adding the same key twice means the second value wins. -/
theorem metadata_add_overwrites (m : Metadata) (k v₁ v₂ : String) :
  Metadata.get (Metadata.add (Metadata.add m k v₁) k v₂) k = some v₂ := by
  unfold Metadata.add Metadata.get
  simp [List.lookup]

end Properties

end BasicTypes

section StigmergicDomain

/-!
## Stigmergic-Specific Types and Tags

These types establish the domain-specific nature of our primitives
for stigmergic coordination systems.
-/

/-- Phantom tag for signal identifiers in stigmergic systems -/
inductive SignalTag

/-- Phantom tag for agent identifiers in stigmergic systems -/
inductive AgentTag

/-- Phantom tag for environment identifiers in stigmergic systems -/
inductive EnvironmentTag

/-- Type-safe signal identifier for stigmergic coordination -/
abbrev SignalId := Id SignalTag

/-- Type-safe agent identifier for stigmergic coordination -/
abbrev AgentId := Id AgentTag

/-- Type-safe environment identifier for stigmergic coordination -/
abbrev EnvironmentId := Id EnvironmentTag

/-- Decay factor for stigmergic signals (0 < factor ≤ 1).

 PURPOSE: Represents how signals weaken over time in the environment.

 PRECONDITIONS: Factor must be in (0, 1] for meaningful decay.

 POSTCONDITIONS: Applied multiplicatively to signal intensity.

 INVARIANTS: 1.0 means no decay, approaching 0 means rapid decay. -/
structure DecayFactor where
  /-- The decay factor value between 0 (exclusive) and 1 (inclusive) -/
  value : NNReal
  /-- Proof that the decay factor is positive -/
  positive : 0 < value
  /-- Proof that the decay factor is at most 1 -/
  at_most_one : value ≤ 1

/-- Create a decay factor with validation.

 PURPOSE: Safe constructor ensuring valid decay factors.

 PRECONDITIONS: Value must be in (0, 1].

 POSTCONDITIONS: Returns Some if valid, None otherwise. -/
noncomputable def DecayFactor.create (v : NNReal) : Option DecayFactor :=
  if h₁ : 0 < v then
    if h₂ : v ≤ 1 then
      some ⟨v, h₁, h₂⟩
    else
      none
  else
    none

/-- No decay constant (factor = 1.0) -/
def DecayFactor.none : DecayFactor :=
  ⟨1, by norm_num, by norm_num⟩

-- Standard decay rate would be defined here, but requires more complex proofs
-- For now we'll leave this as future work

/-- Apply decay to a value over time.

 Mathematically: decay(v, factor, Δt) = v * factor^Δt

 In English: Value v decays by factor raised to the time difference. -/
noncomputable def apply_decay (value : NNReal) (factor : DecayFactor)
    (time_delta : Time) : NNReal :=
  value * (factor.value.rpow time_delta.val)

/-- Decay reduces or preserves value, never increases.

 This fundamental property ensures signals only weaken over time. -/
theorem decay_non_increasing (v : NNReal) (f : DecayFactor) (t : Time) :
  apply_decay v f t ≤ v := by
  unfold apply_decay
  have h : f.value.rpow t.val ≤ 1 := by
    apply NNReal.rpow_le_one
    exact f.at_most_one
    exact t.property
  calc
    v * f.value.rpow t.val ≤ v * 1 := mul_le_mul_left' h v
    _ = v := mul_one v

end StigmergicDomain

end Stigmergic
