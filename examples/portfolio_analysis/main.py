"""Main entry point for AI-powered portfolio analysis using DSPy."""
# pyright: reportUnknownMemberType=false

import asyncio

from clearflow import NodeResult
from examples.portfolio_analysis.market_data import (
    create_bullish_market_data,
    create_sample_market_data,
    create_volatile_market_data,
)
from examples.portfolio_analysis.models_pydantic import (
    AllocationChange,
    MarketData,
    TradingDecision,
)
from examples.portfolio_analysis.portfolio_flow import create_portfolio_analysis_flow


def print_market_overview(market_data: MarketData) -> None:
    """Print market data overview."""
    print("\n" + "=" * 80)
    print("📊 SIMULATED MARKET DATA (Educational Example)")
    print("=" * 80)

    for asset in market_data.assets:
        print(f"\n{asset.symbol}:")
        print(f"  Price: ${asset.price:.2f}")
        print(f"  Volume: {asset.volume:,}")
        print(f"  Volatility: {asset.volatility:.2%}")
        print(f"  Momentum: {asset.momentum:+.2f}")
        print(f"  Sector: {asset.sector}")

    print(f"\nMarket Sentiment: {market_data.market_sentiment}")
    print(f"Risk-Free Rate: {market_data.risk_free_rate:.2%}")
    print(f"Market Date: {market_data.market_date}")


def _get_allocation_action(delta: float) -> str:
    """Get allocation action based on delta.

    Returns:
        Action string: "INCREASE", "DECREASE", or "HOLD".
    """
    if delta > 0:
        return "INCREASE"
    if delta < 0:
        return "DECREASE"
    return "HOLD"


def _print_allocation_changes(changes: tuple[AllocationChange, ...]) -> None:
    """Print allocation changes."""
    if not changes:
        print("\nNo allocation changes approved (HOLD)")
        return

    print("\nApproved Allocation Changes:")
    for change in changes:
        delta = change.recommended_allocation - change.current_allocation
        action = _get_allocation_action(delta)
        msg = (
            f"  • {change.symbol}: {action} to {change.recommended_allocation:.1f}% "
            f"(from {change.current_allocation:.1f}%)"
        )
        print(msg)
        if change.change_reason:
            print(f"    Reason: {change.change_reason}")


def _print_trading_decision(decision: TradingDecision) -> None:
    """Print approved trading decision details."""
    print("\n✅ Trading Decision Approved")
    print(f"\nExecution Plan: {decision.execution_plan}")

    _print_allocation_changes(decision.approved_changes)

    if decision.monitoring_requirements:
        print("\nMonitoring Requirements:")
        for req in decision.monitoring_requirements:
            print(f"  • {req}")

    if decision.decision_status == "escalate":
        print("\n⚠️ Escalation Required")


def print_final_decision(result: NodeResult[TradingDecision]) -> None:
    """Print the final trading decision or error."""
    print("\n" + "=" * 80)
    print("📋 EXAMPLE OUTPUT (Not Investment Advice)")
    print("=" * 80)

    _print_trading_decision(result.state)

    print("\n" + "=" * 80)
    print("⚠️  Educational example only. Not for actual investment decisions.")
    print("=" * 80)


async def run_portfolio_analysis(scenario: str = "normal") -> None:
    """Run the portfolio analysis workflow.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"
    """
    # Create market data based on scenario
    if scenario == "bullish":
        market_data = create_bullish_market_data()
        print("\n🚀 Running BULLISH market scenario (simulated data)...")
    elif scenario == "volatile":
        market_data = create_volatile_market_data()
        print("\n⚡ Running VOLATILE market scenario (simulated data)...")
    else:
        market_data = create_sample_market_data()
        print("\n📈 Running NORMAL market scenario (simulated data)...")

    # Display market overview
    print_market_overview(market_data)

    # Create and run the flow
    print("\n" + "=" * 80)
    print("🤖 AI TEAM ANALYSIS (Educational Demonstration)")
    print("=" * 80)

    flow = create_portfolio_analysis_flow()
    result = await flow(market_data)

    # Display final decision
    print_final_decision(result)


def _print_menu() -> None:
    """Print menu options."""
    print("\n" + "=" * 80)
    print("🎯 EDUCATIONAL PORTFOLIO ANALYSIS EXAMPLE")
    print("=" * 80)
    print("\n⚠️  DISCLAIMER: This is an educational example using simulated data.")
    print("    Not for actual investment decisions. Not investment advice.")
    print("\nThis example demonstrates multi-agent portfolio analysis using DSPy")
    print("for structured outputs and Pydantic for validation.")
    print("\nSelect market scenario:")
    print("1. Normal market conditions")
    print("2. Bullish market (opportunities)")
    print("3. Volatile market (risk limits)")
    print("4. Run all scenarios")


async def _run_scenario_by_choice(choice: str) -> None:
    """Run scenario based on user choice."""
    scenarios = {
        "1": "normal",
        "2": "bullish",
        "3": "volatile",
    }

    if choice in scenarios:
        await run_portfolio_analysis(scenarios[choice])
    elif choice == "4":
        for scenario in ["normal", "bullish", "volatile"]:
            await run_portfolio_analysis(scenario)
            if scenario != "volatile":
                input("\nPress Enter to continue to next scenario...")
    else:
        print("Invalid choice. Running normal scenario.")
        await run_portfolio_analysis("normal")


async def main() -> None:
    """Main entry point with menu."""
    _print_menu()
    choice = input("\nEnter choice (1-4): ").strip()
    await _run_scenario_by_choice(choice)


if __name__ == "__main__":
    asyncio.run(main())
