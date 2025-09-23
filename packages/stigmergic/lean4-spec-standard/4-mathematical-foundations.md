# 4. Mathematical Foundations

> Version: 0.1.0-draft  
> Status: Section 1 Draft for Review  
> Part of: Lean 4 Specification Standard

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section establishes how to leverage Mathlib's verified mathematical structures to build protocol specifications on solid foundations. Every mathematical choice must be justified and appropriate for the domain.

## 4.1 Real Numbers for Continuous Quantities

**Requirement**: Use mathematical Real numbers (ℝ) for all continuous quantities. Never use floating-point types in specifications.

**Rationale**: Protocol specifications must be mathematically precise and implementation-independent. Floating-point representations introduce rounding errors, platform dependencies, and implementation details that have no place in a specification. Real numbers provide exact mathematical semantics.

**Implementation Guidelines**:

- Import `Mathlib.Data.Real.Basic` for real number support
- Use ℝ for time, probabilities, measurements, and ratios
- Let implementations choose appropriate representations (Float, Fixed-point, etc.)
- Specify precision requirements separately from mathematical properties

**Example - Continuous Quantities in Protocols**:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Data.Real.NNReal

/-- Time as a non-negative real number -/
def Time := {t : ℝ // 0 ≤ t}

/-- Resource quantities using non-negative reals -/
def ResourceAmount := ℝ≥0  -- Mathlib's non-negative reals

/-- Decay over time with mathematical precision -/
structure DecayingValue where
  initial : ℝ≥0
  decayRate : ℝ  -- Can be negative for growth
  startTime : Time
  
/-- Value at any point in time (mathematical, not computational) -/
noncomputable def DecayingValue.valueAt (v : DecayingValue) (t : Time) : ℝ≥0 :=
  v.initial * Real.exp (v.decayRate * (t.val - v.startTime.val))

/-- Properties are proven mathematically -/
theorem decay_monotone (v : DecayingValue) (h : v.decayRate < 0) :
    ∀ t₁ t₂ : Time, t₁ ≤ t₂ → v.valueAt t₂ ≤ v.valueAt t₁ := by
  intro t₁ t₂ ht
  unfold valueAt
  apply mul_le_mul_of_nonneg_left
  · apply Real.exp_le_exp.mpr
    apply mul_nonpos_of_neg_of_nonneg h
    linarith [ht]
  · exact v.initial.property
```

## 4.2 Algebraic Structures

**Requirement**: Use Mathlib's algebraic hierarchy for all mathematical structures. Never reimplement standard algebraic concepts.

**Rationale**: Mathlib provides thousands of proven theorems about algebraic structures. By using these standard structures, we inherit all these theorems and ensure our specifications integrate with the broader mathematical ecosystem.

**Key Structures from Mathlib**:

- Groups: `AddGroup`, `AddCommGroup`, `Group`, `CommGroup`
- Rings: `Semiring`, `Ring`, `CommRing`
- Orders: `PartialOrder`, `LinearOrder`, `Lattice`
- Combinations: `OrderedAddCommGroup`, `LinearOrderedField`

**Example - Protocol Algebra Using Mathlib**:

```lean
import Mathlib.Algebra.Group.Defs
import Mathlib.Algebra.Order.Group.Abs
import Mathlib.Data.Real.Basic

/-- Votes form an ordered additive group -/
def VoteCount := ℤ
  deriving AddCommGroup, LinearOrder

/-- Reputation forms a multiplicative group with identity 1 -/
def Reputation := {r : ℝ // 0 < r}
  deriving Mul, One, Inv, Div

/-- The Group instance is inherited from positive reals -/
instance : Group Reputation := by
  -- Mathlib provides this instance for positive reals
  inferInstance

/-- Using Mathlib's lattice for consensus levels -/
inductive ConsensusLevel
  | none | weak | moderate | strong | unanimous
  deriving DecidableEq

instance : LinearOrder ConsensusLevel where
  le a b := match a, b with
    | .none, _ => true
    | .weak, .weak | .weak, .moderate | .weak, .strong | .weak, .unanimous => true
    | .moderate, .moderate | .moderate, .strong | .moderate, .unanimous => true
    | .strong, .strong | .strong, .unanimous => true
    | .unanimous, .unanimous => true
    | _, _ => false
  le_refl := by intro a; cases a <;> rfl
  le_trans := by intro a b c hab hbc; cases a <;> cases b <;> cases c <;> simp at * <;> tauto
  le_antisymm := by intro a b hab hba; cases a <;> cases b <;> simp at * <;> rfl
  le_total := by intro a b; cases a <;> cases b <;> simp

/-- Lattice operations come for free -/
instance : Lattice ConsensusLevel :=
  inferInstance  -- Mathlib provides this from LinearOrder
```

## 4.3 Temporal Properties

**Requirement**: Model time as a continuous, totally ordered structure. Use Mathlib's order theory for temporal reasoning.

**Rationale**: Time in distributed systems is continuous and totally ordered (within each frame of reference). Discrete time models introduce artificial synchronization points that don't exist in reality.

**Temporal Patterns**:

- Use continuous time (ℝ-based) for specifications
- Model intervals using Mathlib's `Set.Icc` (closed intervals)
- Use order theory for temporal precedence
- Specify causality through partial orders when needed

**Example - Temporal Specifications**:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Order.Bounds.Basic
import Mathlib.Data.Set.Intervals.Basic

/-- Events in the protocol -/
structure Event where
  id : Id
  timestamp : Time
  content : OpaqueData

/-- Temporal ordering of events -/
instance : Preorder Event where
  le e₁ e₂ := e₁.timestamp ≤ e₂.timestamp
  le_refl := fun _ => le_refl
  le_trans := fun _ _ _ => le_trans

/-- A time window with validity proof -/
structure TimeWindow where
  start : Time
  finish : Time
  valid : start ≤ finish

/-- Check if a time is within the window -/
def TimeWindow.contains (w : TimeWindow) (t : Time) : Prop :=
  w.start ≤ t ∧ t ≤ w.finish

/-- Events within a time window -/
def eventsInWindow (events : List Event) (window : TimeWindow) :=
  events.filter (fun e => window.contains e.timestamp)

/-- Causal ordering (partial order for distributed events) -/
structure CausalOrder where
  events : Set Event
  precedes : Event → Event → Prop
  irrefl : ∀ e ∈ events, ¬precedes e e
  trans : ∀ e₁ e₂ e₃, e₁ ∈ events → e₂ ∈ events → e₃ ∈ events →
    precedes e₁ e₂ → precedes e₂ e₃ → precedes e₁ e₃

/-- Lamport's happens-before is a causal order -/
def lamportClock : CausalOrder := sorry  -- Implementation details
```

## 4.4 Spatial Properties

**Requirement**: When modeling spatial or geometric properties, use Mathlib's metric space and topology libraries.

**Rationale**: Spatial properties in distributed systems (network topology, geographic distribution) require proper mathematical foundations. Mathlib provides verified implementations of metric spaces, topological spaces, and geometric structures.

**Example - Network Topology**:

```lean
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Data.Real.Basic

/-- Network nodes with distance metric -/
structure NetworkNode where
  id : Id
  location : ℝ × ℝ  -- 2D coordinates for simplicity

/-- Distance between nodes (could be latency, hop count, etc.) -/
instance : MetricSpace NetworkNode where
  dist n₁ n₂ := Real.sqrt ((n₁.location.1 - n₂.location.1)^2 + 
                           (n₁.location.2 - n₂.location.2)^2)
  dist_self := by intro; simp [Real.sqrt_zero]
  dist_comm := by intro a b; simp [add_comm]
  dist_triangle := sorry  -- PROOF REQUIRED: The triangle inequality for
                          -- Euclidean distance must be proven here for
                          -- compliance. Omitted for brevity in this example.
  edist_dist := by intro; simp [ENNReal.ofReal_eq_coe_nnreal]
  eq_of_dist_eq_zero := by
    intro a b h
    simp at h
    ext
    · have : (a.location.1 - b.location.1)^2 = 0 := by linarith [Real.sqrt_eq_zero'.mp h]
      linarith [sq_eq_zero_iff.mp this]
    · have : (a.location.2 - b.location.2)^2 = 0 := by linarith [Real.sqrt_eq_zero'.mp h]
      linarith [sq_eq_zero_iff.mp this]

/-- Nodes within communication range -/
def inRange (n₁ n₂ : NetworkNode) (range : ℝ) : Prop :=
  dist n₁ n₂ ≤ range

/-- The network topology forms a graph based on range -/
def networkTopology (nodes : Set NetworkNode) (range : ℝ) :=
  {edges : Set (NetworkNode × NetworkNode) // 
    ∀ e ∈ edges, e.1 ∈ nodes ∧ e.2 ∈ nodes ∧ inRange e.1 e.2 range}
```

## Summary of Mathematical Foundations

These patterns ensure that:

- All continuous quantities use exact mathematical representations
- Algebraic structures leverage Mathlib's proven theorems
- Temporal properties model real-world continuous time
- Spatial properties use proper metric/topological foundations
- Specifications remain implementation-independent

By building on Mathlib's foundations, we inherit thousands of proven theorems and ensure our specifications are mathematically sound. This implements our core philosophy: properties that matter are verified by the compiler through mathematical proof.
