# Continue Stigmergic Coordination Development

Please continue work on the Stigmergic Coordination Lean4 specification, starting with implementing the abstract Signal design we've established.

## Context
Read @session-context.md for the key architectural decisions and insights from our previous session.

## Current Priority
Start with Phase 1, Task 1.1 from @plan.md:
- Update `Stigmergic/Foundation/Signal.lean` to be an abstract interface
- Remove prescribed "content" field and SignalType
- Ensure strength calculation is NOT in Signal (belongs in SignalSpace)
- Keep only minimal coordination properties (id, emitter, timestamp, initialStrength)

## Key Design Principles to Follow
1. **Signal is abstract**: Like ClearFlow's `Message` base class, our `Signal` should define minimal required properties. Users extend it with domain-specific fields.

2. **Environment calculates strength**: SignalSpace computes current strength from initial emission + reinforcements + decay. Signal itself is just immutable data.

3. **MVP completeness**: Even the simplest implementation must have:
   - Attention-minutes as conserved quantity
   - Proper decay for ALL components (including reinforcements)
   - Learning loop with credibility updates from outcomes

## Implementation Approach
1. Start by reading the current Signal.lean to understand what needs changing
2. Convert to class/interface pattern (Lean's equivalent of abstract base)
3. Create example concrete implementations showing user extensions
4. Update SignalDecisions.lean with rationale
5. Run `lake -q build` and fix any errors without suppressions

## Critical Reminders
- No `sorry` statements in proofs
- Agents are proxies for intelligence (LLM/human/hybrid)
- Framework provides coordination mechanics, users provide semantics
- Reinforcements MUST decay based on age (critical bug we fixed)
- Follow the corrected reinforcement design in @packages/stigmergic/docs/reinforcement-design.md

Begin by examining the current `Signal.lean` implementation and proposing the refactoring approach to make it abstract.