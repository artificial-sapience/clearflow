"""Data models for Risk Analyst."""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ConcentrationRisk:
    """Risk concentration for a sector or asset."""

    identifier: str = Field(description="Sector or asset ID")
    percentage: float = Field(description="Risk concentration percentage", ge=0.0, le=100.0)


@dataclass(frozen=True)
class StressTestResult:
    """Result of a stress test scenario."""

    scenario: str = Field(description="Scenario name")
    pnl_impact: float = Field(description="Profit/loss impact in dollars")


@dataclass(frozen=True)
class RiskAssessment:
    """Risk analysis of portfolio allocations."""

    portfolio_var: float = Field(description="Value at Risk in dollars", gt=0)
    sharpe_ratio: float = Field(description="Risk-adjusted return metric")
    risk_level: Literal["low", "medium", "high", "extreme"] = Field(description="Overall risk classification")
    concentration_risks: Sequence[ConcentrationRisk] = Field(description="Risk concentrations by sector or asset")
    stress_tests: Sequence[StressTestResult] = Field(description="Stress test scenario results")
