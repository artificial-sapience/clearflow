# 8. Compliance Scorecard and Audit Guide

> Version: 0.1.0-draft
> Status: Section 1 Draft for Review
> Part of: Lean 4 Specification Standard

## Core Philosophy Reminder

**THE FUNDAMENTAL PRINCIPLE**: If a property matters, the compiler must check it.

## Quick Compliance Scorecard

Use this scorecard to quickly assess compliance level:

### Level 1: Type Safety (Minimum Bar)

- [ ] No `sorry` in proofs
- [ ] No unguarded `axiom` (all axioms in dedicated file with justification)
- [ ] No implementation types (`Float`, `UInt32`) in specifications
- [ ] All invariants enforced by types, not runtime validation
- [ ] Smart constructors for complex invariants

### Level 2: Proof Completeness (Core Requirement)

- [ ] Every typeclass law is a proof-requiring field
- [ ] Every operation has property theorems (e.g., associativity, identity)
- [ ] All composition operations have preservation theorems
- [ ] Classical logic usage is documented
- [ ] All functions are total or have explicit domain restrictions

### Level 3: Documentation (Professional Standard)

- [ ] Module follows template (Overview, Main Definitions, etc.)
- [ ] Inline docs include PURPOSE, PRECONDITIONS, POSTCONDITIONS
- [ ] Bijective correspondence between math and English
- [ ] File organization uses `section` blocks
- [ ] Normative choices documented with revision mechanisms

**Compliance Levels**:

- **Minimum Compliance**: All Level 1 + Level 2 ✓
- **Full Compliance**: All levels ✓

## How to Audit a Lean 4 Specification

### Phase 1: Compiler-Enforced Properties (CRITICAL)

1. **For each typeclass**, ask:

    - Are ALL laws expressed as fields requiring proofs?
    - Can I create an instance that violates the laws? (Try it!)
    - Example test: Try to create `instance : InformationSpace Unit` without proving laws

2. **For each operation**, ask:

    - What properties should it have? (associativity? commutativity? identity?)
    - Are these properties stated as theorems?
    - Are the theorems proven (not `sorry`)?

3. **For each structure with invariants**, ask:

    - Can I construct an invalid instance?
    - Are the fields private with smart constructors?
    - Do operations preserve invariants?

### Phase 2: Theorem Coverage (IMPORTANT)

1. **Check operation coverage**:

    ```lean
    -- For any binary operation like `compose`, expect:
    theorem compose_assoc : ...
    theorem compose_id_left : ...
    theorem compose_id_right : ...
    ```

2. **Check preservation theorems**:

    ```lean
    -- For any operation on constrained types:
    theorem operation_preserves_invariant : ...
    ```

### Phase 3: Documentation Review

Apply the existing documentation standards, but remember: **documentation is not verification**.

## Common Pitfalls to Avoid

1. **Mistaking documentation for specification**: Comments don't compile
2. **Assuming "obvious" properties**: If it's not proven, it's not guaranteed
3. **Focusing on style over substance**: Pretty code that allows violations is worthless
4. **Missing the forest for the trees**: The goal is machine-verified correctness

## Automated Compliance Checks

When automated linters are available, they should check for:

- Use of `axiom` outside designated files
- Presence of `sorry` or `admit`
- Use of implementation types (`Float`, `UInt32`, etc.)
- Public structures that should be private
- Missing proofs for properties
- Non-Mathlib mathematical definitions without justification

## Manual Review Checklist

For aspects that cannot be automatically checked:

### Mathematical Foundations

- [ ] All continuous quantities use ℝ, not Float
- [ ] Mathematical structures use Mathlib definitions
- [ ] Custom mathematical definitions have justification
- [ ] Temporal properties use continuous models

### Type Design

- [ ] Semantic distinctions have distinct types
- [ ] No string parsing for semantic information
- [ ] Phantom types prevent ID confusion
- [ ] Abstract models allow multiple implementations

### Proof Patterns

- [ ] All recursive functions have termination proofs
- [ ] Partial functions have explicit domain restrictions
- [ ] Typeclasses have laws as proof-requiring fields
- [ ] Properties precede implementation

### Organization

- [ ] Clear layer hierarchy without cycles
- [ ] Minimal, organized imports
- [ ] Consistent naming conventions
- [ ] Proper visibility/encapsulation

### Multi-Epistemic

- [ ] Non-formalizable aspects acknowledged
- [ ] Interface points between formal/informal marked
- [ ] Experimental features properly marked
- [ ] Evolution mechanisms documented

## Red Flags in Review

Be especially alert for:

1. **Laws in comments instead of fields** - The #1 violation
2. **Operations without property theorems** - Especially `compose`, `merge`, etc.
3. **Missing termination proofs** - Security vulnerability
4. **String-based dispatch** - Loss of type safety
5. **Undocumented axioms** - Hidden assumptions
6. **Implementation types in specs** - Breaks abstraction

## Summary

This audit guide focuses on what matters most: ensuring that if a property matters, the compiler checks it. Use the scorecard for quick assessment, follow the audit phases for thorough review, and watch for common pitfalls.

Remember: The goal is not just clean code or good documentation - it's mathematical certainty about system behavior. Every compromise on these standards is a compromise on that certainty.
