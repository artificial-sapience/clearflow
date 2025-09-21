"""Message types for portfolio analysis.

Message-driven architecture with single initiating command.
Events describe outcomes, not instructions.
"""

from collections.abc import Mapping
from typing import Literal

from pydantic import Field

from clearflow import Command, Event, StrictBaseModel
from examples.portfolio_analysis.shared.models import ErrorType, MarketData, NodeName
from examples.portfolio_analysis.specialists.compliance.models import ComplianceReview
from examples.portfolio_analysis.specialists.decision.models import TradingDecision
from examples.portfolio_analysis.specialists.portfolio.models import PortfolioRecommendations
from examples.portfolio_analysis.specialists.quant.models import QuantInsights
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment

# ============================================================================
# PORTFOLIO CONSTRAINTS
# ============================================================================


class PortfolioConstraints(StrictBaseModel):
    """Risk and allocation limits for portfolio optimization.

    Defines hard constraints that the AI must respect when generating
    portfolio recommendations, ensuring compliance with risk management
    policies and regulatory requirements.

    Used by:
    - Risk analysts to validate exposure limits
    - Portfolio managers to guide allocation decisions
    - Compliance officers to enforce regulatory boundaries
    """

    max_position_size: float = Field(
        default=15.0,
        ge=0,
        le=100,
        description="Maximum percentage allocation allowed for any single asset position (0-100%)",
    )
    max_sector_allocation: float = Field(
        default=40.0,
        ge=0,
        le=100,
        description="Maximum percentage of portfolio allowed in any single sector (0-100%)",
    )
    min_position_size: float = Field(
        default=2.0,
        ge=0,
        le=100,
        description="Minimum percentage allocation if a position is taken, avoids dust positions (0-100%)",
    )
    max_var_limit: float = Field(
        default=2_000_000.0,
        gt=0,
        description="Maximum Value at Risk in dollars for 95% confidence interval (must be positive)",
    )
    max_drawdown_threshold: float = Field(
        default=0.20,
        ge=0,
        le=1,
        description="Maximum acceptable portfolio drawdown as decimal (0.0-1.0, where 0.20 = 20% loss tolerance)",
    )


# ============================================================================
# SINGLE INITIATING COMMAND
# ============================================================================


class StartAnalysisCommand(Command):
    """Command to initiate multi-specialist portfolio analysis workflow.

    Triggers a cascade of AI-powered analysis through quantitative,
    risk, portfolio management, and compliance specialists. This is the
    only command - all subsequent messages are events representing completed analyses.

    Design pattern:
    - Single command initiates the workflow
    - Events capture specialist conclusions
    - Type-based routing orchestrates the analysis pipeline
    """

    market_data: MarketData = Field(description="Current market conditions, prices, and indicators for analysis")
    portfolio_constraints: PortfolioConstraints = Field(
        description="Risk limits and allocation constraints that all recommendations must respect"
    )


# ============================================================================
# EVENTS - Represent outcomes of processing
# ============================================================================


class MarketAnalyzedEvent(Event):
    """Event containing completed quantitative market analysis.

    Generated after the Quant Analyst AI evaluates market conditions,
    containing structured insights about trends, signals, and opportunities.

    Published by: QuantAnalystNode
    Consumed by: RiskAnalystNode

    Analysis includes:
    - Technical indicators and signals
    - Market regime identification
    - Statistical arbitrage opportunities
    - Quantitative factor exposures
    """

    insights: QuantInsights = Field(
        description="AI-generated quantitative analysis including signals, correlations, and opportunities"
    )
    market_data: MarketData = Field(description="Original market data passed through for downstream analysis stages")
    constraints: PortfolioConstraints = Field(
        description="Portfolio constraints propagated for use in subsequent analysis nodes"
    )


class RiskAssessedEvent(Event):
    """Event containing comprehensive risk evaluation results.

    Generated after the Risk Analyst AI evaluates portfolio risks,
    containing metrics, scenarios, and risk mitigation recommendations.

    Published by: RiskAnalystNode
    Consumed by: PortfolioManagerNode

    Risk analysis covers:
    - Value at Risk calculations
    - Stress testing scenarios
    - Correlation risk assessment
    - Tail risk evaluation
    """

    assessment: RiskAssessment = Field(
        description="AI-generated risk analysis including VaR, scenarios, and risk warnings"
    )
    market_data: MarketData = Field(description="Market data for portfolio manager's allocation decisions")
    constraints: PortfolioConstraints = Field(description="Risk constraints to enforce in portfolio construction")
    insights: QuantInsights = Field(
        description="Quantitative insights passed through for portfolio optimization context"
    )


class RecommendationsGeneratedEvent(Event):
    """Event containing strategic portfolio allocation recommendations.

    Generated after the Portfolio Manager AI synthesizes quant and risk
    analyses into actionable allocation changes and investment strategy.

    Published by: PortfolioManagerNode
    Consumed by: ComplianceOfficerNode

    Recommendations include:
    - Specific allocation changes
    - Investment thesis rationale
    - Execution timeline strategy
    - Expected outcome projections
    """

    recommendations: PortfolioRecommendations = Field(
        description="AI-generated portfolio changes including allocations, thesis, and execution plan"
    )
    assessment: RiskAssessment = Field(description="Risk assessment passed through for compliance validation context")
    constraints: PortfolioConstraints = Field(description="Constraints for compliance verification of recommendations")


class ComplianceReviewedEvent(Event):
    """Event containing regulatory and policy compliance validation.

    Generated after the Compliance Officer AI reviews recommendations
    against regulatory requirements and internal policies.

    Published by: ComplianceOfficerNode
    Consumed by: DecisionMakerNode

    Compliance checks include:
    - Regulatory requirement validation
    - Internal policy adherence
    - Concentration limit verification
    - Restricted list screening
    """

    review: ComplianceReview = Field(
        description="AI-generated compliance validation with pass/fail status and required actions"
    )
    recommendations: PortfolioRecommendations = Field(
        description="Portfolio recommendations passed through for final decision context"
    )
    constraints: PortfolioConstraints = Field(description="Constraints used in compliance validation for audit trail")


class DecisionMadeEvent(Event):
    """Terminal event containing final trading decision and execution instructions.

    Generated as the culmination of the analysis pipeline, containing
    the synthesized decision ready for execution or manual review.

    Published by: DecisionMakerNode
    Terminal type: Ends the analysis flow

    Decision includes:
    - Proceed/hold determination
    - Specific trades if proceeding
    - Confidence level assessment
    - Execution instructions
    """

    decision: TradingDecision = Field(
        description="AI-synthesized final decision with specific trades or hold rationale"
    )
    review: ComplianceReview | None = Field(
        default=None, description="Compliance review if available (None for early-stage failures)"
    )


class AnalysisFailedEvent(Event):
    """Event signaling analysis pipeline failure requiring conservative action.

    Generated when any specialist node encounters an unrecoverable error,
    triggering fail-safe handling to protect portfolio from uncertain conditions.

    Published by: Any specialist node on error
    Routes to: DecisionMakerNode for conservative response

    Failure handling:
    - Captures failure context for debugging
    - Preserves partial results when available
    - Suggests appropriate fallback action
    - Maintains audit trail for compliance
    """

    failed_stage: NodeName = Field(
        description="Specialist node name where failure occurred (validated against NodeName literal)"
    )
    error_type: ErrorType = Field(description="Error classification (validated against ErrorType literal)")
    error_message: str = Field(description="Detailed error description for logging and potential recovery")
    partial_results: Mapping[str, float | str | int] | None = Field(
        description="Partial metrics before failure, e.g., {'var': 1500000.0, 'max_drawdown': 0.15, 'positions_analyzed': 5}"
    )
    can_retry: bool = Field(description="Whether the error is transient and retry might succeed")
    fallback_action: Literal["hold", "escalate"] = Field(
        description="Recommended conservative action: hold positions or escalate to human"
    )
    market_data: MarketData | None = Field(
        description="Original market data if available for context in decision making"
    )
    constraints: PortfolioConstraints | None = Field(
        description="Portfolio constraints if available for fail-safe decision logic"
    )
