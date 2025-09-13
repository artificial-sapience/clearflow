# Message-Driven Portfolio Analysis Example

Multi-specialist financial analysis using focused messages without god-objects.

## Key Design: Avoiding God-Objects

This example demonstrates how to avoid god-objects in events by using focused, single-responsibility messages:

### ❌ BAD: God-Object Pattern (Not Used)
```python
# DON'T DO THIS - Too much data in one event
@dataclass
class AnalysisCompleteEvent(Event):
    market_data: MarketData           # Full input data
    quant_insights: QuantInsights     # Full quant analysis
    risk_assessment: RiskAssessment   # Full risk analysis
    recommendations: Recommendations  # Full recommendations
    compliance: ComplianceReport      # Full compliance review
    # This event knows too much!
```

### ✅ GOOD: Focused Messages (Used Here)
```python
# Each message has single responsibility
@dataclass
class MarketAnalyzedEvent(Event):
    identified_opportunities: tuple[str, ...]  # Just symbols
    opportunity_scores: tuple[float, ...]      # Just scores
    market_trend: Literal["bullish", "bearish", "sideways"]
    analysis_confidence: float
    # Focused on market analysis outcome only

@dataclass
class RiskAssessedEvent(Event):
    acceptable_symbols: tuple[str, ...]  # Just approved symbols
    risk_scores: tuple[float, ...]       # Just risk scores
    max_position_sizes: tuple[float, ...]
    overall_risk_level: Literal["low", "medium", "high"]
    # Focused on risk assessment outcome only
```

## Architecture Overview

```
AnalyzeMarketCommand → [QuantAnalyst] → MarketAnalyzedEvent
                                              ↓
                        [Orchestrator] → AssessRiskCommand
                                              ↓
                          [RiskAnalyst] → RiskAssessedEvent
                                              ↓
                        [Orchestrator] → GenerateRecommendationsCommand
                                              ↓
                      [PortfolioManager] → RecommendationsGeneratedEvent
                                              ↓
                        [Orchestrator] → ReviewComplianceCommand
                                              ↓
                     [ComplianceOfficer] → ComplianceReviewedEvent
                                              ↓
                        [Orchestrator] → MakeDecisionCommand
                                              ↓
                       [DecisionMaker] → DecisionMadeEvent
```

## Key Components

### Messages (Single Responsibility)
- **Commands**: Initiate specific work with minimal data
- **Events**: Report specific outcomes without excess context

### Specialist Nodes
- **QuantAnalystNode**: Identifies market opportunities
- **RiskAnalystNode**: Assesses risk for opportunities
- **PortfolioManagerNode**: Generates allocation recommendations
- **ComplianceOfficerNode**: Reviews for compliance
- **DecisionMakerNode**: Makes final trading decision

### Orchestrator Nodes
Transform events into commands for next specialist:
- **PrepareRiskAssessment**: MarketAnalyzedEvent → AssessRiskCommand
- **PrepareRecommendations**: RiskAssessedEvent → GenerateRecommendationsCommand
- **PrepareComplianceReview**: RecommendationsGeneratedEvent → ReviewComplianceCommand
- **PrepareDecision**: ComplianceReviewedEvent → MakeDecisionCommand

## Running the Example

```bash
# From clearflow directory
python -m examples.portfolio_analysis_message_driven.main

# Or run directly
cd examples/portfolio_analysis_message_driven
python main.py
```

## Benefits of This Approach

1. **Single Responsibility**: Each message does one thing well
2. **Loose Coupling**: Specialists don't need to know about each other's internals
3. **Testability**: Each node can be tested with focused inputs
4. **Maintainability**: Changes to one specialist don't ripple through system
5. **Event Sourcing**: Natural audit trail of decisions

## Comparison with Legacy Approach

### Legacy (Node-Flow-State)
- Passes entire state objects between nodes
- State accumulates data as it flows
- Nodes see more than they need

### Message-Driven (This Example)
- Passes focused messages between nodes
- Each message contains only essential data
- Nodes see only what they need to know