# ClearFlow Target Audience

This document defines who we build for and who we hope will contribute to ClearFlow. It guides our messaging, design decisions, and community building.

## What We Build

ClearFlow is **deterministic orchestration** for **LLM-powered agentic software** - we provide the predictable framework layer that manages your probabilistic LLM calls.

## Primary Users

**Engineers building LLM-powered agents for production**
- Creating autonomous agents that use LLMs to reason, decide, and act
- Need deterministic orchestration layer, not another source of uncertainty
- Have experienced framework-level failures compounding LLM variability
- Want at least one layer of their stack they can fully test and trust

**Developers who've outgrown minimal frameworks**
- Started with lightweight tools but hit their limits with complex agents
- Need proper generics support for type-safe state management between LLM calls
- Want 100% test coverage in their orchestration layer (can't test LLMs, can test everything else)
- Require deterministic flow logic even when LLM outputs vary

**Teams where LLM-powered agent failures have real consequences**
- Financial services (LLM-powered trading agents, intelligent compliance systems)
- Healthcare (diagnostic agents using medical LLMs, treatment recommendation systems)
- Customer service (autonomous support agents that resolve complex issues)
- Software development (coding agents that plan and execute changes)
- DevOps automation (self-healing systems powered by LLM reasoning)

**Developers building multi-step LLM workflows**
- Orchestrating chains of LLM calls with conditional logic
- Managing immutable state between varying LLM interactions
- Need explicit, testable orchestration logic regardless of LLM responses
- Want framework determinism to compensate for LLM non-determinism

## Contributors

**Engineers who understand LLM-powered agents**
- Have built production agents and know the failure modes
- Understand why LLM non-determinism requires explicit handling
- Can contribute patterns for common agent architectures

**Functional programming enthusiasts**
- Appreciate immutability for tracking state between LLM calls
- Understand why pure functions help isolate non-determinism to the LLMs
- Know how to test the deterministic parts of non-deterministic systems

**Type safety advocates**
- Run mypy/pyright in strict mode on their own agent code
- Understand the challenge of typing LLM responses
- Never use `Any` when proper types can model LLM outputs

## NOT Our Audience

**Rapid prototypers**
- Building quick LLM demos or chatbots
- Want to "just make it work"
- Don't need production reliability

**Teams wanting all-in-one platforms**
- Expect built-in prompt templates and LLM integrations
- Want pre-built agent architectures
- Need high-level abstractions over LLM complexity

**Developers who prefer implicit behavior**
- Want the framework to handle LLM errors automatically
- Prefer convention over explicit configuration
- Like "magic" that hides complexity

**People building simple LLM applications**
- Basic chatbots without agent behavior
- Single-shot LLM calls without workflows
- Stateless request-response patterns

## In One Sentence

**We build for engineers who need deterministic orchestration for their non-deterministic LLM agents, and who know that at least one layer of the stack must be fully testable.**

## Origin Story

ClearFlow exists because LLM outputs are probabilistic by nature. Your framework shouldn't add more variability:
- LLM responses vary between runs; your flow logic should be deterministic
- State mutations compound variability; immutability provides one source of truth

We built ClearFlow for developers who need at least one predictable layer in their stack while building agents with inherently non-deterministic LLMs.

## What This Means for Development

This audience definition guides our decisions:
- **API Design**: Deterministic orchestration patterns (e.g., single termination ensures flows complete predictably)
- **Documentation**: Clear boundaries between what we control (orchestration) and what we don't (LLM behavior)
- **Feature Requests**: "No" to anything that adds non-determinism to the orchestration layer
- **Examples**: Real patterns showing how to manage LLM variability with deterministic flows
- **Success Metrics**: Orchestration that behaves consistently regardless of LLM variations

## What This Means for Contributors

Contributors should expect:
- PRs must demonstrate value for LLM-powered agent development
- Examples must show realistic agent patterns, not simple LLM calls
- Code must handle LLM non-determinism explicitly
- Tests must cover agent workflow edge cases
- Documentation must explain agent behavior, not just API