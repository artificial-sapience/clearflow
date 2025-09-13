"""Event-driven message types for portfolio analysis.

Pure event-driven architecture with single initiating command.
Events describe outcomes, not instructions.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from clearflow import Command, Event
from examples.portfolio_analysis.shared.models import MarketData
from examples.portfolio_analysis_message_driven.specialists.compliance.models import ComplianceReview
from examples.portfolio_analysis_message_driven.specialists.decision.models import TradingDecision
from examples.portfolio_analysis_message_driven.specialists.portfolio.models import PortfolioRecommendations
from examples.portfolio_analysis_message_driven.specialists.quant.models import QuantInsights
from examples.portfolio_analysis_message_driven.specialists.risk.models import RiskAssessment

# ============================================================================
# PORTFOLIO CONSTRAINTS
# ============================================================================


@dataclass(frozen=True, kw_only=True)
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
    Contains: Complete LLM-generated quantitative insights
    """

    # Complete LLM response - no manual extraction
    insights: QuantInsights

    # Context for next stage
    market_data: MarketData  # Original data for downstream nodes
    constraints: PortfolioConstraints  # Constraints to propagate


@dataclass(frozen=True, kw_only=True)
class RiskAssessedEvent(Event):
    """Event when risk assessment is complete.

    Published by: RiskAnalystNode
    Contains: Complete LLM-generated risk assessment
    """

    # Complete LLM response - no manual extraction
    assessment: RiskAssessment

    # Context for next stage
    market_data: MarketData
    constraints: PortfolioConstraints
    insights: QuantInsights  # Pass through for downstream access


@dataclass(frozen=True, kw_only=True)
class RecommendationsGeneratedEvent(Event):
    """Event when portfolio recommendations are ready.

    Published by: PortfolioManagerNode
    Contains: Complete LLM-generated portfolio recommendations
    """

    # Complete LLM response - no manual extraction
    recommendations: PortfolioRecommendations

    # Context for compliance
    assessment: RiskAssessment  # Pass through from previous stage
    constraints: PortfolioConstraints


@dataclass(frozen=True, kw_only=True)
class ComplianceReviewedEvent(Event):
    """Event when compliance review is complete.

    Published by: ComplianceOfficerNode
    Contains: Complete LLM-generated compliance review
    """

    # Complete LLM response - no manual extraction
    review: ComplianceReview

    # Context for decision
    recommendations: PortfolioRecommendations  # Pass through from previous stage
    constraints: PortfolioConstraints


@dataclass(frozen=True, kw_only=True)
class DecisionMadeEvent(Event):
    """Event when final trading decision is made.

    Published by: DecisionMakerNode
    Contains: Complete LLM-generated trading decision
    """

    # Complete LLM response - no manual extraction
    decision: TradingDecision

    # Context for execution (failure cases may not have these)
    review: ComplianceReview | None = None  # May be None for failure cases


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
    partial_results: Mapping[str, float | str | int] | None  # Any partial results available
    can_retry: bool  # Whether retry might succeed
    fallback_action: Literal["hold", "escalate"]  # Suggested fallback

    # Original context for recovery
    market_data: MarketData | None
    constraints: PortfolioConstraints | None
