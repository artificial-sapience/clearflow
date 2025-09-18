# Portfolio Analysis Example (Message-Driven)

Multi-specialist workflow for portfolio allocation decisions using event-driven architecture with real LLM intelligence.

## Flow

```mermaid
graph LR
    Start([Market Data]) --> Q[QuantAnalyst]
    Q -->|MarketAnalyzedEvent| R[RiskAnalyst]
    Q -->|AnalysisFailedEvent| D[DecisionMaker]
    R -->|RiskAssessedEvent| P[PortfolioManager]
    R -->|AnalysisFailedEvent| D
    P -->|RecommendationsGeneratedEvent| C[ComplianceOfficer]
    P -->|AnalysisFailedEvent| D
    C -->|ComplianceReviewedEvent| D
    C -->|AnalysisFailedEvent| D
    D -->|DecisionMadeEvent| End([Final Decision])
```

## Quick Start

```bash
# From project root directory

# 1. Set up your OpenAI API key
cp .env.example .env
# Edit .env and add your API key

# 2. Install dependencies
uv sync --all-extras

# 3. Run the example
cd examples/portfolio_analysis_message_driven
python main.py  # If venv is activated
# Or: uv run python main.py
```

## How It Works

This example demonstrates a pure event-driven workflow where each specialist node analyzes data and publishes events describing outcomes:

1. **QuantAnalyst** - Analyzes market data using LLM, publishes opportunities found
2. **RiskAnalyst** - Assesses risk using LLM, publishes acceptable positions
3. **PortfolioManager** - Optimizes portfolio using LLM, publishes recommendations
4. **ComplianceOfficer** - Reviews compliance using LLM, publishes approved allocations
5. **DecisionMaker** - Makes final decision using LLM, publishes executable orders

Each node uses DSPy for structured LLM outputs with comprehensive error handling.

## Key Features

- **Pure event-driven** - Single command starts flow, all subsequent messages are events
- **LLM intelligence** - Real OpenAI/DSPy integration, not simulated logic
- **Type-safe messages** - Immutable dataclasses with Mapping types
- **Error recovery** - AnalysisFailedEvent routes to DecisionMaker for conservative handling
- **No orchestrators** - Direct event routing, flow definition is the sole orchestrator
- **Observable** - Compatible with ClearFlow's Observer pattern (no console logging in nodes)

## Architecture Principles

### Event-Driven Design
- **Single initiating command**: `StartAnalysisCommand` contains all initial context
- **Events describe outcomes**: Past-tense naming (MarketAnalyzedEvent, not AnalyzeMarketEvent)
- **No intermediate commands**: Events flow directly between nodes
- **Explicit routing**: Flow definition specifies all event routes

### Message Design (No God-Objects)
```python
# ✅ GOOD: Focused events with single responsibility
@dataclass(frozen=True)
class MarketAnalyzedEvent(Event):
    opportunities: tuple[str, ...]  # Just symbols identified
    opportunity_scores: tuple[float, ...]  # Confidence scores
    market_trend: Literal["bullish", "bearish", "sideways"]
    # Context for next stage
    market_data: MarketData
    constraints: PortfolioConstraints

# ❌ BAD: God-object with too much data
class AnalysisCompleteEvent(Event):
    all_analysis_data: dict  # Everything in one place
    full_market_data: MarketData
    complete_insights: QuantInsights
    # Too much responsibility!
```

## Files

- `main.py` - Entry point with DSPy configuration and scenario selection
- `portfolio_flow.py` - Pure event-driven flow definition (no orchestrators)
- `messages.py` - Focused event types with immutable Mapping fields
- `nodes.py` - Specialist nodes with DSPy predictors (no console logging)
- `market_data.py` - Market data generation for different scenarios
- `specialists/` - DSPy signatures and models for each specialist

## Comparison with Legacy Approach

### Legacy (Node-Flow-State)
- Accumulates state as it flows
- Nodes mutate shared state
- Implicit data dependencies

### Message-Driven (This Example)
- Events carry only essential data
- Nodes produce new events without mutation
- Explicit data flow via messages