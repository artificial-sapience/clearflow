"""Data models for Compliance Officer."""

from collections.abc import Sequence
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ComplianceViolation:
    """Compliance rule violation."""

    rule: str = Field(description="Rule identifier")
    severity: Literal["warning", "violation", "critical"] = Field(description="Violation severity")
    details: str = Field(description="Violation details")


@dataclass(frozen=True)
class ComplianceReview:
    """Regulatory compliance assessment."""

    all_checks_passed: bool = Field(description="Whether all compliance checks passed")
    violations: Sequence[ComplianceViolation] = Field(description="Compliance violations found")
    approval_status: Literal["approved", "conditional", "rejected"] = Field(description="Compliance approval status")
    required_disclosures: Sequence[str] = Field(description="Required regulatory disclosures")
