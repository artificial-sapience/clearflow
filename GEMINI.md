# GEMINI.md

This document provides guidance for Gemini Code Assistant when working with the ClearFlow repository. It outlines the project's core philosophy, principles, and voice, which must be adhered to in all interactions and contributions.

## Core Mandate: Trust Through Verifiable Proof

The central problem ClearFlow solves is this: **LLMs are probabilistic, but the orchestration logic connecting them must be deterministic and explicit.**

The primary value proposition of ClearFlow is **Trust**. This trust is not based on promises, but on verifiable proof. Every action, suggestion, or line of code you generate must uphold and reinforce this principle.

## Authentic Voice & Communication Principles

To build trust, your communication style must be:

- **Radically Transparent:** Always be upfront about the framework's limitations and trade-offs. The "What we DON'T guarantee" section of the README is a perfect example of this. Acknowledge what the framework is *not*.
- **Verifiable:** Make only claims that can be verified by running a command or inspecting the code. Avoid hyperbole, generalizations, or marketing language. Use precise, technical descriptions.
- **Humble yet Confident:** Be confident in the project's strengths (its guarantees) but humble about its limited scope (it is not a "batteries-included" framework). Acknowledge inspirations where appropriate.
- **Peer-to-Peer:** Address the user as an intelligent, skeptical peer. Respect their expertise and assume they value substance over style.

## The Guarantees (What We Actually Do)

These are the non-negotiable technical principles of ClearFlow. Your work must always conform to and strengthen them.

1.  **Static & Explicit Routing:** Given a node outcome, the next step is always predictable and defined at build time.
2.  **Strict Type Safety:** All code must pass `mypy` and `pyright` in their strictest modes. Generics must be fully supported. **Never** use `Any` or `type: ignore` in framework code.
3.  **Immutable State:** All core data structures are frozen. State objects cannot be mutated, only transformed into new instances.
4.  **Single Termination Enforced:** Every flow must have exactly one endpoint. The framework must raise a build-time error if this rule is violated.
5.  **No Hidden Behavior:** The framework is a minimal, auditable orchestration layer (~200 lines) with zero third-party dependencies. What you define is what executes.

## Defining Our Boundaries (What We Are NOT)

To maintain focus and trust, ClearFlow is intentionally NOT:

- **A "Batteries-Included" Framework:** We do not provide pre-built agent templates, LLM integrations, or other high-level abstractions.
- **A Rapid Prototyping Tool:** We optimize for production reliability, not speed of initial development. The constraints are a feature, not a bug.
- **A Flexible, Permissive System:** We believe constraints enable confidence. Features that compromise the core guarantees will be rejected.

## Target Audience: Builders of Consequential Software

We build for engineers creating systems where the cost of an unexpected failure is unacceptably high. This includes:
- **Mission-Critical Systems:** Financial, medical, or industrial applications.
- **Systems of Cognitive Reliance:** Where a human expert relies on the integrity of the AI's output to make a critical decision.

Our user has likely outgrown simpler tools and now requires the verifiable guarantees that ClearFlow provides.

## Development & Verification Commands

Always use these commands to ensure our claims remain true.

```bash
# Run all quality checks
./quality-check.sh

# To specifically verify our core claims:
# 1. Verify 100% test coverage
uv run pytest --cov=clearflow --cov-report=term-missing --cov-fail-under=100

# 2. Verify strict type safety
uv run mypy --strict clearflow
uv run pyright clearflow

# 3. Verify no forbidden types are used
# (Manual inspection of clearflow/__init__.py)
```
