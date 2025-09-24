# Continue Stigmergic Coordination Development

Please continue work on the Stigmergic Coordination Lean4 specification, implementing the abstract Signal design we've established.

## Context
Read @session-context.md for the key architectural decisions and insights from our previous session.

## Current Priority
Start with Phase 1, Task 1.1 from @plan.md:
- Update `Stigmergic/Foundation/Signal.lean` to be an abstract interface
- Remove prescribed "content" field
- Keep only minimal coordination properties

## Key Design Principle
**Signal is abstract**: Like ClearFlow's `Message` base class, our `Signal` should define minimal required properties (id, emitter, timestamp). Users extend it with domain-specific fields. No forced "content" field - users choose natural names for their domain.

## Implementation Approach
1. Start by reading the current Signal.lean to understand what needs changing
2. Refactor to abstract class/interface pattern
3. Update decisions file with rationale
4. Run `lake -q build` and fix any errors without suppressions

## Remember
- Agents are proxies for intelligence (LLM/human/hybrid)
- Framework provides coordination, users provide semantics
- DSPy belongs in user code, not framework core
- Follow ClearFlow's successful abstraction pattern

Begin by examining the current `Signal.lean` implementation and proposing the refactoring approach.