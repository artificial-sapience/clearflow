"""Regulatory compliance validators for portfolio analysis.

This module contains ONLY hard-coded regulatory requirements that cannot be violated.
All other risk assessment and recommendations are handled by AI intelligence.
"""

from examples.portfolio_analysis.config import ComplianceRules
from examples.portfolio_analysis.models_pydantic import (
    AllocationChange,
    ComplianceCheck,
)

# Constants
MAX_TOTAL_ALLOCATION = 100.0  # Maximum total portfolio allocation percentage


def validate_position_limits(
    allocation_changes: tuple[AllocationChange, ...],
) -> ComplianceCheck:
    """Check regulatory position limits.

    Args:
        allocation_changes: Proposed allocation changes

    Returns:
        ComplianceCheck with position limit status
    """
    violations = [
        change.symbol
        for change in allocation_changes
        if change.recommended_allocation > ComplianceRules.POSITION_LIMIT
    ]

    if violations:
        return ComplianceCheck(
            rule_name="position_limits",
            status="fail",
            details=f"Position limit exceeded for: {', '.join(violations)}",
        )

    return ComplianceCheck(
        rule_name="position_limits",
        status="pass",
        details="All positions within regulatory limits",
    )


def validate_sector_concentration(
    allocation_changes: tuple[AllocationChange, ...],
) -> ComplianceCheck:
    """Check regulatory sector concentration limits.

    Args:
        allocation_changes: Proposed allocation changes

    Returns:
        ComplianceCheck with sector concentration status
    """
    # Simplified sector mapping for demo
    sectors = {
        "Technology": {"NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN"},
        "Finance": {"JPM", "BAC", "GS", "MS", "WFC"},
    }

    for sector_name, symbols in sectors.items():
        total = sum(
            change.recommended_allocation
            for change in allocation_changes
            if change.symbol in symbols
        )

        if total > ComplianceRules.SECTOR_LIMIT:
            return ComplianceCheck(
                rule_name="sector_concentration",
                status="fail",
                details=f"{sector_name} sector exceeds {ComplianceRules.SECTOR_LIMIT}% limit",
            )

    return ComplianceCheck(
        rule_name="sector_concentration",
        status="pass",
        details="Sector allocations within regulatory limits",
    )


def _check_negative_allocations(
    allocation_changes: tuple[AllocationChange, ...],
) -> tuple[str, ...]:
    """Get symbols with negative allocations."""
    return tuple(
        change.symbol
        for change in allocation_changes
        if change.recommended_allocation < 0
    )


def _check_total_allocation(
    allocation_changes: tuple[AllocationChange, ...],
) -> float:
    """Calculate total allocation percentage."""
    return sum(change.recommended_allocation for change in allocation_changes)


def validate_allocation_sanity(
    allocation_changes: tuple[AllocationChange, ...],
) -> ComplianceCheck:
    """Basic sanity checks for allocations.

    Args:
        allocation_changes: Proposed allocation changes

    Returns:
        ComplianceCheck with sanity check status
    """
    # Check for negative allocations
    negative = _check_negative_allocations(allocation_changes)
    if negative:
        return ComplianceCheck(
            rule_name="allocation_sanity",
            status="fail",
            details=f"Negative allocations not allowed: {', '.join(negative)}",
        )

    # Check total doesn't exceed 100%
    total = _check_total_allocation(allocation_changes)
    if total > MAX_TOTAL_ALLOCATION:
        return ComplianceCheck(
            rule_name="allocation_sanity",
            status="fail",
            details=f"Total allocation exceeds 100%: {total:.1f}%",
        )

    return ComplianceCheck(
        rule_name="allocation_sanity",
        status="pass",
        details="Allocation sanity checks passed",
    )
