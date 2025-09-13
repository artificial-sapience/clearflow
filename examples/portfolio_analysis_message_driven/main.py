"""Main entry point for message-driven portfolio analysis."""

import asyncio

from clearflow import FlowId
from examples.portfolio_analysis_message_driven.messages import AnalyzeMarketCommand, DecisionMadeEvent
from examples.portfolio_analysis_message_driven.portfolio_flow import create_portfolio_analysis_flow


def create_market_scenario(scenario: str = "normal") -> AnalyzeMarketCommand:
    """Create market analysis command for different scenarios.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"

    Returns:
        Command to start market analysis

    """
    flow_id = FlowId.create()

    if scenario == "bullish":
        return AnalyzeMarketCommand(
            flow_id=flow_id,
            triggered_by_id=None,
            asset_symbols=("AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"),
            market_sentiment="bullish",
            risk_free_rate=0.045,
            market_date="2024-01-15",
        )
    if scenario == "volatile":
        return AnalyzeMarketCommand(
            flow_id=flow_id,
            triggered_by_id=None,
            asset_symbols=("NVDA", "META", "COIN"),
            market_sentiment="bearish",
            risk_free_rate=0.055,
            market_date="2024-01-15",
        )
    # normal
    return AnalyzeMarketCommand(
        flow_id=flow_id,
        triggered_by_id=None,
        asset_symbols=("SPY", "QQQ", "IWM", "DIA"),
        market_sentiment="neutral",
        risk_free_rate=0.05,
        market_date="2024-01-15",
    )


def print_market_command(command: AnalyzeMarketCommand) -> None:
    """Print market analysis command details."""
    print("\n" + "=" * 80)
    print("📊 MARKET ANALYSIS REQUEST")
    print("=" * 80)
    print(f"\nAssets to analyze: {', '.join(command.asset_symbols)}")
    print(f"Market sentiment: {command.market_sentiment}")
    print(f"Risk-free rate: {command.risk_free_rate:.2%}")
    print(f"Market date: {command.market_date}")
    print(f"Flow ID: {command.flow_id}")


def print_decision_event(event: DecisionMadeEvent) -> None:
    """Print final trading decision event."""
    print("\n" + "=" * 80)
    print("📋 FINAL DECISION EVENT")
    print("=" * 80)
    print(f"\nExecution Plan: {event.execution_plan}")
    print(f"Decision Status: {event.decision_status.upper()}")

    if event.approved_trades:
        print("\nApproved Trades:")
        for symbol, action, amount in event.approved_trades:
            print(f"  • {symbol}: {action} {amount:.1f}%")
    else:
        print("\nNo trades approved")

    if event.monitoring_required:
        print("\n⚠️ Monitoring Required")

    print(f"\nTriggered by: {event.triggered_by_id}")
    print(f"Flow ID: {event.flow_id}")


def print_message_flow() -> None:
    """Print the message flow diagram."""
    print("\n" + "=" * 80)
    print("🔄 MESSAGE-DRIVEN FLOW")
    print("=" * 80)
    print("""
    AnalyzeMarketCommand
            ↓
    [QuantAnalystNode] → MarketAnalyzedEvent
            ↓
    [PrepareRiskAssessment] → AssessRiskCommand
            ↓
    [RiskAnalystNode] → RiskAssessedEvent
            ↓
    [PrepareRecommendations] → GenerateRecommendationsCommand
            ↓
    [PortfolioManagerNode] → RecommendationsGeneratedEvent
            ↓
    [PrepareComplianceReview] → ReviewComplianceCommand
            ↓
    [ComplianceOfficerNode] → ComplianceReviewedEvent
            ↓
    [PrepareDecision] → MakeDecisionCommand
            ↓
    [DecisionMakerNode] → DecisionMadeEvent

    Note: AnalysisFailedEvent from any node routes directly to DecisionMaker
    """)


async def run_portfolio_analysis(scenario: str = "normal") -> None:
    """Run the portfolio analysis workflow.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"

    """
    # Create market command
    command = create_market_scenario(scenario)

    # Display command
    print_market_command(command)

    # Show message flow
    print_message_flow()

    # Create and run the flow
    print("\n" + "=" * 80)
    print("🤖 EXECUTING MESSAGE-DRIVEN WORKFLOW")
    print("=" * 80)

    flow = create_portfolio_analysis_flow()
    result = await flow.process(command)

    # Display final decision
    print_decision_event(result)


def print_menu() -> None:
    """Print menu options."""
    print("\n" + "=" * 80)
    print("🎯 MESSAGE-DRIVEN PORTFOLIO ANALYSIS")
    print("=" * 80)
    print("\n📊 Demonstrates focused messages without god-objects")
    print("\nEach message has single responsibility:")
    print("- Commands contain only essential input data")
    print("- Events contain only specific outcomes")
    print("- No large data structures passed between nodes")
    print("\nSelect market scenario:")
    print("1. Normal market conditions (default)")
    print("2. Bullish market (opportunities)")
    print("3. Volatile market (high risk)")


async def main() -> None:
    """Run the main entry point with menu."""
    print_menu()
    choice = input("\nEnter choice (1-3, default=1): ").strip()

    scenarios = {
        "1": "normal",
        "2": "bullish",
        "3": "volatile",
    }

    scenario = scenarios.get(choice, "normal")
    if choice and choice not in scenarios:
        print("Invalid choice. Running default scenario (normal).")

    print(f"\n🚀 Running {scenario.upper()} market scenario...")
    await run_portfolio_analysis(scenario)


if __name__ == "__main__":
    asyncio.run(main())
