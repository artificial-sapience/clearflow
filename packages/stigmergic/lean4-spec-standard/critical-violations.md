# Critical Violations to Check First

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Overview

Before any other review, check for these most common and critical violations. These represent the most frequent ways specifications fail to achieve mathematical certainty.

## 1. Lawless Typeclasses (MOST CRITICAL VIOLATION)

**Check**: For every typeclass with laws, are the laws fields requiring proofs?

```lean
-- ❌ VIOLATION: Laws as documentation only
class InformationSignalSpace (ι : Type) where
 copy : ι → ι × ι
 erase : ι → Unit
 /-- Law: Copy preserves information. -/
 copy_preserves : ∀ i, (copy i).1 = i ∧ (copy i).2 = i -- This is just a comment!

-- ✅ CORRECT: Laws as required proof fields
class InformationSignalSpace (ι : Type) where
 copy : ι → ι × ι
 erase : ι → Unit
 copy_preserves : ∀ i, (copy i).1 = i ∧ (copy i).2 = i -- Must prove this!
```

**Why Critical**: Without proof fields, any instance can violate the laws. The compiler cannot help you.

## 2. Operations Without Properties

**Check**: For every operation (especially compose, combine, merge), are there theorems?

```lean
-- ❌ VIOLATION: Operation defined, properties assumed
def Task.compose := ...
-- Where are the theorems about associativity, identity, etc.?

-- ✅ CORRECT: Operation with proven properties
def Task.compose := ...
theorem Task.compose_assoc : (T₃ ∘ T₂) ∘ T₁ = T₃ ∘ (T₂ ∘ T₁) := ...
theorem Task.compose_id_left : id ∘ T = T := ...
```

## 3. Undocumented Classical Logic

**Check**: Is `Classical.em` or any axiom used without documentation?

```lean
-- ❌ VIOLATION: Hidden use of classical logic
theorem Task.possible_or_impossible := by
 exact Classical.em _ -- No justification!

-- ✅ CORRECT: Documented use with justification
/-- Uses classical logic (excluded middle) as impossibility
 results require classical reasoning. See Axioms.lean. -/
theorem Task.possible_or_impossible := by
 exact Classical.em _
```

## Quick Detection Guide

### How to Spot Lawless Typeclasses

1. Search for `class` definitions
2. Look for comment patterns like `/-- Law:` or `-- Law:`
3. Check if the "law" is actually a field requiring proof
4. Try to create a violating instance - if it compiles, it's broken!

### How to Spot Missing Properties

1. Search for operations: `compose`, `merge`, `combine`, `join`
2. Look for corresponding theorems with `_assoc`, `_id`, `_comm`
3. Check preservation theorems for operations on constrained types
4. If theorems are missing, the operation is unverified

### How to Spot Hidden Axioms

1. Search for `Classical.`, `axiom`, `sorry`, `admit`
2. Check for imports of `Classical`
3. Look for uses without documentation
4. Verify all axioms are in designated `Axioms.lean` file

## Summary

These three violations represent the most common ways specifications fail to achieve compiler-verified correctness:

1. **Lawless typeclasses** mean instances can violate intended behavior
2. **Operations without properties** mean composition behavior is unverified
3. **Undocumented axioms** mean hidden assumptions about the system

Always check for these first. Fixing these violations is the fastest path to a mathematically rigorous specification.
