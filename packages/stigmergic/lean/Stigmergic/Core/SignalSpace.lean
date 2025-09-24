import Stigmergic.Foundation.Primitives
import Stigmergic.Foundation.Signal

set_option linter.minImports false
set_option linter.upstreamableDecl false
set_option linter.ppRoundtrip false

/-!
# Stigmergic.Core.SignalSpace
The signal space is the shared environment where LLM agents emit and observe signals.

## Overview

Unlike a spatial environment, the signal space is a semantic space where:
- Signals are messages with content and type
- Agents query by semantic relevance, not distance
- Attraction is based on content matching, not proximity
- Coordination emerges from signal patterns, not spatial arrangement

## Main Definitions

- `SignalSpace` - Collection of signals with semantic operations
- `SignalSpace.empty` - Create an empty space
- `SignalSpace.emit` - Add a signal to the space
- `SignalSpace.queryByType` - Find signals by type
- `SignalSpace.queryRecent` - Get recent signals
- `SignalSpace.remove` - Remove consumed signal

## Implementation Notes

This module replaces the spatial Environment with a signal-driven
coordination space suitable for LLM agents. No spatial concepts,
no energy management, pure semantic coordination.

## Normative Decisions

See SignalSpaceDecisions.lean for design choices and alternatives considered.
-/

namespace Stigmergic

/-- Signal space maintains signals for semantic coordination.

 PURPOSE: Shared space for stigmergic coordination through signal emition.

 PRECONDITIONS: Created through SignalSpace.empty.

 POSTCONDITIONS: All operations maintain invariants.

 INVARIANTS:
 - All signal IDs are unique
 - All signal timestamps ≤ current space time
 - Signals are immutable once emited
 - No spatial indexing (semantic only) -/
structure SignalSpace where
  /-- Collection of signals indexed by ID -/
  signals : SignalId → Option Signal
  /-- Current space time for timestamp validation -/
  currentTime : Time
  /-- Total number of signals in space -/
  size : Nat
  /-- Proof that all stored signals have timestamps ≤ currentTime -/
  timeInvariant : ∀ id, ∀ signal, signals id = some signal → signal.timestamp ≤ currentTime
  /-- Proof that signals map correctly to their IDs -/
  idInvariant : ∀ id, ∀ signal, signals id = some signal → signal.id = id

section SpaceOperations

/-- Create an empty space.

 PURPOSE: Initialize a new space with no signals.

 PRECONDITIONS: None.

 POSTCONDITIONS: Returns empty space at given time.

 Mathematically: empty(t) = {signals: ∅, time: t, size: 0}

 In English: Creates a space with no signals at time t. -/
def SignalSpace.empty (now : Time) : SignalSpace where
  signals := fun _ => none
  currentTime := now
  size := 0
  timeInvariant := by
    intro id signal h
    simp at h  -- none ≠ some signal, vacuous
  idInvariant := by
    intro id signal h
    simp at h  -- none ≠ some signal, vacuous

/-- Result of emitting a signal to the space. -/
inductive EmitResult where
  /-- Successfully published the signal -/
  | success : SignalSpace → EmitResult
  /-- Failed due to duplicate ID -/
  | duplicateId : EmitResult
  /-- Failed due to future timestamp -/
  | futureTimestamp : EmitResult

/-- Publish a signal to the space.

 PURPOSE: Add a new signal for agents to observe.

 PRECONDITIONS:
 - signal.id must not already exist in space
 - signal.timestamp ≤ space.currentTime

 POSTCONDITIONS:
 - On success, returns updated space with signal
 - On failure, returns specific error reason

 Mathematically: emit(space, t) = space ∪ {t} if valid, error otherwise

 In English: Emits signal if ID is unique and timestamp is valid. -/
noncomputable def SignalSpace.emit (space : SignalSpace) (signal : Signal) : EmitResult :=
  open Classical in
  -- Check ID uniqueness
  match space.signals signal.id with
  | some _ => EmitResult.duplicateId
  | none =>
    -- Check timestamp validity
    if h : signal.timestamp ≤ space.currentTime then
      -- Create updated space
      let newSignals := fun id =>
        if id = signal.id then some signal else space.signals id

      EmitResult.success {
        signals := newSignals
        currentTime := space.currentTime
        size := space.size + 1
        timeInvariant := by
          intro id' signal' h'
          unfold newSignals at h'
          split_ifs at h' with h_eq
          · grind
          · exact space.timeInvariant id' signal' h'
        idInvariant := by
          intro id' signal' h'
          unfold newSignals at h'
          split_ifs at h' with h_eq
          · grind
          · exact space.idInvariant id' signal' h'
      }
    else
      EmitResult.futureTimestamp

/-- Query signals by type.

 PURPOSE: Find all signals matching a semantic type.

 PRECONDITIONS: None.

 POSTCONDITIONS: Returns list of matching signals.

 Mathematically: queryByType(space, type) = {t ∈ space | t.type = type}

 In English: Returns all signals with the specified type. -/
def SignalSpace.queryByType (_ : SignalSpace) (_ : SignalType) : List Signal :=
  -- In real implementation, would iterate through stored signals
  -- For MVP, return empty list as placeholder
  []

/-- Query recent signals.

 PURPOSE: Get the N most recent signals.

 PRECONDITIONS: None.

 POSTCONDITIONS: Returns up to N recent signals.

 Mathematically: queryRecent(space, n) = top_n(space, by: timestamp)

 In English: Returns the N most recently emited signals. -/
def SignalSpace.queryRecent (_ : SignalSpace) (_ : Nat) : List Signal :=
  -- Would return signals sorted by timestamp, limited to N
  []

/-- Query signals by content match.

 PURPOSE: Find signals with content matching a pattern.

 PRECONDITIONS: None.

 POSTCONDITIONS: Returns matching signals.

 NOTE: In production would use semantic similarity/embeddings.

 Mathematically: queryContent(space, pattern) = {t ∈ space | pattern ⊆ t.content}

 In English: Returns signals whose content contains the pattern. -/
def SignalSpace.queryContent (_ : SignalSpace) (_ : String) : List Signal :=
  -- Would perform semantic search on content
  []

/-- Get a signal by its ID.

 PURPOSE: Retrieve a specific signal from the space.

 PRECONDITIONS: None (returns Option).

 POSTCONDITIONS: Returns Some signal if ID exists, None otherwise.

 Mathematically: getById(space, id) = space.signals(id)

 In English: Looks up a signal by its unique identifier. -/
def SignalSpace.getById (space : SignalSpace) (id : SignalId) : Option Signal :=
  space.signals id

/-- Remove a consumed signal from the space.

 PURPOSE: Allow agents to consume signals.

 PRECONDITIONS: Signal with ID must exist.

 POSTCONDITIONS: Returns updated space without the signal.

 NOTE: Some systems might keep consumed signals with a flag instead.

 Mathematically: remove(space, id) = space \ {t | t.id = id}

 In English: Removes the signal with the given ID from the space. -/
noncomputable def SignalSpace.remove (space : SignalSpace) (id : SignalId) : SignalSpace :=
  open Classical in
  match h : space.signals id with
  | none => space  -- ID doesn't exist, no change
  | some _ =>
    { space with
      signals := fun tid => if tid = id then none else space.signals tid
      size := space.size - 1
      timeInvariant := by
        intro id' signal h'
        by_cases h_eq : id' = id
        · subst h_eq
          simp at h'
        · have h_neq : ¬(id' = id) := h_eq
          simp only [if_neg h_neq] at h'
          exact space.timeInvariant id' signal h'
      idInvariant := by
        intro id' signal h'
        by_cases h_eq : id' = id
        · subst h_eq
          simp at h'
        · have h_neq : ¬(id' = id) := h_eq
          simp only [if_neg h_neq] at h'
          exact space.idInvariant id' signal h'
    }

/-- Update space time.

 PURPOSE: Advance the space's current time.

 PRECONDITIONS: newTime ≥ space.currentTime (time doesn't go backwards).

 POSTCONDITIONS: Returns space with updated time.

 Mathematically: tick(space, t) = {signals: space.signals, time: t}

 In English: Updates the space's clock to a new time. -/
def SignalSpace.tick (space : SignalSpace) (newTime : Time)
    (h : space.currentTime ≤ newTime) : SignalSpace where
  signals := space.signals
  currentTime := newTime
  size := space.size
  timeInvariant := by
    intro id signal ht
    have old_inv := space.timeInvariant id signal ht
    exact le_trans old_inv h
  idInvariant := space.idInvariant

end SpaceOperations

section SpaceProperties

/-- Empty space has no signals.

 Mathematically: ∀id, empty(t).getById(id) = None

 In English: A newly created space contains no signals. -/
theorem empty_space_has_no_signals (now : Time) (id : SignalId) :
  (SignalSpace.empty now).getById id = none := by
  rfl

theorem emit_then_get (space : SignalSpace) (signal : Signal) (space' : SignalSpace)
    (h : space.emit signal = EmitResult.success space') :
  space'.getById signal.id = some signal := by
  simp only [SignalSpace.emit] at h
  split at h
  · contradiction
  · split_ifs at h
    · injection h with h'
      rw [← h']
      simp [SignalSpace.getById]

/-- Signal space size increases on successful emit.

 Mathematically: emit(space, t) = success(space') → space'.size = space.size + 1

 In English: Successfully emitting a signal increases the space size by one. -/
theorem emit_increases_size (space : SignalSpace) (signal : Signal) (space' : SignalSpace)
    (h : space.emit signal = EmitResult.success space') :
  space'.size = space.size + 1 := by
  unfold SignalSpace.emit at h
  grind

/-- Remove decreases size.

 Mathematically: t ∈ space → remove(space, t.id).size = space.size - 1

 In English: Removing an existing signal decreases space size by one. -/
theorem remove_decreases_size (space : SignalSpace) (id : SignalId) (signal : Signal)
    (h : space.getById id = some signal) :
  (space.remove id).size = space.size - 1 := by
  unfold SignalSpace.remove SignalSpace.getById at *
  grind


/-- Signal space time is monotonic.

 Mathematically: space.currentTime ≤ tick(space, t).currentTime

 In English: Signal space time never goes backwards. -/
theorem space_time_monotonic (space : SignalSpace) (newTime : Time)
    (h : space.currentTime ≤ newTime) :
  space.currentTime ≤ (space.tick newTime h).currentTime := by
  exact h

end SpaceProperties

end Stigmergic
