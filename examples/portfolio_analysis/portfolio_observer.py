"""Portfolio-specific observer for rich, meaningful output display.

This observer demonstrates how to create domain-specific output formatting
without any logging in nodes or main. All display logic is centralized here.
"""

import sys
from datetime import datetime
from typing import override

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
        self.node_timings: dict[str, float] = {}

    @override
    async def on_flow_start(self, flow_name: str, message: Message) -> None:
        """Display initial market analysis setup.

        Args:
            flow_name: Name of the flow starting
            message: Initial StartAnalysisCommand with market data

        """
        if isinstance(message, StartAnalysisCommand):
            self.start_time = datetime.now()
            self._print_header()
            self._print_market_overview(message)
            self._print_constraints(message)
            self._print_separator()

    @override
    async def on_flow_end(self, flow_name: str, message: Message, error: Exception | None) -> None:
        """Display final analysis results or error.

        Args:
            flow_name: Name of the flow ending
            message: Final message (DecisionMadeEvent or AnalysisFailedEvent)
            error: Exception if flow failed

        """
        self._print_separator()

        if error:
            self._print_error_summary(error)
        elif isinstance(message, DecisionMadeEvent):
            self._print_decision_summary(message)
            self._print_execution_time()
        elif isinstance(message, AnalysisFailedEvent):
            self._print_failure_summary(message)

        self._print_separator()

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Display node analysis beginning.

        Args:
            node_name: Name of specialist node starting
            message: Message being processed

        """
        # Track node start time
        from time import time
        self.node_timings[node_name] = time()

        # Display progress indicator
        icon = self._get_node_icon(node_name)
        print(f"\n{icon} {self._format_node_name(node_name)}:", end=" ", flush=True)

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Display node analysis results.

        Args:
            node_name: Name of specialist node that completed
            message: Result message from node
            error: Exception if node failed

        """
        # Calculate node execution time
        from time import time
        elapsed = time() - self.node_timings.get(node_name, time())

        if error:
            print(f"❌ Failed ({elapsed:.1f}s)")
            print(f"   Error: {error}")
        else:
            print(f"✓ ({elapsed:.1f}s)")
            self._print_node_insights(node_name, message)

    def _print_header(self) -> None:
        """Print analysis header."""
        print("\n" + "=" * 80)
        print("📈 PORTFOLIO ANALYSIS - AI-DRIVEN INVESTMENT DECISIONS")
        print("=" * 80)

    def _print_market_overview(self, command: StartAnalysisCommand) -> None:
        """Print market conditions overview."""
        market = command.market_data
        assets = market.assets

        print(f"\n📊 MARKET CONDITIONS")
        print(f"   Date: {market.market_date}")
        print(f"   Sentiment: {market.market_sentiment.upper()}")
        print(f"   Risk-Free Rate: {market.risk_free_rate:.2%}")
        print(f"   Assets Under Analysis: {len(assets)}")

        # Sector breakdown
        sectors = {}
        for asset in assets:
            sectors[asset.sector] = sectors.get(asset.sector, 0) + 1

        print(f"\n   Sector Distribution:")
        for sector, count in sorted(sectors.items()):
            print(f"     • {sector}: {count} assets")

    def _print_constraints(self, command: StartAnalysisCommand) -> None:
        """Print portfolio constraints."""
        c = command.portfolio_constraints
        print(f"\n📋 INVESTMENT CONSTRAINTS")
        print(f"   Position Limits: {c.min_position_size:.0f}%-{c.max_position_size:.0f}% per asset")
        print(f"   Sector Limit: {c.max_sector_allocation:.0f}% max per sector")
        print(f"   Risk Limits: VaR ${c.max_var_limit:,.0f}, Max Drawdown {c.max_drawdown_threshold:.0%}")

    def _print_node_insights(self, node_name: str, message: Message) -> None:
        """Print key insights from each specialist node."""
        if isinstance(message, MarketAnalyzedEvent):
            self._print_quant_insights(message)
        elif isinstance(message, RiskAssessedEvent):
            self._print_risk_assessment(message)
        elif isinstance(message, RecommendationsGeneratedEvent):
            self._print_portfolio_recommendations(message)
        elif isinstance(message, ComplianceReviewedEvent):
            self._print_compliance_review(message)

    def _print_quant_insights(self, event: MarketAnalyzedEvent) -> None:
        """Print quantitative analysis insights."""
        insights = event.insights
        print(f"   📊 Market Trend: {insights.market_trend.upper()}")
        print(f"   📊 Confidence: {insights.overall_confidence:.0%}")

        # Top opportunities
        if insights.opportunities:
            print(f"   📊 Top Opportunities:")
            for opp in insights.opportunities[:3]:
                print(f"      • {opp.symbol}: {opp.signal_type.upper()} @ {opp.target_allocation:.0f}%")

    def _print_risk_assessment(self, event: RiskAssessedEvent) -> None:
        """Print risk analysis results."""
        assessment = event.assessment
        print(f"   ⚠️ Portfolio VaR: ${assessment.portfolio_var:,.0f}")
        print(f"   ⚠️ Sharpe Ratio: {assessment.sharpe_ratio:.2f}")
        print(f"   ⚠️ Risk Status: {assessment.risk_level.upper()}")

    def _print_portfolio_recommendations(self, event: RecommendationsGeneratedEvent) -> None:
        """Print portfolio manager recommendations."""
        recs = event.recommendations
        if recs.allocation_changes:
            print(f"   💼 Proposed Changes: {len(recs.allocation_changes)}")
            total_buy = sum(c.new_weight - c.current_weight
                          for c in recs.allocation_changes
                          if c.new_weight > c.current_weight)
            total_sell = sum(c.current_weight - c.new_weight
                           for c in recs.allocation_changes
                           if c.new_weight < c.current_weight)
            print(f"   💼 Rebalancing: +{total_buy:.0f}% / -{total_sell:.0f}%")

    def _print_compliance_review(self, event: ComplianceReviewedEvent) -> None:
        """Print compliance review results."""
        review = event.review
        print(f"   ✅ Compliance: {'PASSED' if review.all_checks_passed else 'FAILED'}")
        if review.violations:
            print(f"   ⚠️ Violations: {len(review.violations)}")

    def _print_decision_summary(self, event: DecisionMadeEvent) -> None:
        """Print final trading decision summary."""
        decision = event.decision

        print(f"\n🎯 FINAL DECISION: {decision.decision_status.upper()}")

        if decision.approved_changes:
            print(f"\n📊 APPROVED ALLOCATIONS ({len(decision.approved_changes)} changes):")

            # Group by action type
            buys = [c for c in decision.approved_changes if c.new_weight > c.current_weight]
            sells = [c for c in decision.approved_changes if c.new_weight < c.current_weight]

            if buys:
                print("\n   BUYS:")
                for change in sorted(buys, key=lambda x: x.new_weight - x.current_weight, reverse=True):
                    delta = change.new_weight - change.current_weight
                    print(f"     • {change.symbol}: +{delta:.1f}% (to {change.new_weight:.1f}%)")

            if sells:
                print("\n   SELLS:")
                for change in sorted(sells, key=lambda x: x.current_weight - x.new_weight, reverse=True):
                    delta = change.current_weight - change.new_weight
                    print(f"     • {change.symbol}: -{delta:.1f}% (to {change.new_weight:.1f}%)")

        if decision.execution_instructions:
            print(f"\n📝 EXECUTION NOTES:")
            for instruction in decision.execution_instructions[:3]:
                print(f"   • {instruction}")

        if decision.risk_warnings:
            print(f"\n⚠️ RISK WARNINGS:")
            for warning in decision.risk_warnings[:3]:
                print(f"   • {warning}")

    def _print_failure_summary(self, event: AnalysisFailedEvent) -> None:
        """Print analysis failure summary."""
        print(f"\n❌ ANALYSIS FAILED")
        print(f"   Stage: {event.failed_at_stage}")
        print(f"   Reason: {event.error_message}")
        if event.partial_results:
            print(f"   Partial Results Available: Yes")

    def _print_error_summary(self, error: Exception) -> None:
        """Print error summary."""
        print(f"\n❌ SYSTEM ERROR")
        print(f"   Type: {error.__class__.__name__}")
        print(f"   Message: {error}")

    def _print_execution_time(self) -> None:
        """Print total execution time."""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"\n⏱️ Total Analysis Time: {elapsed:.1f}s")

    def _print_separator(self) -> None:
        """Print a section separator."""
        print("=" * 80)

    def _get_node_icon(self, node_name: str) -> str:
        """Get icon for specialist node."""
        icons = {
            "quant_analyst": "📊",
            "risk_analyst": "⚠️",
            "portfolio_manager": "💼",
            "compliance_officer": "✅",
            "decision_maker": "🎯",
        }
        return icons.get(node_name.lower(), "⚙️")

    def _format_node_name(self, node_name: str) -> str:
        """Format node name for display."""
        names = {
            "quant_analyst": "Quantitative Analysis",
            "risk_analyst": "Risk Assessment",
            "portfolio_manager": "Portfolio Optimization",
            "compliance_officer": "Compliance Review",
            "decision_maker": "Decision Making",
        }
        return names.get(node_name.lower(), node_name.replace("_", " ").title())