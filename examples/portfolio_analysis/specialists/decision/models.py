"""Data models for Trading Decision."""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange


@dataclass(frozen=True)
class TradingDecision:
    """Final trading decision and execution plan."""

    decision_status: Literal["approved", "rejected", "conditional"] = Field(description="Decision status")
    approved_changes: Sequence[AllocationChange] = Field(description="Approved allocation changes")
    execution_instructions: Sequence[str] = Field(description="Execution instructions")
    risk_warnings: Sequence[str] = Field(description="Risk warnings to monitor")
