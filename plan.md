# Stigmergic Coordination Lean4 Specification Plan

## Current Status
**Specification needs refactoring** to match MVP design:
- ✅ Zero `sorry` statements
- ✅ Clean build
- ❌ Signal has wrong structure (needs to be abstract)
- ❌ Agent has fixed thresholds (needs IntelligenceProvider)
- ❌ Missing intelligence abstraction

## Core Architecture Decision
**Signal as Abstract Base Type**: Following ClearFlow's pattern, the framework defines abstract `Signal` with minimal properties (id, emitter, timestamp). Users extend with domain-specific fields. No forced "content" field.


## Implementation Phases

### Phase 1: Fix Agent Specification (Week 1)

#### Task 1.1: Update Signal to Abstract Interface
- [ ] Update `Stigmergic/Foundation/Signal.lean`:
  - Change Signal to a class/interface with minimal properties
  - Remove any prescribed "content" field
  - Keep only: id, emitter, timestamp as required properties
- [ ] Update `SignalDecisions.lean` documenting abstraction rationale
- [ ] Run `lake -q build` and fix all errors (no suppressions)

#### Task 1.2: Create IntelligenceProvider Interface
- [ ] Add `Stigmergic/Core/IntelligenceProvider.lean`
- [ ] Define `IntelligenceProvider` structure with:
  - `evaluateRelevance : Role → α → IO Float` (where α is any Signal implementation)
  - `generateResponse : Role → List α → IO (Option α)`
  - `discoverRole : List (α × Bool) → IO Role`
- [ ] Document decisions in `IntelligenceProviderDecisions.lean`
- [ ] Run `lake -q build` and fix all errors (no suppressions)

#### Task 1.3: Refactor Agent to Use Intelligence
- [ ] Update `Stigmergic/Core/Agent.lean`:
  - Remove `relevanceThreshold : NNReal`
  - Remove fixed `attractedTypes : List SignalType`
  - Add `intelligence : IntelligenceProvider` field
  - Add `history : List (Signal × Bool)` for learning
- [ ] Update `Agent.perceivesSignal` to `Agent.observe` using intelligence
- [ ] Add `Agent.act` method delegating to intelligence
- [ ] Add `Agent.learn` method for role evolution
- [ ] Update `AgentDecisions.lean` documenting the refactor
- [ ] Run `lake -q build` and fix all errors (no suppressions)

#### Task 1.4: Update Properties for Intelligent Agents
- [ ] Update `Stigmergic/Properties/Safety.lean`:
  - Prove agents only act on relevant signals
  - Prove agent identity preserved through learning
- [ ] Update `Stigmergic/Properties/Emergence.lean`:
  - Prove coordination without direct communication
  - Prove signals mediate all interaction
- [ ] Run `lake -q build` and fix all errors (no suppressions)

### Phase 2: Python Implementation Bridge (Week 2)

#### Task 2.1: Create Python Package Structure
- [ ] Create `packages/stigmergic/python/` directory
- [ ] Set up `pyproject.toml` (NO DSPy dependency in core!)
- [ ] Create `stigmergic/__init__.py` with public API exports
- [ ] Run `uv sync` to set up environment

#### Task 2.2: Implement Core Abstractions
- [ ] Create `signal.py`:
  - Abstract `Signal` base class (matching Lean interface)
  - Required properties: id, emitter, timestamp
  - No content field - users extend as needed
- [ ] Create `intelligence.py`:
  - Abstract `IntelligenceProvider` base class
  - Methods work with any Signal implementation
- [ ] Create `agent.py`:
  - Agent class using IntelligenceProvider
  - Observe, act, learn methods
- [ ] Create `space.py`:
  - SignalSpace as simple list of signals
  - Generic over signal type

#### Task 2.3: Create Example Intelligence Providers
- [ ] In `examples/providers/`:
  - `DSPyProvider` - requires DSPy in example deps
  - `HumanProvider` - uses input() for decisions
  - `HybridProvider` - combines both
- [ ] Write tests showing framework/user code separation

### Phase 3: Stigmergic Chat Example (Week 3)

#### Task 3.1: Port Chat Example
- [ ] Create `examples/stigmergic_chat/`
- [ ] Define user's signal types:
  - `ChatMessage(Signal)` with text, reply_to fields
  - Natural field names, no forced "content"
- [ ] Implement chat-specific providers:
  - Extend framework's IntelligenceProvider
  - Use DSPy for assistant intelligence
- [ ] Implement main chat loop (no prescribed flow!)
- [ ] Test with human + LLM interaction

#### Task 3.2: Validate Against ClearFlow Version
- [ ] Compare functionality with `examples/chat/`
- [ ] Demonstrate multi-party chat capability
- [ ] Show specialized assistant responses
- [ ] Document advantages of stigmergic approach

#### Task 3.3: Performance Testing
- [ ] Test with 10-100 signals in space
- [ ] Measure LLM API call costs
- [ ] Validate response times
- [ ] Confirm memory usage acceptable

### Phase 4: Additional Examples & Documentation (Week 4)

#### Task 4.1: Portfolio Analysis Example
- [ ] Port `examples/portfolio_analysis/` to stigmergic
- [ ] Show goal decomposition (analyze → assess risk → decide)
- [ ] Demonstrate emergent coordination
- [ ] Compare with flow-based version

#### Task 4.2: Multi-Agent Code Review
- [ ] Create code review example
- [ ] Multiple specialized reviewers (style, security, performance)
- [ ] Show how reviewers coordinate through signals
- [ ] No central orchestrator needed

#### Task 4.3: Documentation and Validation
- [ ] Update main README with stigmergic examples
- [ ] Create comparison table: ClearFlow vs Stigmergic
- [ ] Document migration guide
- [ ] Validate all examples run successfully

## References
- MVP Design: `packages/stigmergic/docs/stigmergic-mvp-design.md`
- Theory: `packages/stigmergic/docs/stigmergic-coordination-theory.md`