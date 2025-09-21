"""Data models for Portfolio Manager."""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class AllocationChange:
    """Portfolio allocation adjustment."""

    symbol: str = Field(description="Asset symbol")
    current_weight: float = Field(description="Current portfolio weight", ge=0, le=100)
    new_weight: float = Field(description="New portfolio weight", ge=0, le=100)
    action: Literal["buy", "sell", "hold", "rebalance"] = Field(description="Action type")


@dataclass(frozen=True)
class ExpectedOutcome:
    """Expected portfolio outcome metric."""

    metric: str = Field(description="Metric name")
    value: float = Field(description="Expected value")


@dataclass(frozen=True)
class PortfolioRecommendations:
    """Portfolio optimization recommendations."""

    allocation_changes: Sequence[AllocationChange] = Field(description="Recommended allocation adjustments")
    rebalancing_urgency: Literal["immediate", "gradual", "conditional"] = Field(description="Execution timeline")
    expected_return: float = Field(description="Expected annual return percentage")
    expected_volatility: float = Field(description="Expected portfolio volatility")
    rationale: str = Field(description="Investment thesis")
