"""Type-safe financial data models using Pydantic dataclasses for validation."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass


# Stage 1: Market Data Input
@dataclass(frozen=True)
class AssetData:
    """Individual asset market data."""

    symbol: str = Field(description="Asset ticker symbol")
    price: float = Field(gt=0, description="Current asset price")
    volume: int = Field(ge=0, description="Trading volume")
    volatility: float = Field(ge=0, le=1, description="30-day volatility as decimal")
    momentum: float = Field(ge=-1, le=1, description="Price momentum indicator")
    sector: str = Field(description="Industry sector classification")


@dataclass(frozen=True)
class MarketData:
    """Stage 1: Raw market data input for analysis."""

    assets: tuple[AssetData, ...] = Field(description="List of assets to analyze")
    market_date: str = Field(description="Date of market data snapshot")
    risk_free_rate: float = Field(ge=0, le=0.1, description="Current risk-free rate")
    market_sentiment: Literal["bullish", "bearish", "neutral"] = Field(
        description="Overall market sentiment"
    )


# Stage 2: Quantitative Analysis Results
@dataclass(frozen=True)
class OpportunitySignal:
    """Individual investment opportunity identified by quant analysis."""

    symbol: str = Field(description="Asset symbol for this opportunity")
    signal_type: Literal["buy", "sell", "hold"] = Field(description="Trading signal")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    target_allocation: float = Field(
        ge=0, le=100, description="Recommended portfolio percentage"
    )
    reasoning: str = Field(description="Rationale for this signal")


@dataclass(frozen=True)
class QuantInsights:
    """Stage 2: Quantitative analysis insights and opportunities."""

    market_trend: Literal["bullish", "bearish", "sideways"] = Field(
        description="Overall market trend assessment"
    )
    sector_analysis: dict[str, float] = Field(
        description="Sector momentum scores (-1 to 1)"
    )
    opportunities: tuple[OpportunitySignal, ...] = Field(
        description="Identified trading opportunities"
    )
    overall_confidence: float = Field(
        ge=0, le=1, description="Overall analysis confidence"
    )
    analysis_summary: str = Field(
        max_length=500, description="Brief summary of analysis"
    )

    @field_validator("sector_analysis")
    @classmethod
    def validate_sector_scores(cls, v: dict[str, float]) -> dict[str, float]:
        """Ensure sector scores are within valid range.
        
        Returns:
            Validated sector scores dictionary.
            
        Raises:
            ValueError: If any sector score is outside [-1, 1] range.
        """
        for sector, score in v.items():
            if not -1 <= score <= 1:
                msg = f"{cls.__name__}: Sector score for {sector} must be between -1 and 1"
                raise ValueError(msg)
        return v


# Stage 3: Risk Assessment
@dataclass(frozen=True)
class RiskMetrics:
    """Portfolio risk calculations."""

    value_at_risk: float = Field(gt=0, description="Value at Risk (VaR) in dollars")
    max_drawdown: float = Field(
        ge=0, le=1, description="Maximum potential loss as decimal"
    )
    concentration_risk: dict[str, float] = Field(
        description="Risk concentration by sector/asset"
    )
    correlation_warning: bool = Field(description="Flag for high correlation issues")


@dataclass(frozen=True)
class RiskAssessment:
    """Stage 3: Risk analysis of quantitative recommendations."""

    risk_metrics: RiskMetrics = Field(description="Calculated risk metrics")
    risk_level: Literal["low", "medium", "high", "extreme"] = Field(
        description="Overall risk classification"
    )
    stress_test_results: dict[str, float] = Field(
        description="Scenario analysis outcomes"
    )
    risk_warnings: tuple[str, ...] = Field(
        description="Specific risk concerns identified"
    )
    risk_summary: str = Field(max_length=500, description="Risk analysis summary")


# Stage 4: Portfolio Management Decisions
@dataclass(frozen=True)
class AllocationChange:
    """Individual portfolio allocation recommendation."""

    symbol: str = Field(description="Asset symbol")
    current_allocation: float = Field(
        ge=0, le=100, description="Current portfolio percentage"
    )
    recommended_allocation: float = Field(
        ge=0, le=100, description="Recommended portfolio percentage"
    )
    change_reason: str = Field(description="Rationale for change")
    priority: Literal["high", "medium", "low"] = Field(
        description="Implementation priority"
    )


@dataclass(frozen=True)
class PortfolioRecommendations:
    """Stage 4: Portfolio manager's strategic decisions."""

    allocation_changes: tuple[AllocationChange, ...] = Field(
        description="Recommended allocation adjustments"
    )
    investment_thesis: str = Field(
        min_length=50, description="Strategic investment thesis"
    )
    execution_timeline: Literal["immediate", "gradual", "conditional"] = Field(
        description="Recommended execution approach"
    )
    expected_outcomes: dict[str, str] = Field(
        description="Expected returns, risks, and other outcomes"
    )
    manager_summary: str = Field(
        max_length=500, description="Portfolio manager summary"
    )


# Stage 5: Compliance Review
@dataclass(frozen=True)
class ComplianceCheck:
    """Individual compliance validation."""

    rule_name: str = Field(description="Compliance rule identifier")
    status: Literal["pass", "fail", "warning"] = Field(
        description="Compliance check result"
    )
    details: str = Field(description="Specific details about the check")


@dataclass(frozen=True)
class ComplianceReview:
    """Stage 5: Regulatory and policy compliance validation."""

    compliance_checks: tuple[ComplianceCheck, ...] = Field(
        description="Individual compliance validations"
    )
    overall_status: Literal["approved", "rejected", "conditional"] = Field(
        description="Overall compliance decision"
    )
    regulatory_notes: tuple[str, ...] = Field(
        description="Regulatory considerations and notes"
    )
    compliance_summary: str = Field(
        max_length=400, description="Compliance review summary"
    )


# Stage 6: Final Trading Decision
@dataclass(frozen=True)
class TradingDecision:
    """Stage 6: Final approved portfolio decision."""

    approved_changes: tuple[AllocationChange, ...] = Field(
        description="Final approved allocation changes"
    )
    execution_plan: str = Field(description="Detailed execution instructions")
    monitoring_requirements: tuple[str, ...] = Field(
        description="Ongoing monitoring needs"
    )
    audit_trail: str = Field(description="Complete decision reasoning chain")
    decision_status: Literal["execute", "hold", "escalate"] = Field(
        description="Final decision status"
    )


# Error States
@dataclass(frozen=True)
class AnalysisError:
    """Error state when analysis fails."""

    error_type: str = Field(description="Type of error encountered")
    error_message: str = Field(description="Detailed error message")
    failed_stage: str = Field(description="Stage where error occurred")
    market_data: MarketData | None = Field(
        default=None, description="Original input for retry"
    )


@dataclass(frozen=True)
class RiskLimitError:
    """Error state when risk limits are exceeded."""

    exceeded_limits: tuple[str, ...] = Field(description="List of exceeded risk limits")
    risk_metrics: RiskMetrics = Field(description="Current risk metrics")
    recommendations: tuple[str, ...] = Field(description="Risk mitigation suggestions")
    failed_stage: str = Field(description="Stage where limit was exceeded")


@dataclass(frozen=True)
class ComplianceError:
    """Error state when compliance checks fail."""

    violations: tuple[ComplianceCheck, ...] = Field(
        description="Compliance violations found"
    )
    required_actions: tuple[str, ...] = Field(
        description="Actions required for compliance"
    )
    escalation_required: bool = Field(description="Whether escalation is needed")
    failed_stage: str = Field(description="Stage where compliance failed")
