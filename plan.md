# Portfolio Analysis Message-Driven Example: Complete Implementation Plan

## Executive Summary

Transform the portfolio_analysis_message_driven example from a broken random-logic simulation into a production-quality, event-driven system with real LLM intelligence using DSPy and OpenAI.

## Current State Analysis

### Critical Issues

1. **Lost LLM Intelligence**: Using `secrets.SystemRandom()` instead of DSPy/OpenAI
2. **Command-Driven Coupling**: 5 Command types + 4 orchestrator nodes create unnecessary complexity
3. **Quality Violations**: 30+ DOC201, BLE001, RUF022, and other violations
4. **Architecture Misalignment**: Not following ClearFlow's event-driven philosophy

### Assets Already Copied

- `shared/` directory with DSPy config and models
- `specialists/*/` directories with signatures and validators
- `market_data.py` with data models
- `.env.example` for OpenAI configuration

## Architecture Design Specification

### Core Principle: Pure Event-Driven Architecture

**Philosophy**: Events describe what happened, not what should happen next. The flow definition is the sole orchestrator.

### Message Types (Simplified)

```python
# Single initiating command
@dataclass(frozen=True, kw_only=True)
class StartAnalysisCommand(Command):
    """Initiate portfolio analysis with market data."""
    market_data: MarketData  # Complete market context
    portfolio_constraints: PortfolioConstraints  # Risk limits, position limits

# Events represent outcomes only
MarketAnalyzedEvent      # Quant completed analysis
RiskAssessedEvent        # Risk completed assessment
RecommendationsGeneratedEvent  # Portfolio manager completed
ComplianceReviewedEvent  # Compliance completed review
DecisionMadeEvent        # Final decision completed
AnalysisFailedEvent      # Any stage failed
```

### Node Architecture

Each node:

1. Receives previous event (or initial command)
2. Extracts needed data
3. Calls DSPy with proper signature
4. Publishes outcome event

```python
@dataclass(frozen=True)
class QuantAnalystNode(MessageNode[StartAnalysisCommand | MarketData, MarketAnalyzedEvent | AnalysisFailedEvent]):
    name: str = "quant_analyst"
    _predictor: dspy.Predict = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "_predictor", dspy.Predict(QuantAnalystSignature))

    async def process(self, message):
        # Use DSPy for real LLM intelligence
        prediction = self._predictor(market_data=message.market_data)
        return MarketAnalyzedEvent(...)
```

### Flow Definition (No Orchestrators)

```python
flow = (
    message_flow("PortfolioAnalysis", quant)
    .from_node(quant)
    .route(MarketAnalyzedEvent, risk)  # Direct routing
    .route(AnalysisFailedEvent, decision)
    .from_node(risk)
    .route(RiskAssessedEvent, portfolio)
    .route(AnalysisFailedEvent, decision)
    # ... continue pattern
)
```

## Detailed Implementation Tasks

### Phase 1: Refactor to Event-Driven Architecture

#### Task 1.1: Redesign Messages

- [ ] Create new `messages.py` with simplified structure
- [ ] Define `StartAnalysisCommand` with complete market data
- [ ] Update all Events to carry necessary data for next nodes
- [ ] Remove intermediate Command types (AssessRisk, GenerateRecommendations, etc.)
- [ ] Add proper type hints and docstrings

#### Task 1.2: Remove Orchestrators

- [ ] Delete `orchestrators.py` entirely
- [ ] Document data flow requirements for each transition
- [ ] Ensure events carry all needed context

#### Task 1.3: Update Flow Definition

- [ ] Rewrite `portfolio_flow.py` with direct event�node routing
- [ ] Remove all orchestrator node references
- [ ] Simplify flow to ~50 lines (from current 100+)
- [ ] Add comprehensive docstring explaining flow

### Phase 2: Integrate DSPy and LLM Intelligence

#### Task 2.1: Configure DSPy

- [ ] Update `main.py` to call `configure_dspy()` at startup
- [ ] Add error handling for missing API key
- [ ] Set up proper model parameters (gpt-5-nano-2025-08-07)
- [ ] Test configuration with simple DSPy call

#### Task 2.2: Implement QuantAnalystNode with DSPy

- [ ] Import DSPy signature from `specialists/quant/signature.py`
- [ ] Initialize DSPy predictor in `__post_init__`
- [ ] Replace random logic with `dspy.Predict()` call
- [ ] Map MarketData to DSPy inputs
- [ ] Extract structured outputs to MarketAnalyzedEvent
- [ ] Handle OpenAI errors gracefully

#### Task 2.3: Implement RiskAnalystNode with DSPy

- [ ] Import DSPy signature from `specialists/risk/signature.py`
- [ ] Process MarketAnalyzedEvent data
- [ ] Use DSPy for risk assessment
- [ ] Generate RiskAssessedEvent with real risk scores
- [ ] Include proper error handling

#### Task 2.4: Implement PortfolioManagerNode with DSPy

- [ ] Import DSPy signature from `specialists/portfolio/signature.py`
- [ ] Process RiskAssessedEvent data
- [ ] Use DSPy for portfolio optimization
- [ ] Generate RecommendationsGeneratedEvent
- [ ] Ensure allocations sum to d100%

#### Task 2.5: Implement ComplianceOfficerNode with DSPy

- [ ] Import DSPy signature from `specialists/compliance/signature.py`
- [ ] Process RecommendationsGeneratedEvent
- [ ] Use DSPy for compliance review
- [ ] Generate ComplianceReviewedEvent
- [ ] Handle violation escalation logic

#### Task 2.6: Implement DecisionMakerNode with DSPy

- [ ] Import DSPy signature from `specialists/decision/signature.py`
- [ ] Process ComplianceReviewedEvent or AnalysisFailedEvent
- [ ] Use DSPy for final decision
- [ ] Generate DecisionMadeEvent
- [ ] Implement conservative fallback for errors

### Phase 3: Quality and Compliance

#### Task 3.1: Fix Documentation (DOC201)

- [ ] Add "Returns" sections to all function docstrings
- [ ] Use proper format: "Returns:\n    Type: Description"
- [ ] Ensure all async functions document return types
- [ ] Update class docstrings with complete descriptions

#### Task 3.2: Fix Exception Handling (BLE001)

- [ ] Replace all blind `except Exception` with specific types
- [ ] Catch `ValidationError`, `OpenAIError`, `ValueError`, `TypeError`
- [ ] Add proper error messages
- [ ] Ensure all errors create AnalysisFailedEvent

#### Task 3.3: Fix Import Order (RUF022)

- [ ] Sort all `__all__` lists alphabetically
- [ ] Use absolute imports everywhere
- [ ] Group imports: stdlib, third-party, local
- [ ] Remove any unused imports

#### Task 3.4: Pass Quality Checks

- [ ] Run `./quality-check.sh` and fix all violations
- [ ] Ensure 100% test coverage
- [ ] Pass pyright strict mode
- [ ] No suppression comments without approval

### Phase 4: Testing and Validation

#### Task 4.1: Create Integration Test

- [ ] Write `test_integration.py` with real OpenAI calls
- [ ] Test complete flow from start to decision
- [ ] Verify each node produces expected event types
- [ ] Test error paths (API failures, invalid data)

#### Task 4.2: Create Example Runner

- [ ] Update `main.py` with realistic market data
- [ ] Add command-line argument parsing
- [ ] Include timing and performance metrics
- [ ] Add visual output formatting

#### Task 4.3: Documentation

- [ ] Create README.md explaining the example
- [ ] Document DSPy integration approach
- [ ] Provide setup instructions for OpenAI API
- [ ] Include example output from real run

## Success Criteria

1. **Architecture**: Pure event-driven with single initiating command
2. **LLM Integration**: Real DSPy/OpenAI calls, no random simulation
3. **Quality**: Zero violations from `./quality-check.sh`
4. **Functionality**: Complete flow executes with actual LLM responses
5. **Maintainability**: Clear, simple code following ClearFlow patterns

## Session Progress Tracking

### Session 1 (Current)

- [x] Analyzed architecture issues
- [x] Copied DSPy integration files
- [x] Created comprehensive plan
- [ ] Begin Phase 1 implementation

### Session 2 (Next)

- [ ] Complete Phase 1 (Event-driven refactor)
- [ ] Begin Phase 2 (DSPy integration)

### Session 3 (Future)

- [ ] Complete Phase 2 (All nodes with DSPy)
- [ ] Complete Phase 3 (Quality compliance)
- [ ] Complete Phase 4 (Testing)

## Key Files to Modify

1. `messages.py` - Simplify to event-driven
2. `nodes.py` - Add DSPy integration
3. `portfolio_flow.py` - Remove orchestrators
4. `main.py` - Add DSPy configuration
5. Delete: `orchestrators.py`

## Dependencies

- DSPy (already in pyproject.toml)
- OpenAI (via DSPy)
- python-dotenv (for .env loading)
- Pydantic (for structured outputs)

## Risk Mitigation

1. **API Key Missing**: Provide clear error with setup instructions
2. **Rate Limits**: Add retry logic with exponential backoff
3. **Model Changes**: Use configurable model name
4. **Type Safety**: Ensure all DSPy outputs validate through Pydantic

## Notes for Future Sessions

- Always check this plan first for context
- Run `./quality-check.sh` before any commits
- Test with real OpenAI API, not mocks
- Maintain event-driven philosophy throughout
- Keep messages focused (no god-objects)
- Document all design decisions in code
