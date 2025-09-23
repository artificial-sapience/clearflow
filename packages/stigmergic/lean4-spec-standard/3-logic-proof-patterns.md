# 3. Logic and Proof Patterns

> Version: 0.1.0-draft  
> Status: Section 1 Draft for Review  
> Part of: Lean 4 Specification Standard

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section establishes patterns and requirements for proofs that ensure every property is verified, not merely asserted. These patterns implement the Theorem-Driven Development principle from Section 1.

## 3.1 What Must Be Proven

**Requirement**: Every claim about protocol behavior MUST be accompanied by a machine-checkable proof.

**Categories of Required Proofs**:

1. **Invariant Preservation**: Functions that operate on constrained types must prove they maintain invariants
2. **Totality**: All functions must handle all possible inputs (no partial functions without explicit domains)
3. **Termination**: Recursive functions must prove they terminate
4. **Composition Properties**: Prove that composing protocol operations maintains safety properties
5. **Impossibility Results**: Prove that certain bad states cannot be reached

**Example - Comprehensive Proof Requirements**:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic

/-- A protocol state that must maintain invariants -/
structure ProtocolState where
  participants : ℕ
  activeProposals : ℕ
  -- Invariant: can't have more proposals than participants
  inv : activeProposals ≤ participants

/-- Adding a participant maintains the invariant -/
theorem addParticipant_preserves_inv (s : ProtocolState) :
    let s' : ProtocolState := {
      participants := s.participants + 1,
      activeProposals := s.activeProposals,
      inv := by
        -- Proof that invariant is maintained
        have h := s.inv
        linarith
    }
    s'.activeProposals ≤ s'.participants := by
  -- Proof is immediate from construction
  exact s'.inv

/-- Composition preserves invariants -/
theorem compose_preserves_safety 
    (f g : ProtocolState → ProtocolState)
    (hf : ∀ s, (f s).activeProposals ≤ (f s).participants)
    (hg : ∀ s, (g s).activeProposals ≤ (g s).participants) :
    ∀ s, ((f ∘ g) s).activeProposals ≤ ((f ∘ g) s).participants := by
  intro s
  exact hf (g s)

/-- Prove certain states are impossible -/
theorem no_negative_participants : ¬∃ (s : ProtocolState), s.participants = 0 ∧ s.activeProposals > 0 := by
  intro ⟨s, hp, ha⟩
  have : s.activeProposals ≤ s.participants := s.inv
  rw [hp] at this
  linarith
```

## 3.2 Proof Patterns

**Pattern**: Structure proofs to be both correct and comprehensible, following established patterns for common proof obligations.

**Core Patterns**:

1. **Totality and Termination by Construction**: Ensure all functions terminate
2. **Property-Based Testing as Proof Discovery**: Use testing to find counterexamples before proving
3. **Typeclasses for Lawful Abstractions**: Generic interfaces with proven laws
4. **Decidability for Computable Predicates**: Bridge logic and computation

### 3.2.1 Totality and Termination by Construction

**Rationale**: Non-terminating functions are not just theoretical concerns—they represent critical vulnerabilities. In a distributed protocol, non-terminating functions can be triggered by malicious inputs, leading to denial-of-service attacks that consume infinite computational resources. Proving termination for all functions is therefore a fundamental security requirement.

**Example - Termination Patterns**:

```lean
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

/-- Structural recursion: automatically terminating -/
def sum : List ℕ → ℕ
  | [] => 0
  | x :: xs => x + sum xs  -- Lean proves termination automatically

/-- Well-founded recursion: manual termination proof -/
def ackermann : ℕ → ℕ → ℕ
  | 0, n => n + 1
  | m + 1, 0 => ackermann m 1
  | m + 1, n + 1 => ackermann m (ackermann (m + 1) n)
  termination_by m n => (m, n)  -- Lexicographic ordering

/-- Partial functions must be explicit about their domain -/
def safeDiv (a b : ℕ) (h : b ≠ 0) : ℕ := a / b

-- This would be rejected: partial function without domain restriction
-- def unsafeDiv (a b : ℕ) : ℕ := a / b  -- What if b = 0?
```

### 3.2.2 Property-Based Testing as Proof Discovery

**Rationale**: Before investing effort in a formal proof, use Lean's property testing to quickly discover counterexamples. This pattern shows how testing guides us to correct theorems.

**Example - Discovery Through Testing**:

```lean
import Mathlib.Data.List.Basic
import Plausible  -- For QuickCheck-style testing

-- Step 1: Hypothesis (incorrect)
#test_impl reverse_append_wrong :=
  ∀ (l₁ l₂ : List ℕ), (l₁ ++ l₂).reverse = l₁.reverse ++ l₂.reverse

-- Step 2: Testing finds counterexample
-- Result: Found counterexample!
-- l₁ = [1], l₂ = [2]
-- LHS: [2, 1], RHS: [1, 2] ✗

-- Step 3: Corrected theorem
theorem reverse_append_correct (l₁ l₂ : List ℕ) :
    (l₁ ++ l₂).reverse = l₂.reverse ++ l₁.reverse := by
  induction l₁ with
  | nil => simp
  | cons x xs ih => simp [ih]

-- Step 4: Test the corrected version
#test_impl reverse_append_correct_test :=
  ∀ (l₁ l₂ : List ℕ), (l₁ ++ l₂).reverse = l₂.reverse ++ l₁.reverse
-- Result: Passed 100 tests ✓
```

### 3.2.3 Typeclasses for Lawful Abstractions

**Rationale**: Typeclasses encode mathematical structures with their laws. Every instance is a binding contract requiring proofs of all laws.

**CRITICAL REQUIREMENT**: Laws MUST be fields in the typeclass that require proofs. Laws in documentation comments are NOT enforced by the compiler and are therefore useless for ensuring correctness.

**Implementation Note**: For each concrete type that implements the typeclass, provide an instance declaration. This declaration is a formal claim that your type satisfies the class's contract. You MUST provide proofs for every law defined in the class as part of the instance definition. An instance with a missing or `sorry`'d proof for a law is a critical violation of the standard.

**Example - Common Violation vs Correct Implementation**:

```lean
-- ❌ CRITICAL VIOLATION: Laws only in documentation
class BadFlourishing (α : Type) where
  enhance : α → α → α
  measure : α → ℝ
  /-- Law: enhance is associative -/
  /-- Law: measure is monotone -/
  -- These "laws" are just comments! Any instance can violate them!

-- This violating instance compiles fine:
instance : BadFlourishing ℝ where
  enhance := (· - ·)  -- Not associative!
  measure := (fun x => -x)  -- Not monotone!
  -- No compiler error because laws aren't enforced

-- ✅ CORRECT: Laws as proof-requiring fields
class Flourishable (α : Type) extends LE α where
  enhance : α → α → α
  measure : α → ℝ
  -- Laws that MUST be proven for every instance
  enhance_assoc : ∀ a b c, enhance (enhance a b) c = enhance a (enhance b c)
  measure_monotone : ∀ a b, a ≤ b → measure a ≤ measure b

-- Now violations are impossible - this won't compile:
-- instance : Flourishable ℝ where
--   enhance := (· - ·)
--   measure := (fun x => -x)
--   enhance_assoc := sorry  -- MUST provide actual proof!
--   measure_monotone := sorry  -- MUST provide actual proof!
```

**Example - Lawful Protocol Abstraction**:

```lean
import Mathlib.Algebra.Order.Group.Defs

/-- A lawful abstraction for types that can flourish -/
class Flourishable (α : Type) extends LE α where
  -- Operations
  enhance : α → α → α
  diminish : α → α → α
  measure : α → ℝ
  
  -- Laws that MUST be proven for every instance
  enhance_increases : ∀ a b, a ≤ enhance a b
  diminish_decreases : ∀ a b, diminish a b ≤ a
  measure_monotone : ∀ a b, a ≤ b → measure a ≤ measure b
  enhance_diminish : ∀ a b, enhance (diminish a b) b = a

/-- Concrete instance with ALL laws proven -/
instance : Flourishable ℝ where
  enhance := (· + ·)
  diminish := (· - ·)
  measure := id
  
  enhance_increases := fun a b => le_add_of_nonneg_right (le_refl b)
  diminish_decreases := fun a b => sub_le a b
  measure_monotone := fun a b h => h
  enhance_diminish := fun a b => add_sub_cancel a b
```

### 3.2.4 Decidability for Computable Predicates

**Rationale**: A `Prop` asserts truth but doesn't guarantee computability. To use a logical predicate in a computable context (like `if/then/else`), we must provide a proof of computability. In Lean, this proof is an instance of the `Decidable` typeclass. This pattern ensures that any part of the specification that implies a decision must be backed by a proven, terminating algorithm for making that decision.

**Example - Making Logic Computable**:

```lean
import Mathlib.Data.List.Basic

/-- A logical predicate (not computable by default) -/
def hasQuorum (n : ℕ) (total : ℕ) : Prop :=
  3 * n > 2 * total

/-- Proof that the predicate is decidable (computable) -/
instance (n total : ℕ) : Decidable (hasQuorum n total) :=
  inferInstanceAs (Decidable (3 * n > 2 * total))

/-- Now we can use it in computation -/
def canProceed (votes total : ℕ) : String :=
  if hasQuorum votes total then
    "Proceed with proposal"
  else
    "Insufficient votes"

-- The predicate is both logically precise and computationally usable
example : canProceed 7 10 = "Proceed with proposal" := rfl
```

## 3.3 Compile-Time Verification

**Requirement**: Leverage Lean's type system to move as many checks as possible to compile time.

**Strategies**:

1. **Dependent Return Types**: Functions return proofs along with values
2. **Propositions as Types**: Encode requirements in type signatures
3. **Static Bounds**: Use type-level naturals for compile-time bounds checking
4. **Witness Types**: Return evidence of properties, not just boolean checks

**Example - Compile-Time Verification Patterns**:

```lean
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Vector.Basic

/-- Return a value with its proof of property -/
def findPositive (l : List ℝ) : Option {x : ℝ // x > 0 ∧ x ∈ l} :=
  match l.find? (· > 0) with
  | none => none
  | some x => 
    if h : x > 0 then
      some ⟨x, h, List.find?_some _ _ ▸ rfl⟩
    else none

/-- Bounded access with compile-time bounds checking -/
def safeGet {n : ℕ} (v : Vector α n) (i : Fin n) : α :=
  v.get i  -- No runtime bounds check needed!

/-- Witness-bearing comparison -/
inductive CompareResult (a b : ℝ) : Type
  | lt (h : a < b) : CompareResult a b
  | eq (h : a = b) : CompareResult a b  
  | gt (h : a > b) : CompareResult a b

def compare (a b : ℝ) : CompareResult a b :=
  if h : a < b then .lt h
  else if h : a = b then .eq h
  else .gt (by linarith)

/-- Type-level state machine with compile-time transition checking -/
inductive State : Type
  | ready | running | done

inductive ValidTransition : State → State → Type
  | start : ValidTransition .ready .running
  | finish : ValidTransition .running .done
  | reset : ValidTransition .done .ready

def transition {s₁ s₂ : State} (_ : ValidTransition s₁ s₂) : State := s₂

-- Invalid transitions fail at compile time:
-- def badTransition : State := transition (s₁ := .ready) (s₂ := .done) _
-- Error: no instance of ValidTransition .ready .done
```

## 3.4 No Axioms Without Justification

**Requirement**: Every axiom MUST be isolated, justified, and independently reviewed.

**Axiom Governance Process**:

1. Axioms MUST be declared in a dedicated `Axioms.lean` file
2. Each axiom MUST include:
   - Formal statement
   - Justification referencing published mathematics
   - Impact analysis on system consistency
   - Review approval documentation
3. Axioms SHOULD be eliminable through future mathematical development

**Example - Properly Governed Axioms**:

```lean
/-!
# Protocol Axioms

This file contains all axioms used in the protocol specification.
Each axiom is justified and has undergone independent review.
-/

/-- The protocol assumes classical logic for decidability.
    
    JUSTIFICATION: While constructive proofs are preferred,
    certain protocol properties require classical reasoning,
    particularly for proving impossibility results.
    
    REFERENCE: Classical logic is consistent with Lean's
    type theory (see Lean documentation, section 3.4).
    
    IMPACT: Enables use of excluded middle and choice.

    ELIMINATION PATH: Could be removed if all proofs
    are reconstructed constructively.
-/
open Classical

/-- Content equality is decidable.
    
    JUSTIFICATION: The protocol requires comparing content
    for deduplication. While content is abstract, we assume
    a decision procedure exists in any implementation.
    
    REFERENCE: Standard assumption in distributed systems
    (see Lamport, "Time, Clocks..." section 2).
    
    IMPACT: Enables content-addressed storage proofs.
    
    NOTE: While this is stated as a global axiom, a more modular
    pattern is to add `[DecidableEq Content]` as a parameter to
    functions that require it. This makes the dependency explicit
    at the function level. This global axiom can then be used to
    satisfy that parameter where needed.
-/
axiom content_decidable : DecidableEq Content

/-- Time is continuous (not discrete).
    
    JUSTIFICATION: Physical time is continuous. Discrete
    time models introduce artificial synchronization points.
    
    REFERENCE: Standard model in real-time systems
    (see Kopetz, "Real-Time Systems" ch. 3).
    
    IMPACT: Enables continuous evolution proofs.
-/
axiom time_continuous : ∀ (t₁ t₂ : Time), t₁ < t₂ → ∃ t, t₁ < t ∧ t < t₂
```

## 3.5 Domain-Driven Theorem Selection

**Principle**: Beyond mathematical completeness, prove theorems that address reasonably anticipated domain scenarios.

**Rationale**: While mathematical completeness is important, practical specifications must prioritize proofs that the domain will actually need. This prevents both over-engineering (proving theorems nobody will use) and under-engineering (missing critical domain properties).

### 3.5.1 Criteria for "Reasonably Anticipated"

A theorem is reasonably anticipated if it:

1. **Addresses the protocol's stated purpose** - Core to agentic flows, or other primary goals
2. **Enables known use patterns** - Required by distributed execution, consensus, or identified workflows  
3. **Mitigates specific risks** - Prevents resource exhaustion, consent violations, or security vulnerabilities
4. **Supports planned features** - Needed for roadmap items like collective measurement or learning

### 3.5.2 Domain Analysis Process

Before implementing proofs, conduct domain analysis:

```lean
/-!
## Domain Analysis for [Module Name]

### Known Use Cases:
1. Multi-agent coordination across distributed nodes
2. Collective decision making with consent preservation
3. Resource-bounded execution environments

### Anticipated Scenarios:
1. Tasks composed in different orders by different agents
2. Parallel execution without global coordination
3. Aggregation of collective outcomes

### Required Properties:
Based on the above, we must prove:
- Order independence for consent
- Resource bound preservation
- Flourishing aggregation properties
-/
```

### 3.5.3 Example: Domain-Driven Theorems

```lean
namespace Protocol.DomainProperties

/-! These theorems address specific anticipated scenarios rather than 
    mathematical completeness for its own sake. -/

-- SCENARIO: Distributed agents execute tasks independently
-- REQUIREMENT: Local reasoning about possibility
theorem parallel_possibility_local {α β γ δ : Type} 
    (T₁ : Task α β) (T₂ : Task γ δ) :
    (T₁ ⊗ T₂).isPossible ↔ T₁.isPossible ∧ T₂.isPossible := by
  sorry  -- TODO: Enables distributed execution

-- SCENARIO: Consent must be preserved through workflow composition  
-- REQUIREMENT: Anti-extraction guarantee
theorem compose_preserves_consent {α β γ : Type} 
    (T₁ : Task α β) (T₂ : Task β γ) 
    [ConsentRequired T₁] [ConsentRequired T₂] :
    ConsentRequired (T₂ ∘ T₁) := by
  sorry  -- TODO: Core safety property

-- SCENARIO: Resource limits in production environments
-- REQUIREMENT: Prevent denial-of-service
theorem compose_resource_bounded {α β γ : Type}
    [ResourceBounded α] [ResourceBounded β] [ResourceBounded γ]
    (T₁ : Task α β) (T₂ : Task β γ) :
    resourceCost (T₂ ∘ T₁) ≤ resourceCost T₁ + resourceCost T₂ := by
  sorry  -- TODO: Security requirement
```

### 3.5.4 Documenting Domain Context

Every domain-driven theorem MUST document its scenario:

```lean
/-- Parallel tasks can be verified independently by different agents.
    
    DOMAIN SCENARIO: In a distributed collective, agents need to verify
    task possibility without coordinating. Agent A might be checking T₁
    while Agent B checks T₂, and they need to reason about T₁ ⊗ T₂.
    
    USE CASE: Distributed proposal validation where each validator
    checks a subset of tasks.
    
    WITHOUT THIS: Agents would need global coordination, creating a
    bottleneck and single point of failure. -/
theorem parallel_possibility_local ...
```

### 3.5.5 Deferral Criteria

It's acceptable to defer a theorem if:

1. **No concrete scenario requires it yet** - Document why it might be needed later
2. **The domain abstraction is still evolving** - Mark as experimental
3. **Simpler properties suffice for now** - Prove weaker versions first

```lean
-- We prove the weaker property that suffices for current use cases
theorem compose_admissible_characterization ...

-- Full associativity deferred until needed for category abstraction
-- theorem compose_assoc : (T₃ ∘ T₂) ∘ T₁ = T₃ ∘ (T₂ ∘ T₁)
-- NOTE: Current use cases only need admissible set properties
```

### 3.5.6 Domain Completeness Checklist

When reviewing for domain completeness, verify:

- [ ] Core protocol goals have corresponding theorems
- [ ] Each anticipated workflow has safety properties proven
- [ ] Security vulnerabilities have prevention theorems
- [ ] Performance constraints have preservation proofs
- [ ] Governance properties are formally guaranteed
- [ ] Integration points have compatibility theorems

## Summary of Logic and Proof Patterns

These patterns ensure that:

- Every property has a machine-checkable proof
- Proofs are structured for human comprehension
- Verification happens at compile time when possible
- Axioms are governed and minimal
- The protocol's safety properties are mathematically guaranteed
- **Domain requirements drive theorem selection beyond pure mathematical completeness**

By following these patterns, we implement the core philosophy: if a property matters, it must be proven, not merely tested or hoped for. We prove what matters to the domain, not just what's mathematically interesting.
