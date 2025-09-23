"""Data models for Quantitative Analyst."""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class MarketSignal:
    """Individual market signal for a specific asset."""

    symbol: str = Field(description="Asset symbol")
    signal: Literal["buy", "sell", "hold"] = Field(description="Trading signal")
    strength: float = Field(description="Signal strength", ge=0.0, le=1.0)


@dataclass(frozen=True)
class QuantInsights:
    """Quantitative analysis insights from market data."""

    market_trend: Literal["bullish", "bearish", "neutral"] = Field(description="Overall market trend assessment")
    confidence: float = Field(description="Confidence in the analysis", ge=0.0, le=1.0)
    top_signals: Sequence[MarketSignal] = Field(description="Top trading signals identified")
    volatility_index: float = Field(description="Market volatility index", ge=0.0, le=100.0)
