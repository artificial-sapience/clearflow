"""Portfolio analysis flow using message-driven architecture.

Direct message-to-node routing without orchestrators.
The flow definition is the single source of routing truth.
"""

from clearflow import Node, create_flow
from examples.portfolio_analysis.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)
from examples.portfolio_analysis.nodes import (
    ComplianceOfficerNode,
    DecisionMakerNode,
    PortfolioManagerNode,
    QuantAnalystNode,
    RiskAnalystNode,
)
from examples.portfolio_analysis.portfolio_observer import PortfolioAnalysisObserver


def create_portfolio_analysis_flow() -> Node[StartAnalysisCommand, DecisionMadeEvent]:
    """Create the portfolio analysis workflow with message-driven architecture.

    This flow demonstrates:
    - Single initiating command (StartAnalysisCommand)
    - Events describe outcomes, not instructions
    - Direct node routing without orchestrators
    - Each node reads what it needs from events
    - Error handling routes failures to decision maker
    - Built-in console output for visibility

    Flow sequence:
    1. StartAnalysisCommand → QuantAnalyst
    2. MarketAnalyzedEvent → RiskAnalyst
    3. RiskAssessedEvent → PortfolioManager
    4. RecommendationsGeneratedEvent → ComplianceOfficer
    5. ComplianceReviewedEvent → DecisionMaker
    6. Any AnalysisFailedEvent → DecisionMaker (conservative handling)

    Returns:
        MessageFlow that processes market analysis into trading decisions.

    """
    # Create specialist nodes (no orchestrators needed)
    quant = QuantAnalystNode()
    risk = RiskAnalystNode()
    portfolio = PortfolioManagerNode()
    compliance = ComplianceOfficerNode()
    decision = DecisionMakerNode()

    # Create portfolio-specific observer for rich output
    observer = PortfolioAnalysisObserver()

    # Build the flow with portfolio-specific observer
    return (
        create_flow("PortfolioAnalysis", quant)
        .observe(observer)
        # Quant analysis outcomes
        .route(quant, MarketAnalyzedEvent, risk)  # Success → Risk assessment
        .route(quant, AnalysisFailedEvent, decision)  # Failure → Conservative decision
        # Risk analysis outcomes
        .route(risk, RiskAssessedEvent, portfolio)  # Success → Portfolio optimization
        .route(risk, AnalysisFailedEvent, decision)  # Failure → Conservative decision
        # Portfolio management outcomes
        .route(portfolio, RecommendationsGeneratedEvent, compliance)  # Success → Compliance review
        .route(portfolio, AnalysisFailedEvent, decision)  # Failure → Conservative decision
        # Compliance review outcomes
        .route(compliance, ComplianceReviewedEvent, decision)  # Success → Final decision
        .route(compliance, AnalysisFailedEvent, decision)  # Failure → Conservative decision
        # Final decision (terminal type)
        .end_flow(DecisionMadeEvent)  # Flow terminates with DecisionMadeEvent
    )
