"""Focused message types for portfolio analysis avoiding god-objects.

Each message has single responsibility and contains only essential data.
"""

from dataclasses import dataclass
from typing import Literal

from clearflow import Command, Event

# ============================================================================
# COMMANDS - Initiate work
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class AnalyzeMarketCommand(Command):
    """Command to start market analysis with specific assets."""

    asset_symbols: tuple[str, ...]
    market_sentiment: Literal["bullish", "bearish", "neutral"]
    risk_free_rate: float
    market_date: str


@dataclass(frozen=True, kw_only=True)
class AssessRiskCommand(Command):
    """Command to assess risk for specific opportunities."""

    opportunity_symbols: tuple[str, ...]
    confidence_scores: tuple[float, ...]
    market_volatility: float


@dataclass(frozen=True, kw_only=True)
class GenerateRecommendationsCommand(Command):
    """Command to generate portfolio recommendations."""

    acceptable_symbols: tuple[str, ...]
    risk_scores: tuple[float, ...]
    target_allocations: tuple[float, ...]


@dataclass(frozen=True, kw_only=True)
class ReviewComplianceCommand(Command):
    """Command to review recommendations for compliance."""

    recommended_changes: tuple[tuple[str, float, float], ...]  # (symbol, current, recommended)
    risk_exposure: float


@dataclass(frozen=True, kw_only=True)
class MakeDecisionCommand(Command):
    """Command to make final trading decision."""

    approved_symbols: tuple[str, ...]
    approved_allocations: tuple[float, ...]
    compliance_status: Literal["approved", "conditional", "rejected"]


# ============================================================================
# EVENTS - Represent outcomes
# ============================================================================


@dataclass(frozen=True, kw_only=True)
class MarketAnalyzedEvent(Event):
    """Event when market analysis is complete."""

    identified_opportunities: tuple[str, ...]
    opportunity_scores: tuple[float, ...]
    market_trend: Literal["bullish", "bearish", "sideways"]
    analysis_confidence: float


@dataclass(frozen=True, kw_only=True)
class RiskAssessedEvent(Event):
    """Event when risk assessment is complete."""

    acceptable_symbols: tuple[str, ...]
    risk_scores: tuple[float, ...]
    max_position_sizes: tuple[float, ...]
    overall_risk_level: Literal["low", "medium", "high"]


@dataclass(frozen=True, kw_only=True)
class RecommendationsGeneratedEvent(Event):
    """Event when portfolio recommendations are ready."""

    recommended_actions: tuple[Literal["buy", "sell", "hold"], ...]
    action_symbols: tuple[str, ...]
    allocation_changes: tuple[float, ...]  # Percentage point changes
    confidence_level: float


@dataclass(frozen=True, kw_only=True)
class ComplianceReviewedEvent(Event):
    """Event when compliance review is complete."""

    approved_symbols: tuple[str, ...]
    rejected_symbols: tuple[str, ...]
    compliance_notes: tuple[str, ...]
    requires_escalation: bool


@dataclass(frozen=True, kw_only=True)
class DecisionMadeEvent(Event):
    """Event when final trading decision is made."""

    execution_plan: str
    approved_trades: tuple[tuple[str, str, float], ...]  # (symbol, action, amount)
    decision_status: Literal["execute", "hold", "escalate"]
    monitoring_required: bool


@dataclass(frozen=True, kw_only=True)
class AnalysisFailedEvent(Event):
    """Event when any analysis step fails."""

    failed_stage: str
    error_type: str
    error_message: str
    can_retry: bool
