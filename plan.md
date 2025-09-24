# Stigmergic Coordination Implementation Plan

## Current Status
- ✅ Design documents completed (MVP design, reinforcement design)
- ✅ Core architectural decisions made
- 🚧 Lean specification needs refactoring for abstract Signal
- ⏳ Python implementation not started

## Phase 1: Fix Lean Specification (Current Priority)

### Task 1.1: Update Signal to Abstract Interface
- [ ] Update `Stigmergic/Foundation/Signal.lean`:
  - Convert Signal to a class/interface with minimal properties (id, emitter, timestamp, initialStrength)
  - Remove prescribed "content" field and SignalType
  - Keep only essential coordination properties
  - Ensure strength calculation is NOT in Signal (belongs in SignalSpace)
- [ ] Create example concrete Signal implementations
- [ ] Update `SignalDecisions.lean` with abstraction rationale
- [ ] Run `lake -q build` and fix all errors

### Task 1.2: Create IntelligenceProvider Interface
- [ ] Add `Stigmergic/Core/IntelligenceProvider.lean`
- [ ] Define interface for LLM/human/hybrid intelligence:
  - `evaluateRelevance : Role → Signal α → IO Float`
  - `generateResponse : Role → List (Signal α) → IO (Option (Signal α))`
  - `discoverRole : List (Signal α × Bool) → IO Role`
- [ ] Document decisions in `IntelligenceProviderDecisions.lean`

### Task 1.3: Refactor Agent to Use Intelligence
- [ ] Update `Stigmergic/Core/Agent.lean`:
  - Remove fixed `relevanceThreshold` and `attractedTypes`
  - Add `intelligence : IntelligenceProvider` field
  - Update `perceive` to `observe` using intelligence.evaluateRelevance
  - Add `act` method delegating to intelligence.generateResponse
- [ ] Update `AgentDecisions.lean`

### Task 1.4: Update SignalSpace for Environmental Dynamics
- [ ] Update `Stigmergic/Core/SignalSpace.lean`:
  - Add `getCurrentStrength` method (calculates with decay + reinforcements)
  - Add `reinforce` method for amplifying/inhibiting signals
  - Remove any strength calculation from Signal itself
- [ ] Add reinforcement tracking structures

## Phase 2: Python MVP Implementation (Week 1-2)

### Task 2.1: Core Package Structure
- [ ] Create `packages/stigmergic/python/` directory
- [ ] Set up `pyproject.toml` with minimal dependencies
- [ ] Create `stigmergic/__init__.py` with public API

### Task 2.2: Implement MVP Reinforcement
- [ ] Create `signal.py` with abstract Signal base class
- [ ] Create `agent.py` with MVPAgent (credibility + budget)
- [ ] Create `space.py` with MVPSignalSpace:
  - Proper decay for all components
  - Reinforcement with attention cost
  - External outcome handling
- [ ] Create `reinforcement.py` with MVPReinforcement types

### Task 2.3: Implement Intelligence Providers
- [ ] Create `intelligence.py` with abstract IntelligenceProvider
- [ ] Create `providers/dspy_provider.py` (requires DSPy in examples)
- [ ] Create `providers/human_provider.py` (uses input())
- [ ] Create `providers/hybrid_provider.py` (escalation logic)

## Phase 3: Validation Examples (Week 3)

### Task 3.1: Stigmergic Chat Example
- [ ] Port chat example to stigmergic pattern
- [ ] Define ChatMessage signal type
- [ ] Implement with human + LLM agents
- [ ] Compare with ClearFlow version

### Task 3.2: Portfolio Analysis Example
- [ ] Port portfolio analysis to stigmergic
- [ ] Show emergent coordination
- [ ] Demonstrate reinforcement dynamics

## Phase 4: Documentation & Testing (Week 4)

### Task 4.1: Comprehensive Testing
- [ ] Unit tests for MVP reinforcement
- [ ] Integration tests for learning loop
- [ ] Property tests for invariants

### Task 4.2: Documentation
- [ ] API documentation
- [ ] Migration guide from ClearFlow
- [ ] Comparison table of approaches

## Success Criteria
- [ ] Lean spec compiles with no `sorry`
- [ ] MVP Python implementation with complete learning loop
- [ ] Chat example working with emergent coordination
- [ ] All tests passing with 100% coverage of public API