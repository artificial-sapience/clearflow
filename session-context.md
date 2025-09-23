# Session Context: From ClearFlow to Stigmergic Coordination

## Journey Overview

We explored how to transform ClearFlow's message-driven orchestration into a stigmergic coordination system where intelligent agents coordinate through environmental traces rather than explicit routing.

## Key Conceptual Insights

### What is a Flow?
- At the deepest level: **A constraint algebra over asynchronous computation**
- In ClearFlow: Explicit routing tables defining message paths
- In Stigmergic: Emergent patterns from environmental modifications

### Goals, Plans, and Agendas
- **Plans**: Hypotheses about causality (rigid, prescriptive)
- **Strategies**: Heuristics for navigating possibility space (adaptive)
- **Agendas**: Negotiated sequences of attention (our TODO lists)
- **Goals in Stigmergy**: Persistent environmental gradients that attract agents

### Stigmergy as Universal Principle
- Not just ants - Wikipedia, open source, markets, cities all use stigmergy
- Core: **Coordination through persistent environmental modification**
- Mathematical foundation: Field theory for distributed cognition

## Technical Design Decisions

### MVP Architecture (100 lines of Python)
Three fundamental capabilities:
1. **Traces**: Persistent messages in environment
2. **Attraction**: Agents finding relevant traces (start with keywords, grow to embeddings)
3. **Action**: DSPy-powered processing and trace emission

### Addressing Peer Review Challenges
1. **Computational Cost**: Tiered observation (filter ’ score ’ evaluate)
2. **Feedback**: Explicit success/failure traces
3. **Control**: Progressive autonomy levels
4. **Cold Start**: Begin with defined roles, let specialization emerge

### Technology Stack
- **DSPy**: For structured LLM intelligence ("program, not prompt")
- **Vector DB**: ChromaDB/Pinecone for semantic search
- **Embeddings**: OpenAI text-embedding-3-small
- **Persistence**: PostgreSQL with pgvector extension

## Current State

### Created Artifacts
1. `docs/stigmergic-coordination-theory.md` - Complete theory and MVP implementation
2. `docs/stigmergy-as-universal-coordination.md` - Why this path matters
3. `docs/plans-todos-and-cognitive-modes.md` - Understanding different coordination tools
4. `docs/flow-as-grammar-not-plan.md` - Flows as constraint systems
5. `docs/goals-strategies-and-flows.md` - Complex outcome achievement
6. `spec/StigmergicCoordination.lean` - Formal specification in Lean4

### Key Code Example
The minimal viable system that can replace ClearFlow is captured in the MVP section of `stigmergic-coordination-theory.md`, using just Trace, Environment, and StigmergicAgent classes with DSPy.

## Next Steps
See `plan.md` for detailed implementation phases. The immediate priority is building the MVP that demonstrates stigmergic coordination replacing a simple ClearFlow workflow.

## Important Context
- We're building on existing stigmergic work (TorchSNN, TorchSM by Galatolo)
- The system should grow from simple (keyword matching) to complex (full autonomy)
- Focus on practical, measurable progress over theoretical perfection
- Use DSPy throughout for structured, optimizable intelligence