# Session Context: Stigmergic Coordination Specification

## Major Breakthrough: Abstract Signal Design

This session achieved a fundamental architectural insight: **Signal should be an abstract base type** that users extend, not a concrete type with prescribed fields. This follows ClearFlow's successful pattern where the framework provides abstractions (`Message`, `Command`, `Event`) and users create concrete implementations.

### Key Design Decisions

1. **Signal as Abstract Base**
   - Framework defines only: id, emitter, timestamp
   - NO forced "content" field
   - Users extend with domain-specific fields
   - Natural field names (`text` for chat, `ticker` for markets)

2. **Intelligence Abstraction**
   - `IntelligenceProvider` interface for all decision-making
   - Supports LLM, human, and hybrid intelligence
   - Agents delegate ALL logic to intelligence provider
   - No fixed thresholds or attraction lists

3. **Framework/User Separation**
   - **Framework**: Coordination mechanics, safety properties
   - **User Code**: Signal types, DSPy integration, domain logic
   - **No DSPy in core**: Users choose their LLM framework

### What We Analyzed

1. **Theory Alignment**: Reviewed theory docs, confirmed we're on path but need to emphasize:
   - "Relevance" over "attraction" (semantic, not physical)
   - LLM-first design (delegate complexity to intelligence)
   - Emergent coordination (no prescribed flows)

2. **DSPy's Role**: "Programming not prompting" happens in user code:
   - Users create Pydantic models extending Signal
   - DSPy signatures work with user's typed signals
   - Framework stays agnostic to LLM approach

3. **Chat Example**: Perfect first validation:
   - Shows paradigm shift (prescribed flow → emergent coordination)
   - Demonstrates human + LLM agents
   - Natural multi-party support

### Current State

**Lean Specification**: Needs refactoring (see plan.md Task 1.1-1.4)
- Signal has wrong structure (needs abstraction)
- Agent has fixed thresholds (needs IntelligenceProvider)
- Properties need updating for intelligent agents

**Documentation**: Complete and aligned
- MVP design doc: Updated with abstract Signal pattern
- Plan: Reorganized with correct task sequence
- Theory docs: Remain as vision/background

### Critical Insights

1. **Simplicity Through Abstraction**: By making Signal abstract, we get:
   - Maximum flexibility for users
   - Clean DSPy integration (Pydantic models ARE signals)
   - No artificial wrapping or parsing

2. **Intelligence Delegation**: The `IntelligenceProvider` pattern enables:
   - LLM agents (via DSPy)
   - Human agents (via input())
   - Hybrid agents (escalation patterns)
   - Same coordination mechanics for all

3. **True Emergence**: With abstract signals and delegated intelligence:
   - No predefined message types
   - No fixed coordination patterns
   - Users discover what works for their domain

## Next Steps

See `plan.md` for detailed implementation phases. Priority is fixing the Lean specification to match our abstract Signal design, then implementing the Python framework following ClearFlow's pattern.