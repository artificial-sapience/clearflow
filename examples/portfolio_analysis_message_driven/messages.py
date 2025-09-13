"""Event-driven message types for portfolio analysis.

Pure event-driven architecture with single initiating command.
Events describe outcomes, not instructions.
"""

from dataclasses import dataclass
from typing import Literal

from clearflow import Command, Event
from examples.portfolio_analysis.shared.models import MarketData


# ============================================================================
# PORTFOLIO CONSTRAINTS
# ============================================================================


@dataclass(frozen=True)
class PortfolioConstraints:
    """Constraints for portfolio optimization."""

    max_position_size: float = 15.0  # Maximum % allocation per asset
    max_sector_allocation: float = 40.0  # Maximum % per sector
    min_position_size: float = 2.0  # Minimum % if position taken
    max_var_limit: float = 2_000_000.0  # Maximum Value at Risk
    max_drawdown_threshold: float = 0.20  # Maximum acceptable drawdown


# ============================================================================
# SINGLE INITIATING COMMAND
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class StartAnalysisCommand(Command):
    """Initiate portfolio analysis with complete market context.

    This is the only command in the system. All subsequent messages are events.
    """

    market_data: MarketData
    portfolio_constraints: PortfolioConstraints


# ============================================================================
# EVENTS - Represent outcomes of processing
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class MarketAnalyzedEvent(Event):
    """Event when quantitative market analysis is complete.

    Published by: QuantAnalystNode
    Contains: Market opportunities identified through LLM analysis
    """

    # Core analysis results
    market_trend: Literal["bullish", "bearish", "sideways"]
    opportunities: tuple[str, ...]  # Asset symbols identified as opportunities
    opportunity_scores: tuple[float, ...]  # Confidence scores (0-1) for each
    sector_momentum: dict[str, float]  # Sector momentum scores (-1 to 1)

    # Context for next stage
    market_data: MarketData  # Original data for downstream nodes
    constraints: PortfolioConstraints  # Constraints to propagate

    # Analysis metadata
    analysis_confidence: float  # Overall confidence in analysis (0-1)
    analysis_summary: str  # Brief LLM-generated summary


@dataclass(frozen=True, kw_only=True)
class RiskAssessedEvent(Event):
    """Event when risk assessment is complete.

    Published by: RiskAnalystNode
    Contains: Risk-adjusted opportunities with position limits
    """

    # Risk-adjusted opportunities
    acceptable_symbols: tuple[str, ...]  # Symbols passing risk thresholds
    risk_scores: tuple[float, ...]  # Risk score (0-1) for each symbol
    max_position_sizes: tuple[float, ...]  # Max % allocation per symbol

    # Portfolio risk metrics
    portfolio_var: float  # Value at Risk estimate
    max_drawdown_estimate: float  # Estimated maximum drawdown
    overall_risk_level: Literal["low", "medium", "high"]

    # Context for next stage
    market_data: MarketData
    constraints: PortfolioConstraints
    sector_momentum: dict[str, float]  # From market analysis

    # Risk metadata
    risk_summary: str  # LLM-generated risk assessment


@dataclass(frozen=True, kw_only=True)
class RecommendationsGeneratedEvent(Event):
    """Event when portfolio recommendations are ready.

    Published by: PortfolioManagerNode
    Contains: Specific allocation recommendations
    """

    # Allocation recommendations
    allocations: dict[str, float]  # Symbol -> % allocation
    actions: dict[str, Literal["buy", "sell", "hold"]]  # Symbol -> action

    # Portfolio metrics
    expected_return: float  # Annualized expected return
    expected_volatility: float  # Annualized expected volatility
    sharpe_ratio: float  # Risk-adjusted return metric

    # Reasoning
    allocation_rationale: dict[str, str]  # Symbol -> reasoning

    # Context for compliance
    risk_metrics: dict[str, float]  # Risk scores per symbol
    constraints: PortfolioConstraints

    # Confidence
    confidence_level: float  # Overall confidence (0-1)


@dataclass(frozen=True, kw_only=True)
class ComplianceReviewedEvent(Event):
    """Event when compliance review is complete.

    Published by: ComplianceOfficerNode
    Contains: Approved allocations with any required adjustments
    """

    # Compliance results
    approved_allocations: dict[str, float]  # Compliant allocations
    rejected_symbols: tuple[str, ...]  # Symbols rejected for compliance
    compliance_adjustments: dict[str, str]  # Symbol -> adjustment reason

    # Compliance status
    compliance_status: Literal["approved", "conditional", "rejected"]
    violations_found: tuple[str, ...]  # List of violations if any

    # Final portfolio metrics
    final_allocations: dict[str, float]  # Ready for execution
    sector_allocations: dict[str, float]  # Sector exposure check

    # Context for decision
    original_recommendations: dict[str, float]  # Before adjustments
    constraints: PortfolioConstraints


@dataclass(frozen=True, kw_only=True)
class DecisionMadeEvent(Event):
    """Event when final trading decision is made.

    Published by: DecisionMakerNode
    Contains: Final executable trading decision
    """

    # Final decision
    decision: Literal["execute", "hold", "escalate"]
    final_allocations: dict[str, float]  # Symbol -> % allocation

    # Execution details
    trade_orders: tuple[tuple[str, Literal["buy", "sell"], float], ...]  # (symbol, action, amount)
    estimated_impact: float  # Estimated portfolio impact %

    # Decision rationale
    decision_reasoning: str  # LLM-generated explanation
    risk_acknowledgments: tuple[str, ...]  # Acknowledged risks

    # Metadata
    confidence: float  # Decision confidence (0-1)
    requires_human_review: bool  # Flag for manual review


@dataclass(frozen=True, kw_only=True)
class AnalysisFailedEvent(Event):
    """Event when any analysis stage fails.

    Published by: Any node encountering an error
    Routes to: DecisionMakerNode for conservative handling
    """

    failed_stage: str  # Which node failed
    error_type: str  # Type of error (e.g., "ValidationError", "OpenAIError")
    error_message: str  # Detailed error message

    # Recovery context
    partial_results: dict[str, any] | None  # Any partial results available
    can_retry: bool  # Whether retry might succeed
    fallback_action: Literal["hold", "escalate"]  # Suggested fallback

    # Original context for recovery
    market_data: MarketData | None
    constraints: PortfolioConstraints | None