"""Portfolio-specific observer for rich, meaningful output display.

This observer demonstrates how to create domain-specific output formatting
without any logging in nodes or main. All display logic is centralized here.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import override

from rich.console import Console

from clearflow import Message, Observer
from examples.portfolio_analysis.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)
from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange


def _print_header() -> None:
    """Print analysis header."""
    print("\n" + "=" * 80)
    print("📈 PORTFOLIO ANALYSIS - AI-DRIVEN INVESTMENT DECISIONS")
    print("=" * 80)


def _print_market_overview(command: StartAnalysisCommand) -> None:
    """Print market conditions overview."""
    market = command.market_data
    assets = market.assets

    print("\n📊 MARKET CONDITIONS")
    print(f"   Date: {market.market_date}")
    print(f"   Sentiment: {market.market_sentiment.upper()}")
    print(f"   Risk-Free Rate: {market.risk_free_rate:.2%}")
    print(f"   Assets Under Analysis: {len(assets)}")

    # Sector breakdown
    sectors = tuple(asset.sector for asset in assets)
    unique_sectors = sorted(frozenset(sectors))

    print("\n   Sector Distribution:")
    for sector in unique_sectors:
        count = sum(1 for s in sectors if s == sector)
        print(f"     • {sector}: {count} assets")


def _print_constraints(command: StartAnalysisCommand) -> None:
    """Print portfolio constraints."""
    c = command.portfolio_constraints
    print("\n📋 INVESTMENT CONSTRAINTS")
    print(f"   Position Limits: {c.min_position_size:.0f}%-{c.max_position_size:.0f}% per asset")
    print(f"   Sector Limit: {c.max_sector_allocation:.0f}% max per sector")
    print(f"   Risk Limits: VaR ${c.max_var_limit:,.0f}, Max Drawdown {c.max_drawdown_threshold:.0%}")


def _print_quant_insights(event: MarketAnalyzedEvent) -> None:
    """Print quantitative analysis insights."""
    insights = event.insights
    print(f"   📊 Market Trend: {insights.market_trend.upper()}")
    print(f"   📊 Confidence: {insights.confidence:.0%}")
    print(f"   📊 Volatility Index: {insights.volatility_index:.1f}")

    # Top signals
    if insights.top_signals:
        print("   📊 Top Signals:")
        for signal in insights.top_signals[:3]:
            print(f"      • {signal.symbol}: {signal.signal.upper()} (strength: {signal.strength:.0%})")


def _print_risk_assessment(event: RiskAssessedEvent) -> None:
    """Print risk analysis results."""
    assessment = event.assessment
    print(f"   ⚠️ Portfolio VaR: ${assessment.portfolio_var:,.0f}")
    print(f"   ⚠️ Sharpe Ratio: {assessment.sharpe_ratio:.2f}")
    print(f"   ⚠️ Risk Status: {assessment.risk_level.upper()}")


def _calculate_rebalancing_totals(changes: Sequence[AllocationChange]) -> tuple[float, float]:
    """Calculate total buy and sell percentages.

    Returns:
        Tuple of (total_buy, total_sell)

    """
    total_buy = sum(c.new_weight - c.current_weight for c in changes if c.new_weight > c.current_weight)
    total_sell = sum(c.current_weight - c.new_weight for c in changes if c.new_weight < c.current_weight)
    return total_buy, total_sell


def _print_portfolio_recommendations(event: RecommendationsGeneratedEvent) -> None:
    """Print portfolio manager recommendations."""
    recs = event.recommendations
    if not recs.allocation_changes:
        return

    print(f"   💼 Proposed Changes: {len(recs.allocation_changes)}")
    total_buy, total_sell = _calculate_rebalancing_totals(recs.allocation_changes)
    print(f"   💼 Rebalancing: +{total_buy:.0f}% / -{total_sell:.0f}%")


def _print_compliance_review(event: ComplianceReviewedEvent) -> None:
    """Print compliance review results."""
    review = event.review
    print(f"   ✅ Compliance: {'PASSED' if review.all_checks_passed else 'FAILED'}")
    if review.violations:
        print(f"   ⚠️ Violations: {len(review.violations)}")


def _print_buys(buys: Sequence[AllocationChange]) -> None:
    """Print buy allocations."""
    if buys:
        print("\n   BUYS:")
        for change in sorted(buys, key=lambda x: x.new_weight - x.current_weight, reverse=True):
            delta = change.new_weight - change.current_weight
            print(f"     • {change.symbol}: +{delta:.1f}% (to {change.new_weight:.1f}%)")


def _print_sells(sells: Sequence[AllocationChange]) -> None:
    """Print sell allocations."""
    if sells:
        print("\n   SELLS:")
        for change in sorted(sells, key=lambda x: x.current_weight - x.new_weight, reverse=True):
            delta = change.current_weight - change.new_weight
            print(f"     • {change.symbol}: -{delta:.1f}% (to {change.new_weight:.1f}%)")


def _print_execution_notes(instructions: Sequence[str]) -> None:
    """Print execution instructions."""
    if instructions:
        print("\n📝 EXECUTION NOTES:")
        for instruction in instructions[:3]:
            print(f"   • {instruction}")


def _print_risk_warnings(warnings: Sequence[str]) -> None:
    """Print risk warnings."""
    if warnings:
        print("\n⚠️ RISK WARNINGS:")
        for warning in warnings[:3]:
            print(f"   • {warning}")


def _group_allocation_changes(
    changes: Sequence[AllocationChange],
) -> tuple[Sequence[AllocationChange], Sequence[AllocationChange]]:
    """Group allocation changes into buys and sells.

    Returns:
        Tuple of (buys, sells)

    """
    buys = [c for c in changes if c.new_weight > c.current_weight]
    sells = [c for c in changes if c.new_weight < c.current_weight]
    return buys, sells


def _print_approved_allocations(changes: Sequence[AllocationChange]) -> None:
    """Print approved allocation changes."""
    print(f"\n📊 APPROVED ALLOCATIONS ({len(changes)} changes):")
    buys, sells = _group_allocation_changes(changes)
    _print_buys(buys)
    _print_sells(sells)


def _print_decision_summary(event: DecisionMadeEvent) -> None:
    """Print final trading decision summary."""
    decision = event.decision
    print(f"\n🎯 FINAL DECISION: {decision.decision_status.upper()}")

    if decision.approved_changes:
        _print_approved_allocations(decision.approved_changes)

    _print_execution_notes(decision.execution_instructions)
    _print_risk_warnings(decision.risk_warnings)


def _print_failure_summary(event: AnalysisFailedEvent) -> None:
    """Print analysis failure summary."""
    print("\n❌ ANALYSIS FAILED")
    print(f"   Stage: {event.failed_stage}")
    print(f"   Reason: {event.error_message}")
    if event.partial_results:
        print("   Partial Results Available: Yes")


def _print_error_summary(error: Exception) -> None:
    """Print error summary."""
    print("\n❌ SYSTEM ERROR")
    print(f"   Type: {error.__class__.__name__}")
    print(f"   Message: {error}")


def _print_separator() -> None:
    """Print a section separator."""
    print("=" * 80)


def _get_node_icon(node_name: str) -> str:
    """Get icon for specialist node.

    Returns:
        Icon string for the given node.

    """
    icons = {
        "quant_analyst": "📊",
        "risk_analyst": "⚠️",
        "portfolio_manager": "💼",
        "compliance_officer": "✅",
        "decision_maker": "🎯",
    }
    return icons.get(node_name.lower(), "⚙️")


def _format_node_name(node_name: str) -> str:
    """Format node name for display.

    Returns:
        Formatted node name string.

    """
    names = {
        "quant_analyst": "Quantitative Analysis",
        "risk_analyst": "Risk Assessment",
        "portfolio_manager": "Portfolio Optimization",
        "compliance_officer": "Compliance Review",
        "decision_maker": "Decision Making",
    }
    return names.get(node_name.lower(), node_name.replace("_", " ").title())


class PortfolioAnalysisObserver(Observer):
    """Observer that provides rich, financial-focused output for portfolio analysis.

    This observer:
    - Displays market conditions and analysis parameters at flow start
    - Shows progress through each specialist's analysis
    - Formats financial data in a meaningful way
    - Provides a comprehensive summary at flow completion
    - Handles errors gracefully with actionable information

    All output is handled here - nodes and main remain clean.
    """

    def __init__(self) -> None:
        """Initialize the portfolio observer."""
        self.start_time: datetime | None = None
        self.console = Console()
        self._current_spinner = None

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Display initial market analysis setup.

        Args:
            flow_name: Name of the flow starting
            message: Initial StartAnalysisCommand with market data

        """
        if isinstance(message, StartAnalysisCommand):
            self.start_time = datetime.now(UTC)
            _print_header()
            _print_market_overview(message)
            _print_constraints(message)
            _print_separator()

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Display final analysis results or error.

        Args:
            flow_name: Name of the flow ending
            message: Final message (DecisionMadeEvent or AnalysisFailedEvent)
            error: Exception if flow failed

        """
        _print_separator()

        if error:
            _print_error_summary(error)
        elif isinstance(message, DecisionMadeEvent):
            _print_decision_summary(message)
            if self.start_time:
                elapsed = (datetime.now(UTC) - self.start_time).total_seconds()
                print(f"\n⏱️ Total Analysis Time: {elapsed:.1f}s")
        elif isinstance(message, AnalysisFailedEvent):
            _print_failure_summary(message)

        _print_separator()

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Display node analysis beginning.

        Args:
            node_name: Name of specialist node starting
            message: Message being processed

        """
        # Start spinner for this node
        self._current_spinner = self.console.status(
            f"[cyan]{_format_node_name(node_name)}[/cyan] analyzing...", spinner="dots"
        )
        self._current_spinner.start()

    def _stop_spinner(self) -> None:
        """Stop the current spinner if it exists."""
        if self._current_spinner:
            self._current_spinner.stop()
            self._current_spinner = None

    def _print_node_status(self, node_name: str, error: Exception | None) -> None:
        """Print node completion status."""
        icon = _get_node_icon(node_name)
        formatted_name = _format_node_name(node_name)

        if error:
            self.console.print(f"{icon} {formatted_name}: [red]❌ Failed[/red]")
            self.console.print(f"   Error: {error}")
        else:
            self.console.print(f"{icon} {formatted_name}: [green]✓[/green]")

    @staticmethod
    def _print_node_insights(message: Message) -> None:
        """Print insights based on message type."""
        if isinstance(message, MarketAnalyzedEvent):
            _print_quant_insights(message)
        elif isinstance(message, RiskAssessedEvent):
            _print_risk_assessment(message)
        elif isinstance(message, RecommendationsGeneratedEvent):
            _print_portfolio_recommendations(message)
        elif isinstance(message, ComplianceReviewedEvent):
            _print_compliance_review(message)

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Display node analysis results.

        Args:
            node_name: Name of specialist node that completed
            message: Result message from node
            error: Exception if node failed

        """
        self._stop_spinner()
        self._print_node_status(node_name, error)

        if not error:
            self._print_node_insights(message)
