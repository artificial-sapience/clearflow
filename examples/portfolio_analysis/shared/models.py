"""Shared data models used across agents."""

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

# Type aliases for consistent validation
NodeName = Literal[
    "QuantAnalystNode",
    "RiskAnalystNode",
    "PortfolioManagerNode",
    "ComplianceOfficerNode",
    "DecisionMakerNode",
]

ErrorType = Literal[
    "ValidationError",
    "APIError",
    "TimeoutError",
    "DataError",
    "LimitExceeded",
]


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
    market_date: str = Field(description="Date of market data snapshot in ISO-8601 format (YYYY-MM-DD)")
    risk_free_rate: float = Field(ge=0, le=0.1, description="Current risk-free rate")
    market_sentiment: Literal["bullish", "bearish", "neutral"] = Field(description="Overall market sentiment")


@dataclass(frozen=True)
class AnalysisError:
    """Error state when analysis fails."""

    error_type: ErrorType = Field(description="Type of error encountered (validated against ErrorType literal)")
    error_message: str = Field(description="Detailed error message for debugging")
    failed_stage: NodeName = Field(description="Node name where error occurred (validated against NodeName literal)")
    market_data: MarketData | None = Field(default=None, description="Original input for retry")
