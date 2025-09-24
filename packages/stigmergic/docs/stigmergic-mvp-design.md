# Stigmergic Coordination MVP Design

## Executive Summary

This document captures our pragmatic, LLM-first approach to building stigmergic coordination. By leveraging LLM intelligence for all semantic evaluation and keeping signal spaces small and ephemeral, we can prove the core concepts without unnecessary complexity.

## Critical Design Decisions (Updated)

### 1. Signal as Minimal Abstract Interface

Following ClearFlow's successful pattern, `Signal` is an abstract base with only stigmergic essentials:

- **Required fields**: `id`, `emitter`, `timestamp`, `initialStrength` (initial emission strength)
- **NO prescribed content**: Users extend with domain-specific fields
- **NO forced "content" field**: Users choose natural names (`text` for chat, `ticker` for markets)
- **NO built-in types**: Users define what signal types mean in their domain

### 2. Environment Calculates Current Strength

In true stigmergic systems, signals don't control their own strength:

- **Signal carries**: Initial emission strength (`initialStrength`) set by emitter - immutable
- **SignalSpace computes**: Current strength `S(t)` based on decay + reinforcements
- **Any agent can reinforce**: Cumulative strength emerges from collective action
- **No owner control**: Once emitted, environment physics determines signal fate

This mirrors biology where pheromone evaporation/diffusion is environmental, not controlled by the ant that laid it.

### 3. MVP Scope Boundaries

**Include (Essential for stigmergic coordination):**

- Minimal Signal interface (4 fields)
- Basic age-based decay in SignalSpace
- Simple in-memory signal collection
- LLM-based relevance evaluation

**Defer (Post-MVP complexity):**

- Complex decay models (exponential, linear, custom)
- Reinforcement mechanisms
- Embedding vectors for semantic search
- Persistence/database layer
- Signal metadata field (reconsider if truly needed)

## Core Principles

### 1. Agents as LLM Proxies

Agents don't contain complex logic - they're thin wrappers that delegate all intelligence to LLMs:

- **Relevance evaluation**: LLM decides what signals matter
- **Action selection**: LLM chooses how to respond
- **Role discovery**: LLM determines specialization from experience
- **Goal decomposition**: LLM breaks down objectives

### 2. Relevance Over Attraction

We've moved beyond physical metaphors:

- **Not**: "Attraction" like ants to pheromones
- **But**: "Relevance" like developers to issues
- **Result**: Semantic understanding, not mathematical forces

### 3. Simplicity First

Start with the simplest thing that could work:

- In-memory signal spaces
- Brute-force LLM evaluation
- No persistence between sessions
- No complex algorithms

## MVP Architecture

### Lean Specification: Abstract Intelligence

The Lean specification captures the concept of "LLM-powered" without implementation details:

```lean
/-- Minimal signal properties for coordination.
    Users implement concrete signal types with domain-specific fields.
-/
class Signal (α : Type) where
  id : α → SignalId
  emitter : α → AgentId
  timestamp : α → Time
  initialStrength : α → NNReal  -- Initial strength when emitted (immutable)
  -- No prescribed content structure!

/-- Signal space manages environmental dynamics -/
structure SignalSpace where
  signals : List (Σ α, Signal α)
  currentTime : Time

  /-- Environment calculates current strength with decay -/
  getCurrentStrength (signalId : SignalId) (now : Time) : NNReal

  /-- Any agent can reinforce existing signals -/
  reinforce (signalId : SignalId) (amount : NNReal) (by : AgentId) : SignalSpace

/-- Abstract intelligence provider interface.
    Models external intelligence (LLM) without implementation details.
-/
structure IntelligenceProvider where
  /-- Evaluate relevance of a signal to a given role -/
  evaluateRelevance : Role → Signal → IO Float  -- Returns 0.0 to 1.0

  /-- Generate response to relevant signals -/
  generateResponse : Role → List Signal → IO (Option Signal)

  /-- Discover specialization from history -/
  discoverRole : List (Signal × Bool) → IO Role

/-- Agent with delegated intelligence.
    Key insight: Agent doesn't CONTAIN logic, it DELEGATES to intelligence.
-/
structure IntelligentAgent where
  id : AgentID
  role : Role  -- Can evolve through learning
  intelligence : IntelligenceProvider  -- External intelligence
  history : List (Signal × Bool)  -- For learning
  -- NO fixed threshold or attractedTypes!

/-- Agent observes space using intelligence -/
def IntelligentAgent.observe (agent : IntelligentAgent) (space : SignalSpace) : IO (List Signal) := do
  let allSignals := space.getAllSignals
  let mut relevant := []

  for signal in allSignals do
    -- Delegate relevance evaluation to intelligence
    let relevance ← agent.intelligence.evaluateRelevance agent.role signal
    if relevance > 0.5 then
      relevant := signal :: relevant

  return relevant

/-- Agent acts based on intelligence -/
def IntelligentAgent.act (agent : IntelligentAgent) (relevant : List Signal) : IO (Option Signal) :=
  agent.intelligence.generateResponse agent.role relevant

/-- Agent learns from outcomes -/
def IntelligentAgent.learn (agent : IntelligentAgent) : IO IntelligentAgent := do
  let newRole ← agent.intelligence.discoverRole agent.history
  return { agent with role := newRole }
```

### Key Abstraction Principles

1. **Intelligence as Interface**: `IntelligenceProvider` abstracts LLM capabilities
2. **No Fixed Parameters**: No thresholds, weights, or attraction lists
3. **Dynamic Evaluation**: Every decision delegated to intelligence
4. **Learning as Evolution**: Roles adapt based on experience
5. **Semantic Flexibility**: Signals are simple strings, not complex type hierarchies
6. **Convention Over Configuration**: Use "GOAL:", "CONSTRAINT:" prefixes, not types

### Properties We Can Still Prove

Even with external intelligence, Lean can verify:

- Agents only act on relevant signals
- Agent identity preserved through learning
- Causal relationship between observations and emissions
- No direct agent-to-agent communication (stigmergic property)

### Signal Space Design

```python
class SignalSpace:
    """Simple in-memory collection with environmental dynamics."""

    def __init__(self):
        self.signals: List[Signal] = []  # Just a list!
        self.max_size = 100  # Reasonable limit
        self.current_time = datetime.now()

    def emit(self, signal: Signal):
        """Add signal to space."""
        self.signals.append(signal)

    def get_current_strength(self, signal_id: str, now: datetime) -> float:
        """Environment calculates current strength with decay.

        This is where the "physics" of the stigmergic environment lives.
        Signal doesn't control its own decay - environment does.
        """
        signal = self._find_signal(signal_id)
        if not signal:
            return 0.0

        # Simple exponential decay for MVP
        age_seconds = (now - signal.timestamp).total_seconds()
        decay_factor = 0.5 ** (age_seconds / 3600)  # Half-life of 1 hour

        # Start with initial emission strength, apply decay
        return signal.initialStrength * decay_factor
        # Future: Add reinforcements here

    def get_all(self) -> List[Signal]:
        """Return all signals for LLM evaluation."""
        return self.signals
```

### Python Implementation: Abstract Signal Pattern

Following ClearFlow's pattern, the framework defines abstract base types that users extend:

```python
from abc import ABC, abstractmethod
from datetime import datetime

# stigmergic/core.py - Framework provides abstractions
class Signal(ABC):
    """Abstract base for all signals - users implement concrete types."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the signal."""
        pass

    @property
    @abstractmethod
    def emitter(self) -> str:
        """Agent that emitted this signal."""
        pass

    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        """When the signal was emitted."""
        pass

    @property
    @abstractmethod
    def initialStrength(self) -> float:
        """Initial strength when emitted (immutable)."""
        pass

    # No content field! Users define their own fields

# User code - extends Signal with domain-specific structure
from dataclasses import dataclass
from pydantic import Field

@dataclass(frozen=True)
class ChatMessage(Signal):
    """Chat-specific signal with natural field names."""
    id: str
    emitter: str
    timestamp: datetime
    initialStrength: float = 1.0  # Default initial strength
    text: str  # Domain-specific field name
    reply_to: Optional[str] = None

@dataclass(frozen=True)
class MarketAnalysis(Signal):
    """Market signal with rich structure for DSPy."""
    id: str
    emitter: str
    timestamp: datetime
    initialStrength: float  # Market confidence affects initial strength
    ticker: str = Field(description="Asset being analyzed")
    trend: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0)
    indicators: Dict[str, float]
    # No artificial "content" wrapper - fields ARE the content!

# DSPy signatures work directly with user's signal types
class AnalystSignature(dspy.Signature):
    """DSPy signature using strongly-typed signals."""
    market_signal: MarketAnalysis = dspy.InputField()
    response: MarketAnalysis = dspy.OutputField()

```

### DSPy Agent Implementation

```python
class StigmergicAgent(dspy.Module):
    """Agent that uses DSPy for intelligence with user's signal types."""

    def __init__(self, role: str):
        super().__init__()
        self.role = role

        # DSPy signatures work with user's concrete signal types
        self.evaluate = dspy.ChainOfThought(
            "role, signal -> is_relevant: bool, reasoning"
        )
        self.respond = dspy.ChainOfThought(
            "role, signals -> response"
        )

    def observe_and_act(self, space: SignalSpace) -> Optional[Signal]:
        """Evaluate signals and potentially respond."""

        for signal in space.get_all():
            # DSPy evaluates user's signal type
            decision = self.evaluate(role=self.role, signal=signal)

            if decision.is_relevant:
                # Generate response in user's signal type
                return self.respond(role=self.role, signals=[signal])

        return None

    def learn_from_outcomes(self, successes: List[Signal], failures: List[Signal]):
        """Agent learns what it's good at through LLM introspection."""

        # Use DSPy to discover specialization
        specialization = self.discover_specialization(
            interaction_history={
                "successes": [s.content for s in successes],
                "failures": [f.content for f in failures]
            }
        )

        # Update role based on discovered patterns
        self.role = specialization.specialized_role
        # No weight matrices or parameters to update!
```

### The Power of DSPy Integration

**Why DSPy instead of raw LLM calls:**

1. **Structured outputs**: Type-safe responses, not string parsing
2. **Optimization**: Can use DSPy's optimizers to improve performance
3. **Composability**: Chain multiple reasoning steps easily
4. **Traceability**: Built-in reasoning chains for debugging

**What DSPy replaces:**

- ❌ Similarity calculations → ✅ `evaluate_relevance`
- ❌ Attraction functions → ✅ `is_relevant: bool`
- ❌ Weight learning → ✅ `discover_specialization`
- ❌ Complex algorithms → ✅ Simple LLM calls

### Multiple Intelligence Providers

The beauty of the `IntelligenceProvider` abstraction is it supports ANY intelligence source:

```python
class HumanIntelligenceProvider:
    """Human-in-the-loop intelligence provider."""

    def __init__(self, human_id: str):
        self.human_id = human_id

    def evaluate_relevance(self, role: str, signal: Signal) -> float:
        """Ask human to evaluate relevance."""
        print(f"\n[{self.human_id}] Evaluate relevance for role '{role}':")
        print(f"Signal: {signal.content}")
        response = input("Relevance (0.0-1.0): ")
        return float(response)

    def generate_response(self, role: str, signals: List[Signal]) -> Optional[Signal]:
        """Ask human to generate response."""
        print(f"\n[{self.human_id}] Generate response for role '{role}':")
        for i, s in enumerate(signals):
            print(f"  {i+1}. {s.content}")

        response_type = input("Response type (or 'none' to skip): ")
        if response_type.lower() == 'none':
            return None

        response_content = input("Response content: ")
        return Signal(
            type=response_type,
            content=response_content,
            creator_id=f"{role} (human: {self.human_id})"
        )

    def discover_role(self, history: List[Tuple[Signal, bool]]) -> str:
        """Ask human to suggest role specialization."""
        print(f"\n[{self.human_id}] Based on history, suggest role specialization:")
        return input("New role: ")

class HybridIntelligenceProvider:
    """Combines LLM and human intelligence based on confidence."""

    def __init__(self, llm_provider, human_provider, confidence_threshold=0.7):
        self.llm = llm_provider
        self.human = human_provider
        self.threshold = confidence_threshold

    def evaluate_relevance(self, role: str, signal: Signal) -> float:
        """LLM evaluates first, escalates to human if uncertain."""
        llm_result = self.llm.evaluate_relevance(role, signal)

        # If LLM is uncertain (near 0.5), ask human
        if 0.4 < llm_result < 0.6:
            print(f"LLM uncertain ({llm_result:.2f}), escalating to human...")
            return self.human.evaluate_relevance(role, signal)

        return llm_result

    def generate_response(self, role: str, signals: List[Signal]) -> Optional[Signal]:
        """Try LLM first, escalate complex decisions to human."""
        # Check if this seems complex (multiple conflicting signals)
        if len(signals) > 3 or self._has_conflicts(signals):
            print("Complex decision detected, consulting human...")
            return self.human.generate_response(role, signals)

        return self.llm.generate_response(role, signals)

# Usage: Flexible agent creation
def create_agent(agent_id: str, role: str, intelligence_type: str):
    """Factory for creating agents with different intelligence sources."""

    if intelligence_type == "llm":
        provider = DSPyIntelligenceProvider()
    elif intelligence_type == "human":
        provider = HumanIntelligenceProvider(human_id=agent_id)
    elif intelligence_type == "hybrid":
        llm = DSPyIntelligenceProvider()
        human = HumanIntelligenceProvider(human_id=agent_id)
        provider = HybridIntelligenceProvider(llm, human)
    else:
        raise ValueError(f"Unknown intelligence type: {intelligence_type}")

    return PythonIntelligentAgent(agent_id, role, provider)

# Example: Mixed intelligence team
team = [
    create_agent("analyst_1", "market_analyst", "llm"),
    create_agent("supervisor", "risk_reviewer", "human"),  # Human oversight
    create_agent("trader", "executor", "hybrid"),  # LLM with human escalation
]
```

This enables powerful scenarios:

- **Quality control**: Human agents review critical decisions
- **Training**: Humans demonstrate, LLMs learn
- **Escalation**: LLMs handle routine, humans handle exceptions
- **Collaboration**: True human-AI teams working through signals

### Bridging Lean to Python

The Lean `IntelligenceProvider` interface maps directly to ANY implementation:

```python
class DSPyIntelligenceProvider:
    """Python implementation of Lean's IntelligenceProvider interface."""

    def __init__(self):
        # DSPy modules implement the abstract intelligence
        self.relevance_eval = dspy.ChainOfThought(
            "role, signal_content -> relevance_score: float, reasoning"
        )
        self.response_gen = dspy.ChainOfThought(
            "role, signals -> response_type, response_content"
        )
        self.role_discover = dspy.ChainOfThought(
            "successes, failures -> new_role, capabilities"
        )

    def evaluate_relevance(self, role: str, signal: Signal) -> float:
        """Implements IntelligenceProvider.evaluateRelevance"""
        result = self.relevance_eval(
            role=role,
            signal_content=signal.content
        )
        return result.relevance_score

    def generate_response(self, role: str, signals: List[Signal]) -> Optional[Signal]:
        """Implements IntelligenceProvider.generateResponse"""
        if not signals:
            return None

        result = self.response_gen(
            role=role,
            signals=[s.content for s in signals]
        )

        return Signal(
            type=result.response_type,
            content=result.response_content,
            creator_id=role
        )

    def discover_role(self, history: List[Tuple[Signal, bool]]) -> str:
        """Implements IntelligenceProvider.discoverRole"""
        successes = [s for s, success in history if success]
        failures = [s for s, success in history if not success]

        result = self.role_discover(
            successes=[s.content for s in successes],
            failures=[f.content for f in failures]
        )

        return result.new_role

# Usage: Bridge Lean spec to Python implementation
class PythonIntelligentAgent:
    """Python agent that follows the Lean specification."""

    def __init__(self, agent_id: str, initial_role: str):
        self.id = agent_id
        self.role = initial_role
        self.intelligence = DSPyIntelligenceProvider()  # Implements Lean interface
        self.history = []

    def observe(self, space: SignalSpace) -> List[Signal]:
        """Implements IntelligentAgent.observe from Lean spec."""
        relevant = []
        for signal in space.get_all():
            relevance = self.intelligence.evaluate_relevance(self.role, signal)
            if relevance > 0.5:  # Minimal filtering as in Lean
                relevant.append(signal)
        return relevant

    def act(self, relevant_signals: List[Signal]) -> Optional[Signal]:
        """Implements IntelligentAgent.act from Lean spec."""
        return self.intelligence.generate_response(self.role, relevant_signals)

    def learn(self):
        """Implements IntelligentAgent.learn from Lean spec."""
        self.role = self.intelligence.discover_role(self.history)
```

This architecture ensures:

1. **Lean spec defines the contract** (what agents must do)
2. **Python implements the contract** (how they do it with DSPy)
3. **Clean separation** between specification and implementation
4. **Verifiable properties** in Lean, intelligent behavior in Python

## Scale Assumptions

### What We're Optimizing For

| Dimension | MVP Target | Rationale |
|-----------|------------|-----------|
| Signals per session | 10-100 | Typical coordination tasks are bounded |
| Agents per session | 3-10 | Small teams are most effective |
| Session duration | Minutes to hours | Tasks complete, then space resets |
| Signal persistence | None (in-memory) | Each task starts fresh |
| LLM calls | O(agents × cycles) | Affordable at small scale |

### Real-World Examples

**Portfolio Analysis (30-40 signals)**

- Initial goal signal
- 3-4 market analysis signals
- 5-6 risk assessment signals
- 10-15 discussion/refinement signals
- 3-4 decision signals
- Final recommendation signal

**Code Review (20-50 signals)**

- PR description signal
- 5-10 issue identification signals
- 10-20 discussion signals
- 5-10 fix suggestion signals
- Approval signal

**Goal Decomposition (20-30 signals)**

- Main goal signal
- 5-8 subgoal signals
- 10-15 progress update signals
- 3-5 completion signals

## Why This Approach Works

### 1. LLM Context Windows Are Huge

- **GPT-4**: 128k tokens ≈ 100 pages of text
- **Claude**: 200k tokens ≈ 150 pages of text
- **100 signals**: ~10k tokens at most
- **Conclusion**: Can evaluate entire space in one call

### 2. Brute Force Is Fine at Small Scale

```python
# This is perfectly reasonable for 100 signals:
def find_relevant_signals(agent_role: str, all_signals: List[Signal]) -> List[Signal]:
    return llm.evaluate(f"""
        Your role: {agent_role}
        All signals: {json.dumps([s.to_dict() for s in all_signals])}

        Which signals are relevant to your role? Why?
        Return signal IDs with relevance scores.
    """)
```

### 3. Most Coordination Is Naturally Bounded

- **Code review**: Ends when PR is merged
- **Analysis**: Completes when decision is made
- **Goal achievement**: Finishes when goal is met
- **Key insight**: These don't need infinite memory

## Implementation Phases

### Phase 1: Core Stigmergic Loop (Week 1)

Build the minimal working system:

```python
class MinimalStigmergicSystem:
    def __init__(self):
        self.space = SignalSpace()
        self.agents = []

    def add_agent(self, role: str):
        self.agents.append(StigmergicAgent(role))

    def inject_goal(self, goal: str):
        self.space.emit(Signal(type="goal", content=goal))

    async def run_cycle(self):
        for agent in self.agents:
            # Each agent evaluates entire space
            relevant = await agent.evaluate_relevance(self.space)

            # Agent decides action based on relevant signals
            if relevant:
                response = await agent.decide_action(relevant)
                if response:
                    self.space.emit(response)
```

### Phase 2: Complete DSPy Integration (Week 2)

Implement the full set of DSPy modules for agent intelligence:

```python
import dspy

# Configure DSPy with your LLM
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4"))

class RelevanceEvaluator(dspy.Module):
    """Evaluates if a signal is relevant to an agent's role."""

    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(
            "role, signal_content, signal_type -> is_relevant: bool, confidence: float, reasoning"
        )

class ActionGenerator(dspy.Module):
    """Generates agent's response to relevant signals."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(
            "role, relevant_signals, goal_context -> action_type, action_content, priority"
        )

class RoleDiscoverer(dspy.Module):
    """Discovers agent's specialization from interaction history."""

    def __init__(self):
        super().__init__()
        self.discover = dspy.ChainOfThought(
            "success_patterns, failure_patterns, peer_roles -> specialization, capabilities, avoid_areas"
        )

# Complete agent using all DSPy modules
class DSPyStigmergicAgent(dspy.Module):
    """Full DSPy-powered agent implementation."""

    def __init__(self, initial_role: str):
        super().__init__()
        self.role = initial_role
        self.relevance_evaluator = RelevanceEvaluator()
        self.action_generator = ActionGenerator()
        self.role_discoverer = RoleDiscoverer()
        self.history = []

    def forward(self, signal_space: SignalSpace) -> Optional[Signal]:
        """Process signals and potentially emit response."""

        # Batch evaluate all signals for relevance
        relevant = []
        for signal in signal_space.get_all():
            eval_result = self.relevance_evaluator(
                role=self.role,
                signal_content=signal.content,
                signal_type=signal.type
            )
            if eval_result.is_relevant and eval_result.confidence > 0.5:
                relevant.append(signal)

        # Generate action if relevant signals exist
        if relevant:
            action = self.action_generator(
                role=self.role,
                relevant_signals=[s.content for s in relevant],
                goal_context=self._extract_goals(signal_space)
            )

            # Create and return new signal
            return Signal(
                type=action.action_type,
                content=action.action_content,
                creator_id=self.role,
                metadata={"priority": action.priority}
            )

        return None
```

### Phase 3: Goal-Driven Coordination (Week 3)

Implement goal decomposition and achievement:

```python
class GoalDecomposer(dspy.Module):
    """Break high-level goals into subgoals."""

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(
            "goal -> subgoals, dependencies, success_criteria"
        )

    def forward(self, goal: Signal) -> List[Signal]:
        result = self.decompose(goal=goal.content)
        return [
            Signal(
                type="subgoal",
                content=sg,
                metadata={"parent": goal.id}
            )
            for sg in result.subgoals
        ]
```

### Phase 4: Validation Examples (Week 4)

Port existing examples to stigmergic pattern:

- **Chat application** (human + LLM agents)
- Portfolio analysis via signals
- Multi-agent code review
- Collaborative document editing
- Distributed problem-solving

## Example: Stigmergic Chat

The chat example perfectly demonstrates the paradigm shift from prescribed flows to emergent coordination.

### ClearFlow Chat (Prescribed)

```
StartChat → UserNode → UserMessageReceived → AssistantNode → AssistantMessageReceived → UserNode (loop)
```

- Fixed alternation between user and assistant
- Messages consumed by nodes
- Breaks if you want multiple participants

### Stigmergic Chat (Emergent)

```python
# User extends Signal with chat-specific fields
@dataclass(frozen=True)
class ChatMessage(Signal):
    """Chat signal with natural field names - no forced 'content' field."""
    id: str
    emitter: str  # Who sent it
    timestamp: datetime
    initialStrength: float = 1.0  # Initial strength
    text: str  # Natural name for chat!
    reply_to: Optional[str] = None
    sentiment: Literal["greeting", "question", "answer", "farewell"] = "question"

# Rich signals for complex interactions
@dataclass(frozen=True)
class CodeReviewSignal(Signal):
    """Code review signal with structured fields for DSPy."""
    id: str
    emitter: str  # Reviewer ID
    timestamp: datetime
    initialStrength: float  # Severity affects initial strength
    file_path: str
    line_numbers: List[int]
    issue_type: Literal["bug", "style", "performance", "security"]
    severity: float = Field(ge=0.0, le=1.0)
    suggestion: str
    # All fields directly accessible - no parsing needed!

class ChatSpace:
    """Signal space for conversation."""
    def __init__(self):
        self.signals: List[ChatSignal] = []  # All messages persist!

    def emit(self, signal: ChatSignal):
        self.signals.append(signal)
        print(f"[{signal.sender}]: {signal.content}")

    def get_recent(self, limit: int = 10) -> List[ChatSignal]:
        """Get recent context for agents."""
        return self.signals[-limit:]

# Human and assistant are just agents with different intelligence
human_agent = StigmergicChatAgent("human", HumanIntelligenceProvider())
assistant_agent = StigmergicChatAgent("assistant", DSPyIntelligenceProvider())

# Coordination emerges from relevance evaluation
while running:
    # Human observes and may speak
    human_signal = await human_agent.observe_and_act(space)
    if human_signal:
        space.emit(human_signal)

    # Assistant observes and may respond
    if space.has_unanswered_signals():
        assistant_signal = await assistant_agent.observe_and_act(space)
        if assistant_signal:
            space.emit(assistant_signal)
```

### Key Advantages

1. **Natural Multi-Party Chat**: Just add more agents

   ```python
   agents = [human, assistant, expert, moderator]
   for agent in agents:
       signal = await agent.observe_and_act(space)
   ```

2. **Specialized Responses**: Agents respond based on relevance

   ```python
   math_assistant = Agent("math_helper", MathIntelligence())  # Responds to math
   code_assistant = Agent("code_helper", CodeIntelligence())  # Responds to code
   ```

3. **Persistent Context**: Full conversation history as signals

4. **Unified Human-AI Interface**: Humans and AIs coordinate identically

### MVP Specification Validation

✅ **Our MVP fully supports this use case:**

| Requirement | MVP Support | Implementation |
|------------|-------------|----------------|
| Small signal space | ✅ Chat typically <100 messages | In-memory list perfect |
| LLM evaluation | ✅ Assistant uses DSPy | `DSPyIntelligenceProvider` |
| Human participation | ✅ Human uses input() | `HumanIntelligenceProvider` |
| Relevance-based | ✅ Agents evaluate each signal | `evaluate_relevance()` |
| Emergent coordination | ✅ No prescribed flow | Agents observe and act |
| Mixed intelligence | ✅ Human + LLM agents | Same `IntelligenceProvider` interface |

The chat example proves our MVP design:

- **Simple**: ~200 lines of Python
- **Powerful**: Supports multi-party, mixed human-AI chat
- **Emergent**: No hardcoded conversation flow
- **Scalable**: Add agents without changing architecture

## Scaling Path (Future)

### When to Add Complexity

| Scale Trigger | Enhancement | Rationale |
|--------------|-------------|-----------|
| >1000 signals | Add vector embeddings | Enable similarity search |
| >10k signals | Use vector database | Efficient persistent storage |
| Multi-day sessions | Add persistence | Maintain context across time |
| >100 agents | Implement sharding | Partition signal space |
| High LLM costs | Add caching layer | Reuse relevance evaluations |

### Natural Evolution

1. **MVP**: List of signals, LLM evaluates all
2. **V2**: Add embeddings for pre-filtering
3. **V3**: Vector DB for similarity search
4. **V4**: Graph relationships for complex coordination

## Comparison with ClearFlow

Understanding how stigmergic coordination differs from traditional flow-based systems:

| Aspect | ClearFlow | Stigmergic Coordination |
|--------|-----------|-------------------------|
| **Routing** | Explicit paths defined | Emergent via relevance |
| **Messages** | Transient, passed between nodes | Persistent signals in space |
| **Coordination** | Prescribed by flow definition | Emerges from agent interactions |
| **Processing** | Nodes transform messages | Agents evaluate and emit signals |
| **Intelligence** | Logic in node implementations | LLM-driven semantic understanding |
| **Scaling** | Add more nodes to flow | Add more agents to space |
| **Failure handling** | Error paths in flow | Signals persist until handled |
| **Type safety** | Strong typing with classes | Flexible via LLM interpretation |

## What We're NOT Building (MVP)

### Avoiding Premature Optimization

- ❌ **Vector embeddings**: Not needed for 100 signals
- ❌ **Similarity calculations**: LLM handles semantic matching
- ❌ **Decay algorithms**: Sessions are short-lived
- ❌ **Persistence layer**: Each task starts fresh
- ❌ **Complex routing**: Agents find relevant signals themselves
- ❌ **Weight matrices**: LLM determines relevance dynamically

### Framework vs User Code Separation

- ❌ **Framework-defined signal types**: Users define their own
- ❌ **Prescribed content structure**: Users choose field names
- ❌ **Built-in goal/constraint types**: Users create domain-specific types
- ❌ **Forced "content" field**: Users name fields naturally
- ❌ **Schema in framework**: Schema belongs in user code

Example - Framework stays minimal:

```python
# Framework provides only abstract base:
class Signal(ABC):
    @property
    @abstractmethod
    def id(self) -> str: pass
    @property
    @abstractmethod
    def emitter(self) -> str: pass
    @property
    @abstractmethod
    def timestamp(self) -> datetime: pass

# Users create rich domain types:
@dataclass(frozen=True)
class PullRequestSignal(Signal):
    id: str
    emitter: str
    timestamp: datetime
    pr_number: int
    files_changed: List[str]
    review_status: Literal["pending", "approved", "changes_requested"]
    # Natural, domain-specific fields!

### Focusing on Core Value
- ✅ **Emergent coordination**: Prove it works
- ✅ **LLM intelligence**: Leverage semantic understanding
- ✅ **Safety properties**: Formal verification in Lean
- ✅ **Simple examples**: Show practical applications
- ✅ **Clear patterns**: Document coordination emergence

## Success Metrics

### MVP Goals
1. **Working system in 4 weeks**
2. **3+ example applications**
3. **<1000 lines of code** (excluding Lean specs)
4. **Zero infrastructure** (no databases, queues, etc.)
5. **Emergent coordination** (no central controller)

### Validation Criteria
- Agents successfully coordinate without direct communication
- Goals decompose and achieve through signal patterns
- System handles 10-100 signals efficiently
- LLM costs remain reasonable (<$1 per session)
- Examples demonstrate clear value

## Key Architecture Principles (Consolidated)

### Framework vs User Code Separation
Following ClearFlow's successful pattern:

**Framework Provides (Minimal abstractions):**
- `Signal` abstract base with 4 required fields
- `SignalSpace` with environmental dynamics (decay calculation)
- `IntelligenceProvider` interface for LLM/human/hybrid intelligence
- `Agent` that delegates all decisions to intelligence

**Users Provide (Domain specifics):**
- Concrete signal types extending abstract `Signal`
- Natural field names (`text`, `ticker`, `objective`)
- Domain-specific signal semantics
- DSPy integration if desired
- Intelligence provider implementations

### Biological Accuracy
Our design mirrors real stigmergic systems:
- **Initial emission**: Emitter sets `initialStrength` when broadcasting signal
- **Environmental decay**: SignalSpace calculates current strength (evaporation)
- **Collective reinforcement**: Any agent can strengthen signals (trail following)
- **No owner control**: Signal fate determined by environment, not emitter

### Why This Design Works
1. **Maximum flexibility**: Users define what signals mean in their domain
2. **Type safety**: Abstract base ensures required fields, users add rest
3. **Clean DSPy integration**: User's Pydantic models ARE signals
4. **True emergence**: No prescribed signal types or flows
5. **Biological fidelity**: Matches how real stigmergic systems work

## Design Rationale

### Why Simple Signals?
1. **LLMs understand semantics** - Don't need type systems to know "GOAL:" means goal
2. **Flexibility** - New signal patterns emerge without schema changes
3. **Simpler proofs** - One Signal type vs. complex type hierarchies
4. **True emergence** - Agents discover patterns, not follow predefined types
5. **No coupling** - Python doesn't need to match complex Lean types

### Why LLM-First?
1. **Semantic understanding** built-in
2. **No custom algorithms** to maintain
3. **Adaptive behavior** without coding
4. **Natural language** signals
5. **Immediate intelligence** vs. training time

### Why Small Spaces?
1. **Most tasks are bounded** in scope
2. **Easier to debug** and understand
3. **Lower costs** for LLM calls
4. **Faster development** without optimization
5. **Proves concept** before scaling

### Why No Persistence?
1. **Tasks complete** then disappear
2. **Fresh start** prevents accumulation
3. **Simpler testing** with clean slate
4. **No database** complexity
5. **Focus on coordination** not storage

## Conclusion

This MVP design prioritizes **proving stigmergic coordination works** over handling massive scale. By leveraging LLM intelligence and keeping spaces small and ephemeral, we can build a working system quickly and validate the core concepts. Once proven, we have a clear scaling path for applications that need it.

The key insight: **Most multi-agent coordination happens in bounded contexts with dozens, not millions, of signals.** Optimizing for this reality lets us build something useful immediately rather than over-engineering for hypothetical scale.
