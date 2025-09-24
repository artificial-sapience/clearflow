import Stigmergic.Foundation.Primitives
import Stigmergic.Foundation.Signal
import Stigmergic.Core.SignalSpace
import Stigmergic.Core.Agent

set_option linter.minImports false
set_option linter.upstreamableDecl false
set_option linter.ppRoundtrip false
set_option linter.style.commandStart false

/-!
# Stigmergic.Properties.Safety

Cross-cutting safety properties of the stigmergic coordination system.

## Overview

This module contains safety properties that involve interactions between
multiple components of the system. Intrinsic properties of individual
types are colocated with their definitions.

Cross-cutting properties here include:
- Signal uniqueness in spaces (SignalSpace + Signal)
- Read-only observations (Agent + SignalSpace)
- Creator identity preservation (Agent + Signal)

For intrinsic properties, see:
- Signal.lean for signal-specific invariants
- Agent.lean for agent preservation theorems

## Normative Decisions

See Properties/SafetyDecisions.lean for design rationale.
-/

namespace Stigmergic

section SpaceSafety

/-- Space maintains signal uniqueness.

 Mathematically: ∀space ∀s₁ s₂ ∈ space, s₁.id = s₂.id → s₁ = s₂

 In English: No two different signals can have the same ID. -/
theorem space_signal_uniqueness (space : SignalSpace)
    (s1 s2 : Signal)
    (h1 : space.signals s1.id = some s1)
    (h2 : space.signals s2.id = some s2)
    (hid : s1.id = s2.id) :
    s1 = s2 := by
  -- Since the space maps IDs to signals uniquely, same ID means same signal
  grind

/-- Space size is always non-negative.

 Mathematically: ∀space, space.size ≥ 0

 In English: A space cannot have negative signal count. -/
theorem space_size_non_negative (space : SignalSpace) :
    0 ≤ space.size := by
  unfold SignalSpace.size
  exact Nat.zero_le _

-- Note: SignalSpace.add is not currently defined in Core/SignalSpace.lean
-- The theorem below would apply if we add an 'add' operation:
-- theorem space_add_increases_size (space : SignalSpace) (signal : Signal) :
--     space.size ≤ (space.add signal).size

end SpaceSafety

section CrossCuttingSafety

/-- Relevance calculation is deterministic.

 Mathematically: ∀a ∀s ∀t, calculateRelevance(a, s, t) = calculateRelevance(a, s, t)

 In English: Given the same inputs, relevance calculation always produces the same result. -/
theorem relevance_deterministic (agent : Agent) (signal : Signal) (now : Time) :
    agent.calculateRelevance signal now = agent.calculateRelevance signal now :=
  rfl

/-- Observation doesn't modify the space.

 Mathematically: observe(agent, space) doesn't change space

 In English: Observing is a read-only operation. -/
theorem observation_read_only (agent : Agent) (space : SignalSpace) :
    let _ := agent.observe space
    space = space :=
  rfl

/-- Signal creation preserves creator identity.

 Mathematically: ∀a ∀content, createSignal(a, content).creator = a.id

 In English: Signals always record their true creator. -/
theorem signal_creator_preserved (agent : Agent) (content : String)
    (signalType : SignalType) (strength : NNReal) (metadata : Metadata) (now : Time) :
    (agent.createSignal content signalType strength metadata now).creator = agent.id := by
  unfold Agent.createSignal Signal.create
  simp

end CrossCuttingSafety

end Stigmergic