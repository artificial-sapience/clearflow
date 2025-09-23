# Lean 4 Specification Standard

> Version: 0.1.0-draft  
> Status: Section 1 Draft for Review  
> Purpose: Unified standard for mathematically rigorous, type-safe Lean 4 specifications

## Overview

This modular organization of the Lean 4 Specification Standard provides clear navigation and easier reference for different aspects of formal verification.

**IMPORTANT**: Always start with [0-core-philosophy.md](0-core-philosophy.md) - it contains the fundamental principle that drives every requirement in this standard.

## Document Structure

The standard is organized into the following modules:

0. **[Core Philosophy](0-core-philosophy.md)** - The fundamental principle: machine-checkable truth ⭐ START HERE

1. **[Core Principles](1-core-principles.md)** - The philosophical "Why" and strengthened principles for formal assurance

2. **[Type Design Patterns](2-type-design-patterns.md)** - The structural "What" - making invalid states unrepresentable

3. **[Logic and Proof Patterns](3-logic-proof-patterns.md)** - The dynamic "How" - ensuring every property is machine-verified

4. **[Mathematical Foundations](4-mathematical-foundations.md)** - The axiomatic "Ground" - building on Mathlib's verified structures

5. **[Documentation Standards](5-documentation-standards.md)** - The human "Interface" - preserving mathematical precision for humans, including normative decision tracking

6. **[Code Organization](6-code-organization.md)** - The architectural "Blueprint" - scaling principles to large systems

7. **[Multi-Epistemic Considerations](7-multi-epistemic.md)** - The living "Bridge" - acknowledging what transcends formalization

8. **[Compliance and Audit Guide](8-compliance-audit.md)** - Practical tools for verifying compliance

Additionally:

- **[Critical Violations](critical-violations.md)** - The most common and critical violations to check first

## Quick Start

1. Read [0-core-philosophy.md](0-core-philosophy.md) first - it's brief but essential
2. Review [critical-violations.md](critical-violations.md) to avoid the most common mistakes
3. Use [8-compliance-audit.md](8-compliance-audit.md) for the compliance scorecard
4. Reference other sections as needed for specific patterns and requirements

## Related Documents

This standard is comprehensive for all Lean 4 specification needs. For additional guidance, see:

- [project-governance.md](../project-governance.md) - Repository organization, versioning, and development workflows

## RFC 2119 Compliance Notice

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

For clarity:

- **MUST/REQUIRED/SHALL**: Absolute requirement of the specification
- **MUST NOT/SHALL NOT**: Absolute prohibition of the specification
- **SHOULD/RECOMMENDED**: Strong recommendation; may be ignored only with valid justification
- **SHOULD NOT/NOT RECOMMENDED**: Strong discouragement; may be done only with valid justification
- **MAY/OPTIONAL**: Truly optional; implementation choice

Specifications complying with this standard SHALL be directly mechanizable in Lean 4 and maintain the mathematical rigor required for formal verification. This means:

- A Lean 4 developer can implement the specification without making design choices
- A mathematician can verify correctness without consulting external sources
- An engineer can implement without resolving ambiguities
- A reviewer can check completeness by reading linearly from top to bottom

## Foundational Mandate: Mathlib as Mathematical Foundation

**Requirement**: All mathematical structures and concepts MUST be built upon or directly use the definitions and hierarchies provided by Mathlib.

**Rationale**: Mathlib represents thousands of hours of expert review and verification. It provides battle-tested definitions of mathematical structures with extensive theorem libraries. Re-implementing these structures risks introducing subtle errors and abandons a massive corpus of proven properties.

**Exceptions**: Custom mathematical definitions are permissible ONLY when:

1. No suitable Mathlib equivalent exists
2. The need is formally documented with extensive justification
3. The custom definition undergoes independent proof review
4. A plan exists to eventually contribute the definition to Mathlib
