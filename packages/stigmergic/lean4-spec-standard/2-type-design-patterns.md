# 2. Type Design Patterns

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section provides concrete patterns for implementing the principles from Section 1. Each pattern demonstrates how to make invalid states unrepresentable while maintaining mathematical elegance.

## 2.1 Semantic Types (No String Parsing)

**Pattern**: Every distinct semantic concept MUST have its own type. Never encode meaning in strings or other primitive types.

**Rationale**: The type system is our primary tool for compile-time verification. When semantic information is encoded in strings, we lose all guarantees and must resort to runtime parsing.

**Implementation Strategy**:

1. Identify all semantic distinctions in your domain
2. Create an inductive type or structure for each distinction
3. Use smart constructors where validation is needed
4. Never use string matching to determine behavior

**Example - Entity Roles**:

```lean
import Mathlib.Data.Finset.Basic

/-- Semantic types for different entity roles in the system -/
inductive EntityRole
 | proposer /-- Can create proposals -/
 | reviewer /-- Can review but not propose -/
 | observer /-- Read-only access -/
 | administrator /-- Meta-governance rights -/
 deriving Repr, DecidableEq

/-- Permissions are derived from roles, not string parsing -/
def EntityRole.canPropose : EntityRole → Bool
 | .proposer => true
 | .administrator => true
 | _ => false

def EntityRole.canReview : EntityRole → Bool
 | .reviewer => true
 | .proposer => true
 | .administrator => true
 | .observer => false

/-- Type-safe role assignment with no string parsing -/
structure Entity where
 id : Id
 roles : Finset EntityRole -- Can have multiple roles

/-- Check permissions through types, not strings -/
def Entity.canPropose (e : Entity) : Bool :=
 e.roles.any (·.canPropose)
```

**Anti-Pattern to Avoid**:

```lean
-- NEVER DO THIS: Encoding semantics in strings
structure BadEntity where
 id : Id
 roleString : String -- "proposer", "reviewer", etc.

def BadEntity.canPropose (e : BadEntity) : Bool :=
 e.roleString.contains "proposer" || e.roleString.contains "admin" -- String parsing!
```

## 2.2 Dependent Types for Invariants

**Pattern**: Use dependent types, primarily `Subtype` (written `{x : T // P x}`), to bundle values with proofs of their properties. This is the primary way to refine general types into specific ones that cannot represent invalid states.

**Rationale**: This pattern makes invariants part of the type itself, shifting validation from runtime to compile time. It is the most direct implementation of "making invalid states unrepresentable."

**Implementation Strategy**:

1. Identify properties that must always hold
2. Use Lean's subtype notation `{x : T // P x}` to create refined types
3. For complex invariants, use structures with proof fields
4. Provide smart constructors that bundle values with their proofs
5. Ensure operations preserve invariants by returning refined types

**Example - Core Refinement Patterns**:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Data.String.Basic

/-- A probability is a real number between 0 and 1 -/
def Probability := {p : ℝ // 0 ≤ p ∧ p ≤ 1}

/-- Smart constructor for probabilities -/
def mkProbability (p : ℝ) (h : 0 ≤ p ∧ p ≤ 1) : Probability := ⟨p, h⟩

/-- Operations preserve the invariant -/
def Probability.complement (p : Probability) : Probability :=
 ⟨1 - p.val, by
 obtain ⟨hp₀, hp₁⟩ := p.property
 constructor <;> linarith⟩

/-- Valid identifier: non-empty, alphanumeric with underscores -/
def ValidIdentifier := {s : String // s.length > 0 ∧ s.all (fun c => c.isAlphanum || c = '_')}

/-- Time intervals with proven ordering using structure -/
structure TimeInterval where
 start : Time
 finish : Time
 valid : start ≤ finish -- Proof field ensures validity

/-- Duration is provably non-negative -/
def TimeInterval.duration (ti : TimeInterval) : {d : ℝ // 0 ≤ d} :=
 ⟨ti.finish.val - ti.start.val, by linarith [ti.valid]⟩

/-- Bounded collections with size guarantees -/
def BoundedList (α : Type) (n : ℕ) := {l : List α // l.length ≤ n}

/-- Adding requires proof we won't exceed bound -/
def BoundedList.cons {α : Type} {n : ℕ} (x : α) (bl : BoundedList α n)
 (h : bl.val.length < n) : BoundedList α n :=
 ⟨x :: bl.val, by
 simp only [List.length_cons] -- New length is (old length + 1)
 -- We need to prove: bl.val.length + 1 ≤ n
 -- We know from h: bl.val.length < n
 -- This is equivalent to: bl.val.length + 1 ≤ n
 exact Nat.succ_le_of_lt h⟩
```

## 2.3 Phantom Types for Disambiguation

**Pattern**: Create distinct types by wrapping primitive types in structures parameterized by "phantom" type tags that exist only at compile time.

**Rationale**: A common source of critical errors is using the wrong kind of identifier or value (e.g., passing a `ProposalId` where a `UserId` is expected). Phantom types prevent these errors with zero runtime cost, as the tags are erased during compilation.

**Implementation Strategy**:

1. Define a generic wrapper type parameterized by a phantom tag
2. Create empty tag types to distinguish different uses
3. Define type aliases using the wrapper with specific tags
4. The compiler enforces distinctions while runtime representation is identical

**Example - Type-Safe Identifiers**:

```lean
/-- Generic ID type parameterized by phantom type -/
structure Id (entity : Type) where
 value : String
 deriving Repr

/-- Phantom tags - these types are never instantiated -/
inductive UserTag
inductive ProposalTag
inductive EntityTag
inductive ContentTag

/-- Type-safe ID aliases -/
def UserId := Id UserTag
def ProposalId := Id ProposalTag
def EntityId := Id EntityTag
def ContentId := Id ContentTag

/-- Functions require specific ID types -/
def getUser (id : UserId) : Option User := sorry

def submitProposal (author : UserId) (proposal : ProposalId) : Bool := sorry

/-- Example: Type error at compile time -/
def example_type_safety (uid : UserId) (pid : ProposalId) : Unit :=
 -- let _ := getUser pid -- COMPILE ERROR! Expected UserId, got ProposalId
 let _ := getUser uid -- This compiles
 let _ := submitProposal uid pid -- Correct types
 () -- Return Unit

/-- Phantom types for units of measure -/
structure Quantity (unit : Type) where
 value : ℝ

inductive Meters
inductive Seconds
inductive MetersPerSecond

def Distance := Quantity Meters
def Duration := Quantity Seconds
def Velocity := Quantity MetersPerSecond

/-- Type-safe operations -/
def velocity (d : Distance) (t : Duration) : Velocity :=
 ⟨d.value / t.value⟩

-- velocity t d -- Would be a compile error! (wrong argument order)
```

## 2.4 Abstract Mathematical Models

**Pattern**: Define system concepts using abstract mathematical types, leaving concrete representations to implementations.

**Rationale**: A formal specification must be timeless and independent of any specific technology. By defining interfaces as abstract mathematical structures (e.g., an "append-only log" with certain proven properties), we avoid tying the system to a specific implementation (like a Merkle Tree, a Git repository, or a blockchain). This ensures the system remains valid and can be implemented by future technologies we cannot yet imagine, while guaranteeing that any compliant implementation will have the mathematically proven properties required for safety and interoperability.

**Implementation Strategy**:

1. Use mathematical types (ℝ, ℕ, Set α) in specifications
2. Define abstract types for domain concepts without revealing representation
3. Specify behavior through mathematical properties, not algorithms
4. Let implementations choose appropriate concrete representations

**Example - Abstract Content Storage**:

```lean
import Mathlib.Data.Set.Basic

/-- Abstract content type with no specified representation -/
constant Content : Type

/-- Abstract storage with mathematical specification -/
structure ContentStore where
 /-- The set of stored content -/
 contents : Set Content
 /-- Retrieval function (mathematical, not algorithmic) -/
 retrieve : Content → Prop
 /-- Consistency: can only retrieve what's stored -/
 retrieve_subset : ∀ c, retrieve c → c ∈ contents

/-- Merkle tree specified abstractly as properties, not structure -/
structure MerkleTree where
 /-- Root hash is an abstract identifier -/
 root : Id
 /-- Verification is a mathematical relation, not an algorithm -/
 verifies : Content → Id → Prop
 /-- Completeness property -/
 complete : ∀ c h, verifies c h → ∃ path, validPath path root h
 /-- Soundness property -/
 sound : ∀ c₁ c₂ h, verifies c₁ h → verifies c₂ h → c₁ = c₂

-- Note: No commitment to binary trees, hash functions, or other implementation details
```

**Anti-Pattern to Avoid**:

```lean
-- NEVER DO THIS: Exposing implementation details
structure BadMerkleTree where
 root : ByteArray -- Implementation detail!
 hashFn : ByteArray → ByteArray -- Algorithm, not property!
 leftChild : Option BadMerkleTree -- Forces binary tree structure!
 rightChild : Option BadMerkleTree
```

## Summary of Type Design Patterns

These patterns work together to create specifications where:

- Every semantic distinction is captured in types
- Invariants are enforced by construction
- Invalid states cannot be represented
- Abstract specifications allow multiple implementations
- The compiler verifies correctness

By following these patterns, we shift verification from runtime to compile time, achieving the core philosophy that if a property matters, the compiler must check it.
