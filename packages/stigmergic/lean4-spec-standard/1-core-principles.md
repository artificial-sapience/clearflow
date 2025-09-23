# 1. Core Principles

> Version: 0.1.0-draft  
> Status: Section 1 Draft for Review  
> Part of: Lean 4 Specification Standard

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section establishes the non-negotiable principles that govern all Lean 4 specifications.

**Our Goal**: Formally proving that the protocol is incapable of violating its specified critical properties.

This represents a fundamental paradigm shift:

- **From** testing for correctness → **To** proving the absence of failure
- **From** empirical confidence → **To** logical certainty
- **From** avoiding failure through runtime checks → **To** making failure unrepresentable
- **From** implicit assumptions → **To** explicit, machine-checkable trusted base

These principles ensure that if our specification compiles, it is mathematically guaranteed to maintain its critical invariants.

## 1.1 The Principle of Representational Correctness

**Principle**: The type system MUST make invalid states unrepresentable. Every invariant must be enforced by construction, not validation.

**Rationale**: Types are our primary tool for compile-time verification. When we defer semantic checking to runtime—whether through string parsing, boolean validation, or runtime assertions—we abandon the mathematical certainty that Lean 4 provides. A well-typed program should be incapable of representing an invalid state.

**Requirements**:

- All semantic distinctions MUST be encoded as distinct types, type variants, or refined types
- Type invariants MUST be enforced by the type's structure itself
- For complex invariants, structures MUST be private with instantiation only through smart constructor functions that require proofs of invariants as arguments
- Invalid states MUST be unrepresentable
- The use of `axiom` is forbidden except under extreme circumstances:
  - Any use MUST be isolated in a dedicated file (e.g., `Axioms.lean`)
  - MUST include formal justification referencing established mathematical literature
  - MUST be approved through formal review process
- No runtime parsing to extract semantic meaning from untyped data
- No `sorry` or `admit` in any specification

**Example - Smart Constructor Pattern**:

```lean
import Mathlib.Data.Real.Basic

/-- A resource with non-negative capacity.
    The structure is private and HOLDS THE PROOF of its own invariant. -/
private structure Resource where
  capacity : ℝ
  proof : 0 ≤ capacity  -- The proof is now a field in the structure

/-- Public-facing opaque type -/
def ResourceType : Type := Resource

/-- Smart constructor requiring proof of non-negativity -/
def mkResource (c : ℝ) (h : 0 ≤ c) : ResourceType :=
  ⟨c, h⟩  -- The proof `h` is now stored within the object

/-- Accessor function that provides BOTH the value and the proof of the invariant.
    There is no `sorry` because the proof is retrieved from the structure. -/
def Resource.capacity (r : ResourceType) : {c : ℝ // 0 ≤ c} :=
  ⟨r.capacity, r.proof⟩

-- Attempting mkResource (-10) fails at compile time - no proof `h` can be provided
```

**Example - Incorrect (Validation Instead of Construction)**:

```lean
-- ANTI-PATTERN: Runtime validation
def mkResource? (c : ℝ) : Option Resource :=
  if 0 ≤ c then some ⟨c⟩ else none  -- Defers checking to runtime!
```

## 1.2 Theorem-Driven Development

**Principle**: Properties precede implementation. State theorems first, then develop functions to satisfy them.

**Requirements**:

- Development MUST follow a theorem-first workflow:
  1. Define types
  2. State theorems about desired properties
  3. Implement functions guided by proof obligations
- Every function's core properties (preconditions, postconditions, invariants) MUST be specified as formal theorems
- All function totality, termination, and well-foundedness MUST be proven
- Non-terminating functions are only allowed if explicitly defined using co-inductive types or stream types, with clear justification
- Proofs MUST be structured for human readability:
  - Complex proofs MUST be decomposed into well-named lemmas
  - Each proof step SHOULD include brief comments explaining the reasoning
  - Tactical proofs SHOULD prefer structured proof terms where clarity benefits

**Example - Theorem-First Development**:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Order.Monotone.Basic

/-- Specification: A function that is monotone and non-negative -/
structure GrowthFunction where
  func : ℝ → ℝ
  property : Monotone func ∧ ∀ t, 0 ≤ func t

/-- First: State the theorem that our intended implementation has the property.
    This can be a private lemma used to construct the final object. -/
private theorem exponentialGrowth_has_property (rate : ℝ) (h : 0 < rate) :
    Monotone (fun t => Real.exp (rate * t)) ∧ ∀ t, 0 ≤ Real.exp (rate * t) := by
  constructor
  · -- Prove monotonicity
    intro t₁ t₂ ht
    exact Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_left ht (le_of_lt h))
  · -- Prove non-negativity
    intro t
    exact Real.exp_pos _

/-- Then: Implement a function that RETURNS the function AND its proof, bundled.
    The return type `GrowthFunction` guarantees any user gets the properties. -/
def makeGrowingResource (rate : ℝ) (h : 0 < rate) : GrowthFunction := {
  func := fun t => Real.exp (rate * t),
  property := exponentialGrowth_has_property rate h
}
```

**Example - Incorrect (Implementation Without Properties)**:

```lean
-- ANTI-PATTERN: Implementation without formal specification
def growthFunction (t : ℝ) : ℝ := t * t + 1

-- Hope it's monotonic? Hope it's always positive? No guarantees!
```

## 1.3 The Specification/Implementation Firewall

**Principle**: Protocol specifications exist in a pure mathematical realm. No implementation details may cross this firewall.

**Rationale**: The protocol must remain valid across all possible implementations—from quantum computers to biological systems. Any implementation detail in the specification constrains future evolution and undermines universality.

**Requirements**:

- All protocol definitions MUST be computationally pure (exist within the identity monad)
- No function in the specification may have a type signature including `IO` or any effect-capable monad
- Mathematical types MUST be used exclusively:
  - Use `ℝ` for real numbers, never `Float`
  - Use `ℕ` for natural numbers, never `UInt32`
  - Opaque data MUST be wrapped in a dedicated `OpaqueData` type with no operations
- Implementation-specific types (`Float`, `UInt8`, array indices) are forbidden
- Bridge code between implementation and specification:
  - MUST reside in separate files clearly marked as implementation
  - MUST NOT be imported by any specification file
  - Is explicitly NOT part of the protocol

**Example - Pure Specification with OpaqueData**:

```lean
import Mathlib.Data.Real.Basic

/-- A wrapper for data that must not be inspected by the protocol.
    It is intentionally defined with no operations, not even equality. -/
def OpaqueData : Type := String

/-- Pure mathematical specification of resource composition -/
structure ResourceComposition where
  /-- Mathematical composition function -/
  compose : ℝ → ℝ → ℝ
  /-- Proof of associativity -/
  assoc : ∀ a b c, compose a (compose b c) = compose (compose a b) c
  /-- Identity element -/
  identity : ℝ
  /-- Proof of identity behavior -/
  id_left : ∀ a, compose identity a = a
  id_right : ∀ a, compose a identity = a

/-- Example: A message with opaque content the protocol cannot inspect -/
structure Message where
  timestamp : ℝ
  content : OpaqueData  -- Protocol can pass it but never examine it
  
/-- This lives in pure math - no algorithms, no efficiency concerns -/
def totalResources (comp : ResourceComposition) (resources : List ℝ) : ℝ :=
  resources.foldl comp.compose comp.identity
```

**Example - Incorrect (Implementation Leakage)**:

```lean
-- ANTI-PATTERN: Efficiency concerns polluting specification
def efficientResourceSum (resources : Array Float) : Float := do
  let mut sum := 0.0
  for r in resources do
    sum := sum + r  -- Mutation! Implementation detail!
  return sum
```

## 1.4 Principled Mathematical Modeling

**Principle**: All mathematical concepts MUST use Mathlib's canonical definitions. Custom structures require extraordinary justification.

**Rationale**: Mathlib provides battle-tested, deeply integrated mathematical structures with thousands of proven theorems. Reimplementing these structures abandons this foundation and risks subtle errors that undermine protocol integrity.

**Requirements**:

- All mathematical concepts MUST use or extend canonical Mathlib definitions:
  - Groups, rings, fields from `Mathlib.Algebra`
  - Orders and lattices from `Mathlib.Order`
  - Topological structures from `Mathlib.Topology`
  - Measure theory from `Mathlib.MeasureTheory`
- All axioms and properties MUST be fully proven, not merely stated
- The choice of mathematical structure MUST be justified:
  - Why is this the right abstraction?
  - What theorems does it give us?
  - What constraints does it enforce?
- Temporal properties MUST use continuous, ordered structures from Mathlib
- Custom mathematical definitions require:
  - Proof that no Mathlib equivalent exists
  - Independent review of the definition
  - Plan to upstream to Mathlib

**Example - Leveraging Mathlib**:

```lean
import Mathlib.Algebra.Group.Defs
import Mathlib.Algebra.Order.Group.Defs  -- For OrderedAddCommGroup
import Mathlib.Data.Real.Basic

/-- Time is simply non-negative reals with Mathlib's order structure -/
def Time := {t : ℝ // 0 ≤ t}

/-- We get ordered structure for free from Mathlib -/
instance : LinearOrder Time := Subtype.linearOrder _

/-- Resources form an ordered additive commutative group.
    By extending `OrderedAddCommGroup`, we inherit the structure and all
    theorems relating the group operation (+) to the order (≤). -/
class ResourceAlgebra (R : Type*) extends OrderedAddCommGroup R

/-- Example: Real-valued resources automatically satisfy our requirements
    because Mathlib already has a proven instance of OrderedAddCommGroup for ℝ. -/
instance : ResourceAlgebra ℝ := inferInstance
```

**Example - Incorrect (Reimplementing Mathlib)**:

```lean
-- ANTI-PATTERN: Reimplementing what Mathlib provides
structure MyGroup where
  carrier : Type
  op : carrier → carrier → carrier  
  id : carrier
  -- Why rebuild what thousands have verified?
```

## 1.5 Provably Governed Normative Parameters

**Principle**: Every value choice embeds ethics. These choices MUST be explicit, revisable, and type-safe in their governance.

**Requirements**:

- Every normative parameter MUST be a named constant with full documentation block
- A central enumerated type MUST list all governable parameters
- The objection mechanism MUST be type-safe:
  - Parameter identification through enumeration, not strings
  - Proposed values must match the parameter's type
  - Governance procedures must be formally specified
- Each normative choice MUST document:
  - Its ethical basis and tradeoffs
  - Formal mechanism for revision
  - Dependencies on other normative choices
  - Sunset conditions where applicable

**Example - Type-Safe Normative Governance**:

```lean
import Mathlib.Data.Rat.Basic
import Mathlib.Data.Real.Basic

/-- Enumeration of all governable normative parameters -/
inductive NormativeParameter
  | minimumQuorum
  | maxProposalLifetime  
  | consensusThreshold
  deriving Repr, DecidableEq

/-- Type-safe parameter values using dependent types -/
def NormativeParameter.type : NormativeParameter → Type
  | .minimumQuorum => ℚ        -- Rational for exact representation
  | .maxProposalLifetime => ℝ   -- Real for time duration
  | .consensusThreshold => ℚ    -- Rational for voting

/-- Current parameter values with full normative documentation -/
namespace NormativeDefaults

/-- Minimum quorum for collective decisions
    
    NORMATIVE BASIS: Balances inclusivity (high quorum) with 
    action capability (low quorum). 2/3 reflects common practice
    in democratic systems while preventing minority capture.
    
    TRADEOFFS: 
    - Higher → More inclusive but harder to act
    - Lower → Easier to act but risk of minority control
    
    DEPENDENCIES: Interacts with consensusThreshold
    
    REVISION: Via meta-governance proposal (see Governance.lean)
    
    SUNSET: Review after 100 decisions or 365 days
-/
def minimumQuorum : ℚ := 2/3

end NormativeDefaults

/-- A structured analysis of predicted impact -/
structure ImpactAnalysis where
  predictedEffect : String
  affectedStakeholders : List String  -- Would be List EntityType in full system
  confidenceLevel : {q : ℚ // 0 ≤ q ∧ q ≤ 1}  -- Confidence as bounded rational
  supportingData : List OpaqueData  -- References to external analysis

/-- Type-safe objection with structured justification fields -/
structure NormativeObjection where
  param : NormativeParameter
  proposedValue : param.type  -- Dependent type ensures type safety!
  rationale : String  -- Core argument may remain textual
  ethicalJustification : String  -- Substance enforced by formal review process, not length
  impactAnalysis : ImpactAnalysis  -- Structured impact assessment
  supporters : List Id

/-- Example: Fully structured objection -/
def validObjection : NormativeObjection := {
  param := .minimumQuorum
  proposedValue := 3/4  -- Must be ℚ, not ℝ or String!
  rationale := "Current quorum allows too much minority control in practice"
  ethicalJustification := "Democratic theory suggests that decisions affecting a community should represent a clear majority will. The current 2/3 threshold has allowed factional groups to push through changes that later proved divisive. Raising to 3/4 better ensures broad consensus while still enabling action."
  impactAnalysis := {
    predictedEffect := "Approximately 20% reduction in proposal passage rate"
    affectedStakeholders := ["active_proposers", "passive_members"]
    confidenceLevel := ⟨7/10, by norm_num⟩
    supportingData := []
  }
  supporters := []
}
```

**Example - Incorrect (Stringly-Typed Governance)**:

```lean
-- ANTI-PATTERN: String-based governance allows errors
structure BadObjection where
  paramName : String      -- "minmumQuorum"? Typo goes undetected!
  newValue : String       -- "0.75"? "75%"? "three quarters"?
  -- No type safety, no parameter validation
```

## Summary of Section 1: Core Principles

This section establishes five strengthened principles that create "nuclear-grade" assurance:

### Key Enhancements from Review

1. **Global Mathlib Mandate** - Now explicitly requires using Mathlib's battle-tested definitions rather than reimplementing mathematical structures

2. **1.1: The Principle of Representational Correctness** (formerly "Type Safety Above All")
   - Added smart constructor pattern requirement
   - Explicit axiom governance with isolation and review requirements
   - Focus on making invalid states unrepresentable

3. **1.2: Theorem-Driven Development** (formerly "Proof-Driven Development")
   - Formalized theorem-first workflow
   - Added proof readability requirements
   - Explicit handling of non-terminating functions

4. **1.3: The Specification/Implementation Firewall** (formerly "Protocol Purity")
   - Explicit monad separation (pure vs IO)
   - Clear boundaries for bridge code
   - Stronger requirements on mathematical types

5. **1.4: Principled Mathematical Modeling** (formerly "Mathematical Rigor")
   - Mandatory use of Mathlib structures
   - Justification requirements for mathematical choices
   - Custom definitions need review and upstream plan

6. **1.5: Provably Governed Normative Parameters** (formerly "Normative Transparency")
   - Type-safe governance using dependent types
   - Enumerated parameters preventing string errors
   - Comprehensive documentation requirements

### What This Achieves: Proving the Absence of Failure

Through these principles, we achieve:

1. **Logical Certainty over Empirical Confidence**
   - Not "we tested it and it worked" but "we proved it cannot fail"
   - Machine-checkable proofs eliminate human error in reasoning
   - No untested edge cases - the proof covers all possibilities

2. **Failure Made Impossible, Not Just Avoided**
   - Invalid states cannot be constructed, not merely checked against
   - If it compiles, it respects all proven properties
   - Runtime validation becomes unnecessary

3. **System-Wide Guarantees**
   - Not just "function A works" but "A ∘ B preserves all invariants"
   - Emergent behaviors are captured and constrained by types
   - Composition preserves safety properties

4. **Explicit, Auditable Trust Base**
   - Every axiom isolated and justified
   - All assumptions machine-checkable
   - Clear boundary between proven and assumed

This is the shift from "hoping it works" to "proving it cannot break."

## 1.6 Automated Compliance Verification

**Principle**: Adherence to this standard MUST be maximally automated. Manual review alone is insufficient for safety-critical specifications.

**Rationale**: Human review, no matter how careful, is prone to error. For a system where we're proving the absence of failure, the verification of compliance with these principles must itself be systematic and automated.

**Requirements**:

- A suite of custom Lean 4 linters MUST be developed to automatically detect violations:
  - Use of `axiom` outside designated files
  - Presence of `sorry` or `admit`
  - Use of implementation types (`Float`, `UInt32`, etc.)
  - Public structures that should be private
  - Missing proofs for properties
  - Non-Mathlib mathematical definitions without justification
- The continuous integration pipeline MUST:
  - Run all compliance checks on every commit
  - Enforce exact toolchain versions
  - Verify all proofs compile without warnings
  - Check for complete specification coverage
- Any approved deviation from these principles:
  - MUST be documented in a `deviations.md` file
  - MUST include formal justification
  - MUST have review approval documented
  - Creates an auditable exception trail

**Example - Compliance Check Configuration**:

```lean
/-- Custom linter to detect forbidden implementation types -/
@[linter]
def noFloatLinter : Linter where
  name := "no_float"
  test := fun decl => do
    let type ← getConstType decl
    if type.contains `Float then
      return some "Float type detected in specification"
    return none

/-- Verify all structures with invariants are private -/
@[linter]  
def privateInvariantLinter : Linter where
  name := "private_invariants"
  -- Implementation would check structure visibility

/-- CRITICAL: Detect typeclasses with laws in comments instead of fields -/
@[linter]
def lawfulTypeClassLinter : Linter where
  name := "lawful_typeclass"
  test := fun decl => do
    if isClass decl then
      let docs ← getDocs decl
      if docs.contains "Law:" && !hasLawFields decl then
        return some "Typeclass has laws in documentation but not as proof fields!"
    return none

/-- Detect operations without property theorems -/
@[linter]
def operationPropertiesLinter : Linter where
  name := "operation_properties"
  test := fun decl => do
    if isCompositionOp decl then
      let name := declName decl
      unless (hasTheorem (name ++ "_assoc") && 
              hasTheorem (name ++ "_id")) do
        return some s!"Operation {name} missing property theorems"
    return none
```

## Summary

These core principles work together to create specifications where mathematical certainty replaces hope, where the compiler enforces correctness, and where trust emerges from proof rather than testing.
