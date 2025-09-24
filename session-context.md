# Session Context: Stigmergic Coordination Specification

## Session Overview
This session focused on refining the stigmergic coordination design with emphasis on first-principles correctness, particularly for the reinforcement mechanism. We made critical architectural decisions about Signal abstraction and fixed fundamental flaws in the reinforcement design.

## Critical Design Decisions Made

### 1. Signal as Abstract Base Type
**Decision**: Signal should be an abstract interface with only stigmergic essentials (id, emitter, timestamp, initialStrength), following ClearFlow's successful Message pattern.

**Key Insights**:
- NO prescribed "content" field - users extend with domain-specific fields
- Users choose natural names (`text` for chat, `ticker` for markets)
- Signal doesn't calculate its own strength - that's SignalSpace's responsibility
- This enables clean DSPy integration where user's Pydantic models ARE signals

### 2. Environmental Strength Calculation
**Decision**: SignalSpace (environment) calculates current strength, not the Signal itself.

**Biological Accuracy**:
- Mirrors real stigmergy where pheromone evaporation is environmental
- Signal only carries initial emission strength (immutable)
- Current strength emerges from decay + reinforcements
- Any agent can reinforce, but signal owner has no special control

### 3. MVP Reinforcement Design (Corrected)

**Critical Fixes Applied**:
1. **Reinforcement Decay**: ALL reinforcements must decay based on age, not just initial strength
2. **Conserved Quantity**: Attention-minutes as explicit scarce resource
3. **Complete Learning Loop**: MVP includes credibility updates from outcomes
4. **Sign-Aware Logic**: Credibility considers whether agent amplified/inhibited correctly
5. **Agent Structure**: MVP has agents with budgets from day 1

**MVP Now Includes**:
- Proper decay: `r.amount * (0.5 ^ (rAge / halfLife))` for each reinforcement
- Budget constraints: Agents have finite daily attention budgets
- Learning: Outcomes immediately update agent credibility
- Resource conservation: Can't spend more attention than available

### 4. Terminology Decisions
- Use "emit" not "deposit" (avoiding biological metaphors)
- "Decay" is correct scientific term (not "fade" or "diminish")
- "Reinforcement" for strengthening signals (not "pheromone trails")
- "Attention-minutes" as the conserved quantity

## Key Documents Created/Updated

1. **reinforcement-design.md**: Complete progressive design from MVP to first principles
   - Fixed critical flaws identified by reviewers
   - Now has working MVP with complete learning loop
   - Progressive enhancement phases clearly defined

2. **stigmergic-mvp-design.md**: Updated with architectural decisions
   - Signal abstraction principles
   - Environmental dynamics responsibility
   - Framework vs user code separation

3. **plan.md**: Reorganized with clear implementation phases
   - Phase 1: Fix Lean specification (current priority)
   - Phase 2: Python MVP implementation
   - Phase 3: Validation examples
   - Phase 4: Documentation & testing

## Technical Insights Gained

### From Reinforcement Critiques
1. **Conservation Required**: Without a conserved quantity, the system has no scarcity or economic pressure
2. **Decay Must Be Universal**: If reinforcements don't decay, "active forgetting" is impossible
3. **External Grounding Essential**: Without outcomes affecting credibility, system is self-referential
4. **Sign Matters**: Correctly inhibiting bad signals should be rewarded

### From Signal Design Analysis
1. **Abstraction Enables Flexibility**: Prescribed fields limit domain modeling
2. **Environment Owns Dynamics**: Signals are data, spaces are behavior
3. **Type Safety Through Extension**: Users create typed signals extending abstract base

## Next Priority Tasks

See `plan.md` for detailed task list. Immediate priorities:

1. **Task 1.1**: Refactor Signal.lean to abstract interface
2. **Task 1.2**: Create IntelligenceProvider interface
3. **Task 1.3**: Update Agent to delegate to intelligence
4. **Task 1.4**: Move strength calculation to SignalSpace

## Important Constraints

- Lean specification must compile with no `sorry` statements
- MVP must be implementable in 1 week
- Python implementation should be ~100-200 lines for MVP
- Must maintain biological accuracy while using domain-appropriate terminology
- 100% test coverage requirement (following ClearFlow standards)