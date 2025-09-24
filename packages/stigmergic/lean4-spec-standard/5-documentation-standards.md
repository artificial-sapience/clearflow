# 5. Documentation Standards

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

This section establishes requirements for documentation that ensures specifications are understandable, maintainable, and preserve the bijective correspondence between mathematics and natural language.

**Quick Reference**:

- **5.1** - Inline Documentation (definitions, theorems, functions)
- **5.2** - Bijective Correspondence (math ↔ English)
- **5.3** - Module Structure (organization, dependencies)
- **5.4** - Normative Choices (value documentation)
- **5.5** - Proof Documentation Patterns (NEW - tactical comments)
- **5.6** - Error Messages (structured, informative)

## 5.1 Inline Documentation Requirements

**Requirement**: Every definition, theorem, and non-trivial function MUST have documentation that explains its purpose and behavior.

**Documentation Components**:

1. **Purpose**: What role does this play in the system?
2. **Preconditions**: What must be true for this to be valid?
3. **Postconditions**: What is guaranteed after execution?
4. **Invariants**: What properties are preserved?
5. **Normative Choices**: Why these specific values/constraints?

**Example - Comprehensive Documentation**:

```lean
/-- Consensus mechanism for system decisions.

 PURPOSE: Enables decentralized decision-making while preventing
 minority capture and ensuring decisive action.

 PRECONDITIONS:
 - All participants have voting rights (proven by `hasVotingRights`)
 - Proposal is in valid voting window
 - No duplicate votes from same entity

 POSTCONDITIONS:
 - Returns `approved` iff votes exceed threshold
 - All votes are cryptographically verified
 - Result is deterministic given same inputs

 INVARIANTS:
 - Vote count never exceeds participant count
 - Threshold remains constant during voting

 NORMATIVE CHOICE: 2/3 threshold balances inclusivity
 with ability to make decisions. See NormativeDefaults.
-/
structure ConsensusVote where
 proposal : ProposalId
 voters : Finset EntityId
 votes : { v : EntityId // v ∈ voters } → VoteChoice
 threshold : Threshold
 /-- Invariant: All voters have rights -/
 voterRights : ∀ e ∈ voters, hasVotingRights e
```

## 5.2 Bijective Correspondence

**Requirement**: Every mathematical expression MUST have a plain English explanation that preserves ALL information bidirectionally.

**Bijection Test**: A reader should be able to:

1. Reconstruct the math from only the English
2. Understand the English from only the math
3. Verify they express identical concepts

**Patterns for Bijective Documentation**:

```lean
/-- The delta function measures change in collective wellbeing.

 Mathematically: ΔF(S, t₁, t₂) = ∑_{e ∈ S} w(e) · (f(e, t₂) - f(e, t₁))

 In English: The delta for a set S between times t₁ and t₂
 equals the sum over all entities e in S of the weight of e multiplied
 by the difference between e's at t₂ and t₁.

 Where:
 - S is a finite set of entities
 - w(e) is the positive weight assigned to entity e
 - f(e,t) is entity e's level at time t
 - All summations converge due to S being finite
-/
noncomputable def weightedDelta (S : Finset Entity) (t₁ t₂ : Time) : ℝ :=
 S.sum fun e => weight e * (measureAt e t₂ - measureAt e t₁)

/-- Objection severity ordering forms a linear hierarchy.

 Mathematically: minor < significant < paramount with transitivity

 In English: Objection severities are strictly ordered where minor
 objections are less severe than significant objections, which are
 less severe than paramount objections, and this ordering is transitive
 (if A < B and B < C, then A < C).
-/
instance : LinearOrder ObjectionSeverity where
 -- Implementation details
```

## 5.3 Module Structure

**Requirement**: Modules MUST be organized hierarchically with clear dependencies and purposes.

**Module Documentation Template**:

```lean
/-!
# Module Name

One-line summary of module purpose.

## Overview

2-3 paragraphs explaining:
- What this module defines
- How it relates to other modules
- Key concepts introduced

## Main Definitions

- `TypeName` - Brief description
- `functionName` - What it computes
- `TheoremName` - What it proves

## Implementation Notes

Technical details that help understanding:
- Why certain approaches were chosen
- Performance considerations (if any)
- Relationship to academic literature

## References

- [Author2023] Title of relevant paper
- [System] Section X.Y of formal specification
-/
```

**Example - Module Documentation**:

```lean
/-!
# .Network.Consensus

Distributed consensus mechanisms for system governance.

## Overview

This module implements the consensus layer of the System,
enabling distributed decision-making without central authority. It builds
on the entity model from `.Core` and uses the temporal logic
from `.MathematicalFoundations`.

The consensus mechanism uses a weight-adjusted voting system with
protections against various attack vectors including sybil attacks,
vote buying, and timing manipulation.

## Main Definitions

- `ConsensusVote` - A vote collection with validity proofs
- `Threshold` - Configurable approval thresholds
- `achievedConsensus` - Determines if consensus is reached
- `consensusMonotone` - Proves consensus is preserved over time

## Implementation Notes

We use Mathlib's `Finmap` for vote storage to ensure each entity
votes at most once. The weight function is abstract, allowing
different implementations (stake-based, reputation-based, etc.).

The time window mechanism prevents both rushing and stalling attacks.

## References

- [Sociocracy3.0] Consent-based governance patterns
- [Castro1999] Practical Byzantine Fault Tolerance
- [System] Section 4.2 - Consensus Mechanisms
-/
```

## 5.4 Normative Choice Documentation

**Requirement**: Every value choice that affects system behavior MUST document its normative basis and revision mechanism.

### 5.4.1 Inline Documentation Pattern

**Documentation Pattern**:

```lean
/-- Minimum time window for voting on proposals.

 VALUE: 72 hours (259200 seconds)

 NORMATIVE BASIS:
 - Balances urgency with deliberation
 - Allows participants in all time zones to engage
 - Provides time for translation and accessibility
 - Prevents rushed decisions that bypass community

 TRADEOFFS:
 - Longer: More inclusive but slower decisions
 - Shorter: Faster action but risk of exclusion

 EMPIRICAL GROUNDING:
 - Analysis of 1000 OSS governance decisions showed
 90% participation achieved within 72 hours
 - See study: [CommunityGovernance2023]

 DEPENDENCIES:
 - Interacts with quorum requirements
 - Must exceed notification delay + response time

 REVISION MECHANISM:
 - Can be adjusted via meta-governance proposal
 - Requires 80% approval (higher than normal)
 - Changes apply to future proposals only

 SUNSET: Review after 50 proposals or 6 months
-/
def minVotingWindow : Duration :=
 ⟨259200, by norm_num⟩ -- 72 hours in seconds
```

### 5.4.2 Formal Decision Files

**Requirement**: Normative decisions MUST also be captured as typed values in module-specific decision files.

**Organization Pattern**:

```text
Foundation/
├── Primitives.lean
├── PrimitivesDecisions.lean # Normative decisions for Primitives

Core/
├── Knowledge.lean
├── KnowledgeDecisions.lean # Normative decisions for Knowledge

Meta/
├── Decision.lean # NormativeDecision type framework
└── AllDecisions.lean # Optional aggregator
```

**Decision File Structure**:

```lean
import .Meta.Decision

/-!
# Knowledge Module Normative Decisions

This file documents all normative (value-laden) decisions made in the design
and implementation of the Knowledge module. These decisions are first-class
system objects that can be versioned, tracked, and evolved.
-/

namespace .Core

open .Meta

/-- Knowledge must explicitly track enabled tasks -/
def DC_KNOW_1 : NormativeDecision := {
 id := ⟨"DC-KNOW-1"⟩
 date := 1736524800 -- 2025-07-10
 type := .DC
 decision := "Knowledge must have an 'enables' field tracking tasks it makes possible"
 alternatives := [
 ("Implicit task enablement", "violates Constructor Theory principle"),
 ("Separate task-knowledge mapping", "loses locality of information"),
 ("Knowledge as passive data", "contradicts constructor-theoretic foundations")
 ]
 rationale := "In Constructor Theory, knowledge is defined by what transformations it enables. Making this explicit ensures knowledge actively participates in the system rather than being passive data."
 dependencies := []
 status := .Active
 context := some "Knowledge must be defined by the transformations it enables"
 supersededBy := none
}

/-- Collection of all knowledge module decisions -/
def knowledgeDecisions : List NormativeDecision := [
 DC_KNOW_1, DC_KNOW_2, ...
]

end .Core
```

### 5.4.3 Cross-Referencing Decisions

**Requirement**: Code MUST reference decision IDs where normative choices affect implementation.

**Cross-Reference Patterns**:

```lean
-- In the implementation file
structure Knowledge where
 /-- The tasks this knowledge enables - THE CRITICAL LINK -/
 enables : Set AnyTask
 -- ^ DC-KNOW-1: Knowledge must explicitly track enabled tasks

-- For multi-line decisions
def Knowledge.synthesize ... :=
 -- CRITICAL FIX: Use union to prevent de-consent attacks (DC-KNOW-2)
 let allConsented := sources.map (·.consentedEntities) |>.foldl (· ∪ ·) {synthesizer}
 ...
```

### 5.4.4 Benefits of This Approach

1. **Type Safety**: Decisions are typed values, not just documentation
2. **Locality**: Decisions live next to the code they affect
3. **Version Control**: Changes to modules and their decisions are tracked together
4. **Machine Processable**: Can generate reports, check dependencies, find conflicts
5. **Living Documentation**: Decisions evolve with the code

## 5.5 Proof Documentation Patterns

**Requirement**: Proofs MUST include inline comments that explain tactical choices, case analysis, and mathematical reasoning to ensure maintainability and reviewability.

**Comment Patterns by Proof Type**:

### 5.5.1 Inductive Proofs

```lean
/-- Fold with union preserves all elements from the input sets -/
theorem fold_union_preserves_all {α : Type} [DecidableEq α]
 (l : List (Set α)) (init : Set α) :
 ∀ s ∈ l, ∀ x ∈ s, x ∈ l.foldl (· ∪ ·) init := by
 -- Generalize init to handle union updates in recursion
 induction l generalizing init with
 | nil =>
 -- Base case: empty list has no sets, so the premise is vacuously true
 intro s h_mem
 simp at h_mem
 | cons hd tl ih =>
 -- Inductive step: element is either in the head set or in the tail
 intro s h_s_in_list
 simp only [List.mem_cons] at h_s_in_list
 cases h_s_in_list with
 | inl h_eq =>
 -- Case 1: s = hd (the head set)
 intro x h_x_in_s
 rw [h_eq] at h_x_in_s -- Now h_x_in_s : x ∈ hd
 -- The fold continues with accumulator (init ∪ hd)
 have h_x_in_acc : x ∈ init ∪ hd := by
 right -- x ∈ hd, so x ∈ init ∪ hd
 exact h_x_in_s
 -- Apply helper lemma: element in accumulator is preserved
 exact mem_foldl_union_acc tl (init ∪ hd) x h_x_in_acc
 | inr h_s_in_tl =>
 -- Case 2: s ∈ tl (s is in the tail)
 intro x h_x_in_s
 -- Apply inductive hypothesis with new accumulator (init ∪ hd)
 apply ih
 exact h_s_in_tl
 exact h_x_in_s
```

**Pattern Elements**:

- **Generalization comment**: Explain why `generalizing` is needed
- **Case documentation**: Each case gets a brief explanation
- **Tactical rationale**: Why `right` vs `left` in union membership
- **Lemma application**: What helper lemmas accomplish

### 5.5.2 Contradiction Proofs

```lean
/-- String append with non-empty suffix creates distinct strings -/
theorem string_append_ne_self (s : String) (suffix : String) :
 suffix ≠ "" → s ≠ s ++ suffix := by
 intro h_suffix_ne h_eq
 -- Strategy: derive a contradiction from the length equality
 -- If s = s ++ suffix, then their lengths must be equal
 have len_eq : s.length = (s ++ suffix).length := by
 rw [← h_eq]
 -- But string concatenation adds lengths: |s ++ suffix| = |s| + |suffix|
 have len_append : (s ++ suffix).length = s.length + suffix.length := by
 exact String.length_append s suffix
 -- Substituting: s.length = s.length + suffix.length, so suffix.length = 0
 rw [len_append] at len_eq
 have suffix_len_zero : suffix.length = 0 := by
 linarith -- Linear arithmetic resolves n = n + m → m = 0
 -- But suffix.length = 0 means suffix = "", contradicting our assumption
 have : suffix = "" := by
 cases suffix with
 | mk data =>
 simp [String.length] at suffix_len_zero
 simp [suffix_len_zero]
 contradiction
```

**Pattern Elements**:

- **Strategy statement**: High-level approach to the proof
- **Step explanations**: What each `have` statement establishes
- **Arithmetic reasoning**: Why `linarith` works here
- **Contradiction setup**: How the final contradiction is derived

### 5.5.3 Conditional Logic Proofs

```lean
/-- EVOLVE validates knowledge with sufficient positive evidence -/
theorem EVOLVE_validation_logic (k : Knowledge) (outcomes : List TaskOutcome)
 (evolver : EntityId) (cycle : Nat) :
 ((relevantOutcomes outcomes k.id).length ≥ 5) ∧
 (((relevantOutcomes outcomes k.id).filter (·.success)).length ≥ 4) →
 (k.EVOLVE outcomes evolver cycle).status = KnowledgeStatus.Validated := by
 intro ⟨h_total_ge_5, h_successes_ge_4⟩
 -- Unfold EVOLVE and relevantOutcomes to expose filters uniformly
 simp only [Knowledge.EVOLVE, relevantOutcomes]
 -- Use `show` to make the goal explicit and manageable
 show (let relevantOutcomes := outcomes.filter (fun o => o.enablingKnowledge == k.id)
 let successCount := relevantOutcomes.filter (·.success) |>.length
 let totalCount := relevantOutcomes.length
 let newStatus := if totalCount ≥ 5 ∧ successCount ≥ 4
 then KnowledgeStatus.Validated
 else if totalCount ≥ 3 ∧ successCount = 0
 then KnowledgeStatus.Falsified
 else k.status
 newStatus) = KnowledgeStatus.Validated
 -- Simplify let expressions and expose the if-then-else structure
 simp only
 -- Case analysis on the nested conditionals
 split_ifs with h1 h2
 · -- Case 1: totalCount ≥ 5 ∧ successCount ≥ 4 → Validated
 rfl
 · -- Case 2: ¬(totalCount ≥ 5 ∧ successCount ≥ 4) - impossible given our assumptions
 -- Contradiction: assumptions violate this branch's negation
 exfalso
 exact h1 ⟨h_total_ge_5, h_successes_ge_4⟩
 · -- Case 3: Similar impossibility
 -- Contradiction: assumptions violate this branch's negation
 exfalso
 exact h1 ⟨h_total_ge_5, h_successes_ge_4⟩
```

**Pattern Elements**:

- **Unfolding explanation**: Why `simp only` with specific lemmas
- **Goal management**: Why `show` is used for complex expressions
- **Case enumeration**: Each branch gets explanation
- **Contradiction comments**: Why exfalso cases are impossible

### 5.5.4 Helper Lemma Documentation

```lean
/-- Helper lemma: if an element is in the accumulator, it remains after folding -/
lemma mem_foldl_union_acc {α : Type} [DecidableEq α]
 (l : List (Set α)) (acc : Set α) (x : α) :
 x ∈ acc → x ∈ l.foldl (· ∪ ·) acc := by
 intro h_acc
 -- We need `generalizing acc` to allow the accumulator to change in recursive calls
 induction l generalizing acc with
 | nil =>
 -- Base case: empty list returns the accumulator unchanged
 exact h_acc
 | cons hd tl ih =>
 -- Inductive case: fold over (hd :: tl) = fold over tl with (acc ∪ hd)
 unfold List.foldl
 apply ih
 -- Since x ∈ acc, we have x ∈ acc ∪ hd (left side of union)
 left
 exact h_acc
```

**Pattern Elements**:

- **Purpose statement**: What the helper accomplishes
- **Technical rationale**: Why `generalizing acc` is needed
- **Base case clarity**: What the trivial case does
- **Recursive explanation**: How the inductive step works

### 5.5.5 Comment Style Guidelines

**Formatting**:

- Use `--` for inline comments (space after dashes)
- Use `-- Strategy:` for high-level approach explanations
- Use `-- Case N:` for case analysis documentation
- Use `-- Contradiction:` for exfalso explanations

**Content**:

- Explain **why** not just **what** the tactics do
- Include **mathematical intuition** behind formal steps
- Document **tactical choices** (e.g., why `left` vs `right`)
- Explain **goal management** decisions (e.g., why `show` is used)

**Consistency**:

- Similar proof patterns should have similar comment patterns
- Use consistent terminology across the module
- Maintain the same level of detail throughout

## 5.6 Error Messages and Diagnostics

**Requirement**: Custom error messages MUST be informative and suggest corrections.

**Error Message Pattern**:

```lean
/-- Custom error types provide structured, type-safe error information -/
inductive ProposalError
 | contentTooShort (actual : Nat) (required : Nat)
 | contentTooLong (actual : Nat) (maximum : Nat)
 | windowTooShort (actual : Duration) (required : Duration)
 | windowTooLong (actual : Duration) (maximum : Duration)

/-- Error messages are generated from the structured error types -/
def ProposalError.signal : ProposalError → String
 | .contentTooShort a r => s!"Content has {a} chars but needs at least {r} to ensure substantive content"
 | .contentTooLong a m => s!"Content has {a} chars but maximum is {m} to ensure reviewability"
 | .windowTooShort a r => s!"Window is {a} but minimum is {r} for inclusive participation"
 | .windowTooLong a m => s!"Window is {a} but maximum is {m} to ensure timely decisions"

/-- Smart constructor that returns structured, informative errors -/
def mkProposal (content : String) (window : Duration)
 : Except ProposalError Proposal := do
 if h : content.length < 10 then
 .error (.contentTooShort content.length 10)
 else if h : content.length > 10000 then
 .error (.contentTooLong content.length 10000)
 else if h : window < minVotingWindow then
 .error (.windowTooShort window minVotingWindow)
 else if h : window > maxVotingWindow then
 .error (.windowTooLong window maxVotingWindow)
 else
 .ok ⟨generateId (), content, window, .draft⟩
```

## Summary of Documentation Standards

These standards ensure that:

- Every definition is fully documented with purpose and constraints
- Mathematical notation has precise English equivalents
- Modules are well-organized with clear dependencies
- **Normative choices are transparent, typed, and co-located with code**
- **Decisions are first-class objects that can be versioned and tracked**
- Error messages guide users toward correct usage
- **Proofs include tactical explanations for maintainability**
- **Comment patterns are consistent across similar proof types**
- **Mathematical intuition is preserved alongside formal reasoning**

Good documentation is not just about explaining code - it's about preserving the mathematical precision while making it accessible to humans. This bridges the gap between formal verification and practical understanding.

The normative decision documentation approach (section 5.4) transforms value-laden choices from static documentation into living, typed values that evolve with the code. The proof documentation patterns (section 5.5) are based on proven practices from the Knowledge.lean module, which achieved exemplary maintainability through systematic application of these comment patterns.
