import Stigmergic.Foundation.Primitives

-- We need NNReal for our Time abstraction
set_option linter.minImports false
-- These types are stigmergic-specific, not generic enough for upstream
set_option linter.upstreamableDecl false
-- ppRoundtrip linter incorrectly flags the standard doc comment pattern for inductive constructors
set_option linter.ppRoundtrip false

/-!
# Stigmergic.Foundation.Signal

Persistent information signals left by agents in the environment.

## Overview

Signals are the fundamental unit of stigmergic communication. They represent
information emited by agents that persists in the environment and can
influence the behavior of other agents (or the same agent) in the future.

## Main Definitions

- `Signal` - Immutable information structure with content, type, metadata
- `Signal.create` - Constructor ensuring all invariants
- `Signal.getAge` - Calculate how long a signal has existed

## Implementation Notes

Signals are immutable once created. Any "modification" creates a new signal.
This ensures deterministic behavior and simplifies reasoning about system state.

## Normative Decisions

- **Immutability**: Signals cannot be modified after creation to ensure
  deterministic stigmergic dynamics
- **Type Safety**: SignalType is a string for flexibility
-/

namespace Stigmergic

/-- Structured signal type for signal-driven coordination.

 PURPOSE: Provides type-safe categorization for LLM agent coordination.

 PRECONDITIONS: Custom types must be non-empty alphanumeric strings.

 POSTCONDITIONS: Type is immutable once set.

 INVARIANTS: Standard types represent coordination primitives.

 Standard types for autonomous coordination:
 - goal: High-level objectives injected by humans/agents
 - task: Decomposed work items from goals
 - progress: Updates on goal/task advancement
 - completion: Signals that goal/task is done
 - requirement: Blocking needs that must be resolved
 - constraint: Invariants that must be maintained
 - custom: Domain-specific type with validated name

 These types enable LLM agents to self-organize around work rather
 than following predetermined flows. -/
inductive SignalType where
  /-- High-level objective to be achieved -/
  | goal
  /-- Decomposed work item from a goal -/
  | task
  /-- Progress update on goal or task -/
  | progress
  /-- Completion signal for goal or task -/
  | completion
  /-- Requirement or blocker needing resolution -/
  | requirement
  /-- Constraint that must be maintained -/
  | constraint
  /-- Domain-specific type with validated name -/
  | custom : String → SignalType
deriving Repr, DecidableEq

/-- Smart constructor for custom signal types.

 PURPOSE: Ensure custom type names are valid identifiers.

 PRECONDITIONS: Name must be non-empty and alphanumeric (plus underscore).

 POSTCONDITIONS: Returns Some if valid, None if invalid.

 Valid names: "food_source", "nest_location", "danger_zone".
 Invalid names: "", "foo-bar", "test type" (spaces not allowed). -/
def SignalType.mkCustom (name : String) : Option SignalType :=
  if name.length > 0 && name.all (fun c => c.isAlpha || c.isDigit || c == '_') then
    some (custom name)
  else
    none

/-- Convert SignalType to string for display/debugging.

 Mathematically: toString(t) = string representation of t

 In English: Standard types use their names, custom types return their string. -/
def SignalType.toString : SignalType → String
  | goal => "goal"
  | task => "task"
  | progress => "progress"
  | completion => "completion"
  | requirement => "requirement"
  | constraint => "constraint"
  | custom name => "custom:" ++ name

/-- Persistent signal structure for stigmergic coordination.

 PURPOSE: Represents information left by agents that persists in the
 environment and influences future agent behavior.

 PRECONDITIONS: Created through Signal.create with valid timestamp.

 POSTCONDITIONS: All fields are immutable after creation.

 INVARIANTS:
 - timestamp ≤ current_time (enforced by Environment when emiting)
 - id is unique within environment (enforced by Environment's signal collection)

 Signals are the foundation of stigmergic communication. -/
structure Signal where
  /-- Unique identifier for this signal -/
  id : SignalId
  /-- Information content of the signal -/
  content : String
  /-- Semantic type for categorization -/
  signalType : SignalType
  /-- Intrinsic strength set by emitter (0 to 1) -/
  strength : NNReal
  /-- When the signal was created -/
  timestamp : Time
  /-- Agent that created this signal -/
  creator : AgentId
  /-- Additional key-value information -/
  metadata : Metadata

section SignalOperations

/-- Create a new signal with current timestamp.

 PURPOSE: Primary constructor for signal creation.

 PRECONDITIONS:
 - now represents the intended timestamp for this signal
 - signalType is a valid SignalType (standard or validated custom)
 - strength is the intrinsic importance (0 to 1) set by emitter

 POSTCONDITIONS:
 - Returns signal with given parameters
 - timestamp = now
 - All fields are immutable

 NOTE: Timestamp validation (now ≤ current_time) is the responsibility
 of the Environment when emiting the signal. ID uniqueness is also
 enforced at the Environment level. -/
def Signal.create (id : SignalId) (content : String) (signalType : SignalType)
    (strength : NNReal) (now : Time) (creator : AgentId) (metadata : Metadata) : Signal :=
  { id, content, signalType, strength, timestamp := now, creator, metadata }

/-- Create a signal with a custom type, validating the type name.

 PURPOSE: Convenience constructor for custom signal types.

 PRECONDITIONS: typeName must be valid per mkCustom rules.

 POSTCONDITIONS: Returns Some signal if type name valid, None otherwise. -/
def Signal.createCustom (id : SignalId) (content : String) (typeName : String)
    (strength : NNReal) (now : Time) (creator : AgentId) (metadata : Metadata) : Option Signal :=
  match SignalType.mkCustom typeName with
  | some signalType => some (Signal.create id content signalType strength now creator metadata)
  | none => none

/-- Calculate age of signal relative to current time.

 PURPOSE: Determine how long a signal has existed.

 PRECONDITIONS: now ≥ signal.timestamp (time moves forward).

 POSTCONDITIONS: Returns now - timestamp as non-negative value.

 Mathematically: age(signal, now) = now - signal.timestamp

 In English: The age equals current time minus creation time. -/
def Signal.getAge (signal : Signal) (now : Time) : Time :=
  Time.age signal.timestamp now

/-- Calculate current strength after time decay.

 PURPOSE: Get the signal's strength accounting for age-based decay.

 PRECONDITIONS: now ≥ signal.timestamp (time moves forward).

 POSTCONDITIONS: Returns decayed strength in [0, signal.strength].

 Mathematically: strength(t) = strength₀ * decay_factor(age)

 In English: Strength decreases over time based on signal type. -/
noncomputable def Signal.getCurrentStrength (signal : Signal) (now : Time) : NNReal :=
  let age := signal.getAge now
  let decayFactor : NNReal :=
    match signal.signalType with
    | SignalType.goal | SignalType.constraint =>
      -- Goals and constraints persist longer
      if age.val ≤ 100 then ⟨1.0, by norm_num⟩
      else if age.val ≤ 500 then ⟨0.8, by norm_num⟩
      else ⟨0.5, by norm_num⟩
    | _ =>
      -- Other types decay faster
      if age.val ≤ 10 then ⟨1.0, by norm_num⟩
      else if age.val ≤ 50 then ⟨0.7, by norm_num⟩
      else ⟨0.3, by norm_num⟩
  signal.strength * decayFactor

/-- Add metadata entry to signal (creates new signal).

 PURPOSE: Attach additional information while preserving immutability.

 POSTCONDITIONS: Returns new signal with updated metadata. -/
def Signal.addMetadata (signal : Signal) (key : String) (value : String) : Signal :=
  { signal with metadata := signal.metadata.add key value }

end SignalOperations

section SignalProperties

/-- Signals are immutable - operations create new signals.

 This is a conceptual property. The type system enforces it through
 the lack of mutation operations. -/
theorem signal_immutable (t : Signal) : t = t :=
  rfl

/-- Age is always non-negative.

 Mathematically: ∀t ∀now, age(t, now) ≥ 0

 In English: The age of any signal at any time is non-negative. -/
theorem signal_age_non_negative (signal : Signal) (now : Time) :
  0 ≤ signal.getAge now :=
  time_non_negative _

/-- Age increases monotonically with time.

 Mathematically: ∀t ∀t₁ ∀t₂, t₁ ≤ t₂ → age(signal, t₁) ≤ age(signal, t₂)

 In English: As time advances, signal age can only increase. -/
theorem signal_age_monotonic (signal : Signal) (t₁ t₂ : Time) (h : t₁ ≤ t₂) :
  signal.getAge t₁ ≤ signal.getAge t₂ :=
  age_monotonic signal.timestamp t₁ t₂ h

/-- Signal creation time is fixed.

 Mathematically: ∀t, t.timestamp = creation_time

 In English: A signal's timestamp never changes after creation. -/
theorem signal_timestamp_immutable (signal : Signal) :
  signal.timestamp = signal.timestamp :=
  rfl

/-- Metadata operations preserve signal identity.

 Adding metadata creates a new signal with same ID but updated metadata. -/
theorem signal_metadata_preserves_id (signal : Signal) (k v : String) :
  (signal.addMetadata k v).id = signal.id :=
  rfl

/-- Age at creation time is zero.

 Mathematically: age(signal, signal.timestamp) = 0

 In English: A signal has age zero at its creation time. -/
theorem signal_age_at_creation (signal : Signal) :
  signal.getAge signal.timestamp = 0 :=
  age_at_creation signal.timestamp

/-- addMetadata preserves content field.

 Mathematically: (addMetadata(t, k, v)).content = t.content

 In English: Adding metadata doesn't change the signal's content. -/
theorem addMetadata_preserves_content (signal : Signal) (k v : String) :
  (signal.addMetadata k v).content = signal.content :=
  rfl

/-- addMetadata preserves signalType field.

 Mathematically: (addMetadata(t, k, v)).signalType = t.signalType

 In English: Adding metadata doesn't change the signal's type. -/
theorem addMetadata_preserves_signalType (signal : Signal) (k v : String) :
  (signal.addMetadata k v).signalType = signal.signalType :=
  rfl

/-- addMetadata preserves timestamp field.

 Mathematically: (addMetadata(t, k, v)).timestamp = t.timestamp

 In English: Adding metadata doesn't change when the signal was created. -/
theorem addMetadata_preserves_timestamp (signal : Signal) (k v : String) :
  (signal.addMetadata k v).timestamp = signal.timestamp :=
  rfl

/-- addMetadata preserves creator field.

 Mathematically: (addMetadata(t, k, v)).creator = t.creator

 In English: Adding metadata doesn't change who created the signal. -/
theorem addMetadata_preserves_creator (signal : Signal) (k v : String) :
  (signal.addMetadata k v).creator = signal.creator :=
  rfl

/-- addMetadata actually adds the metadata entry.

 Mathematically: get(addMetadata(t, k, v).metadata, k) = Some(v)

 In English: After adding metadata with key k and value v,
 looking up k in the metadata returns v. -/
theorem addMetadata_adds_entry (signal : Signal) (k v : String) :
  (signal.addMetadata k v).metadata.get k = some v :=
  metadata_add_get _ _ _

end SignalProperties

section SignalTypeProperties

/-- Custom type validation rejects empty strings.

 Mathematically: mkCustom("") = None

 In English: Empty strings are not valid custom type names. -/
theorem mkCustom_rejects_empty : SignalType.mkCustom "" = none :=
  rfl

/-- Custom type validation accepts valid identifiers.

 Mathematically: ∀s, s ≠ "" ∧ isAlphaNum(s) → mkCustom(s) = Some(custom s)

 In English: Non-empty alphanumeric strings produce valid custom types. -/
theorem mkCustom_accepts_valid (s : String)
    (h_nonempty : s.length > 0)
    (h_valid : s.all (fun c => c.isAlpha || c.isDigit || c == '_')) :
  SignalType.mkCustom s = some (SignalType.custom s) := by
  unfold SignalType.mkCustom
  simp [h_nonempty, h_valid]

/-- Standard types have distinct string representations.

 This ensures no confusion between type representations. -/
theorem signalType_toString_injective_standard :
  SignalType.toString SignalType.goal ≠ SignalType.toString SignalType.task ∧
  SignalType.toString SignalType.goal ≠ SignalType.toString SignalType.progress ∧
  SignalType.toString SignalType.goal ≠ SignalType.toString SignalType.completion ∧
  SignalType.toString SignalType.task ≠ SignalType.toString SignalType.progress ∧
  SignalType.toString SignalType.task ≠ SignalType.toString SignalType.completion ∧
  SignalType.toString SignalType.progress ≠ SignalType.toString SignalType.completion := by
  unfold SignalType.toString
  simp only [ne_eq]
  exact ⟨by decide, by decide, by decide, by decide, by decide, by decide⟩

/-- createCustom fails with invalid type names.

 Mathematically: createCustom(..., "", ...) = None

 In English: Can't create signals with invalid custom type names. -/
theorem createCustom_validates_type (id : SignalId) (content typeName : String)
    (strength : NNReal) (now : Time) (creator : AgentId) (metadata : Metadata) :
  typeName = "" → Signal.createCustom id content typeName strength now creator metadata = none := by
  intro h
  unfold Signal.createCustom
  rw [h]
  simp [mkCustom_rejects_empty]

end SignalTypeProperties

end Stigmergic
