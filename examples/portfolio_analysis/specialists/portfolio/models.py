"""Data models for Portfolio Manager."""

from collections.abc import Mapping
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class AllocationChange:
    """Individual portfolio allocation recommendation."""

    symbol: str = Field(description="Asset symbol")
    current_allocation: float = Field(ge=0, le=100, description="Current portfolio percentage")
    recommended_allocation: float = Field(ge=0, le=100, description="Recommended portfolio percentage")
    change_reason: str = Field(description="Rationale for change")
    priority: Literal["high", "medium", "low"] = Field(description="Implementation priority")


@dataclass(frozen=True)
class PortfolioRecommendations:
    """Stage 4: Portfolio manager's strategic decisions."""

    allocation_changes: tuple[AllocationChange, ...] = Field(description="Recommended allocation adjustments")
    investment_thesis: str = Field(min_length=50, description="Strategic investment thesis")
    execution_timeline: Literal["immediate", "gradual", "conditional"] = Field(
        description="Recommended execution approach"
    )
    expected_outcomes: Mapping[str, str] = Field(
        description="Projected outcomes by metric, e.g., {'expected_return': '12.5%', 'sharpe_ratio': '1.8', 'max_drawdown': '8%'}"
    )
    manager_summary: str = Field(max_length=500, description="Portfolio manager summary")
