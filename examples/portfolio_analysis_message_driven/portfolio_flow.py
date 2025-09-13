"""Portfolio analysis flow using message-driven architecture."""

from clearflow import MessageFlow, message_flow
from examples.portfolio_analysis_message_driven.messages import (
    AnalysisFailedEvent,
    AnalyzeMarketCommand,
    AssessRiskCommand,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    GenerateRecommendationsCommand,
    MakeDecisionCommand,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    ReviewComplianceCommand,
    RiskAssessedEvent,
)
from examples.portfolio_analysis_message_driven.nodes import (
    ComplianceOfficerNode,
    DecisionMakerNode,
    PortfolioManagerNode,
    QuantAnalystNode,
    RiskAnalystNode,
)
from examples.portfolio_analysis_message_driven.orchestrators import (
    PrepareComplianceReviewNode,
    PrepareDecisionNode,
    PrepareRecommendationsNode,
    PrepareRiskAssessmentNode,
)


def create_portfolio_analysis_flow() -> MessageFlow[AnalyzeMarketCommand, DecisionMadeEvent]:
    """Create the portfolio analysis workflow with message-driven architecture.

    This flow demonstrates:
    - Multi-specialist workflow with focused messages
    - No god-objects in events (each message has single responsibility)
    - Orchestrator nodes that transform messages between specialists
    - Error handling that routes to final decision

    Flow sequence:
    1. QuantAnalyst analyzes market → MarketAnalyzedEvent
    2. Orchestrator prepares risk command → AssessRiskCommand
    3. RiskAnalyst assesses risk → RiskAssessedEvent
    4. Orchestrator prepares recommendation command → GenerateRecommendationsCommand
    5. PortfolioManager generates recommendations → RecommendationsGeneratedEvent
    6. Orchestrator prepares compliance command → ReviewComplianceCommand
    7. ComplianceOfficer reviews → ComplianceReviewedEvent
    8. Orchestrator prepares decision command → MakeDecisionCommand
    9. DecisionMaker makes final decision → DecisionMadeEvent

    Error handling:
    - Any AnalysisFailedEvent routes directly to DecisionMaker
    - DecisionMaker handles errors with conservative "HOLD" decision

    Returns:
        MessageFlow that processes market analysis commands into trading decisions.

    """
    # Create specialist nodes
    quant = QuantAnalystNode()
    risk = RiskAnalystNode()
    portfolio = PortfolioManagerNode()
    compliance = ComplianceOfficerNode()
    decision = DecisionMakerNode()

    # Create orchestrator nodes
    prep_risk = PrepareRiskAssessmentNode()
    prep_recommendations = PrepareRecommendationsNode()
    prep_compliance = PrepareComplianceReviewNode()
    prep_decision = PrepareDecisionNode()

    # Build the flow with explicit message routing
    return (
        message_flow("PortfolioAnalysis", quant)
        # Quant analysis outcomes
        .from_node(quant)
        .route(MarketAnalyzedEvent, prep_risk)
        .route(AnalysisFailedEvent, decision)
        # Risk assessment preparation
        .from_node(prep_risk)
        .route(AssessRiskCommand, risk)
        # Risk analysis outcomes
        .from_node(risk)
        .route(RiskAssessedEvent, prep_recommendations)
        .route(AnalysisFailedEvent, decision)
        # Recommendation preparation
        .from_node(prep_recommendations)
        .route(GenerateRecommendationsCommand, portfolio)
        # Portfolio management outcomes
        .from_node(portfolio)
        .route(RecommendationsGeneratedEvent, prep_compliance)
        .route(AnalysisFailedEvent, decision)
        # Compliance preparation
        .from_node(prep_compliance)
        .route(ReviewComplianceCommand, compliance)
        # Compliance review outcomes
        .from_node(compliance)
        .route(ComplianceReviewedEvent, prep_decision)
        .route(AnalysisFailedEvent, decision)
        # Decision preparation
        .from_node(prep_decision)
        .route(MakeDecisionCommand, decision)
        # Final decision (single termination)
        .from_node(decision)
        .end(DecisionMadeEvent)
    )
