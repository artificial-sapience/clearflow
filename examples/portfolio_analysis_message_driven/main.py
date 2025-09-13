"""Main entry point for message-driven portfolio analysis with LLM intelligence."""

import asyncio
import sys
import uuid
from pathlib import Path

from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange
from examples.portfolio_analysis_message_driven.market_data import (
    create_bullish_market_data,
    create_sample_market_data,
    create_volatile_market_data,
)
from examples.portfolio_analysis_message_driven.messages import (
    DecisionMadeEvent,
    PortfolioConstraints,
    StartAnalysisCommand,
)
from examples.portfolio_analysis_message_driven.portfolio_flow import create_portfolio_analysis_flow
from examples.portfolio_analysis_message_driven.shared.config import configure_dspy

# Display constants
MAX_ASSETS_TO_DISPLAY = 5
MAX_ALLOCATIONS_TO_DISPLAY = 10
MAX_TRADES_TO_DISPLAY = 5
MAX_RISKS_TO_DISPLAY = 3
DECISION_REASONING_PREVIEW_LENGTH = 200


def create_market_scenario(scenario: str = "normal") -> StartAnalysisCommand:
    """Create market analysis command for different scenarios.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"

    Returns:
        StartAnalysisCommand with complete market data and constraints.

    """
    # Get appropriate market data
    if scenario == "bullish":
        market_data = create_bullish_market_data()
    elif scenario == "volatile":
        market_data = create_volatile_market_data()
    else:  # normal
        market_data = create_sample_market_data()

    # Define portfolio constraints
    constraints = PortfolioConstraints(
        max_position_size=15.0,  # Max 15% per asset
        max_sector_allocation=40.0,  # Max 40% per sector
        min_position_size=2.0,  # Min 2% if taking position
        max_var_limit=2_000_000.0,  # $2M Value at Risk limit
        max_drawdown_threshold=0.20,  # 20% max drawdown
    )

    return StartAnalysisCommand(
        market_data=market_data,
        portfolio_constraints=constraints,
        flow_id=uuid.uuid4(),  # Generate flow ID for this analysis session
    )


def print_market_command(command: StartAnalysisCommand) -> None:
    """Print market analysis command details.

    Args:
        command: The start analysis command to display.

    """
    print("\n" + "=" * 80)
    print("📊 MARKET ANALYSIS REQUEST")
    print("=" * 80)

    # Extract asset symbols from market data
    symbols = [asset.symbol for asset in command.market_data.assets]
    print(
        f"\nAssets to analyze: {', '.join(symbols[:MAX_ASSETS_TO_DISPLAY])}{'...' if len(symbols) > MAX_ASSETS_TO_DISPLAY else ''}"
    )
    print(f"Total assets: {len(symbols)}")
    print(f"Market sentiment: {command.market_data.market_sentiment}")
    print(f"Risk-free rate: {command.market_data.risk_free_rate:.2%}")
    print(f"Market date: {command.market_data.market_date}")

    print("\nPortfolio Constraints:")
    print(f"  • Max position size: {command.portfolio_constraints.max_position_size}%")
    print(f"  • Max sector allocation: {command.portfolio_constraints.max_sector_allocation}%")
    print(f"  • Max VaR limit: ${command.portfolio_constraints.max_var_limit:,.0f}")
    print(f"  • Max drawdown: {command.portfolio_constraints.max_drawdown_threshold:.0%}")


def _print_decision_header(decision_status: str) -> None:
    """Print decision event header."""
    print("\n" + "=" * 80)
    print("📋 FINAL DECISION EVENT")
    print("=" * 80)
    print(f"\nDecision: {decision_status.upper()}")


def _print_approved_changes(changes: tuple[AllocationChange, ...]) -> None:
    """Print approved changes if any."""
    if changes:
        print("\nApproved Changes:")
        for change in changes:
            print(f"  • {change}")


def _print_monitoring_requirements(requirements: tuple[str, ...]) -> None:
    """Print monitoring requirements if any."""
    if requirements:
        print("\nMonitoring Requirements:")
        for req in requirements[:MAX_RISKS_TO_DISPLAY]:
            print(f"  • {req}")


def print_decision_event(event: DecisionMadeEvent) -> None:
    """Print final trading decision event.

    Args:
        event: The decision made event to display.

    """
    _print_decision_header(event.decision.decision_status)
    _print_approved_changes(event.decision.approved_changes)

    print(f"\nExecution Plan: {event.decision.execution_plan[:DECISION_REASONING_PREVIEW_LENGTH]}...")

    if event.decision.decision_status == "escalate":
        print("\n⚠️ REQUIRES HUMAN REVIEW")

    _print_monitoring_requirements(event.decision.monitoring_requirements)
    print(f"\nAudit Trail: {event.decision.audit_trail[:DECISION_REASONING_PREVIEW_LENGTH]}...")


def print_message_flow() -> None:
    """Print the pure event-driven message flow diagram."""
    print("\n" + "=" * 80)
    print("🔄 PURE EVENT-DRIVEN FLOW (No Orchestrators)")
    print("=" * 80)
    print("""
    StartAnalysisCommand
            ↓
    [QuantAnalystNode] → MarketAnalyzedEvent
            ↓
    [RiskAnalystNode] → RiskAssessedEvent
            ↓
    [PortfolioManagerNode] → RecommendationsGeneratedEvent
            ↓
    [ComplianceOfficerNode] → ComplianceReviewedEvent
            ↓
    [DecisionMakerNode] → DecisionMadeEvent

    Note: AnalysisFailedEvent from any node routes directly to DecisionMaker
    Each node reads what it needs from the previous event.
    """)


async def run_portfolio_analysis(scenario: str = "normal") -> None:
    """Run the portfolio analysis workflow.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"

    """
    # Configure DSPy with OpenAI
    print("\n🔧 Configuring DSPy with OpenAI...")
    try:
        configure_dspy()
        print("✅ DSPy configured successfully")
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Ensure OPENAI_API_KEY is set")
        sys.exit(1)

    # Create market command
    command = create_market_scenario(scenario)

    # Display command
    print_market_command(command)

    # Show message flow
    print_message_flow()

    # Create and run the flow
    print("\n" + "=" * 80)
    print("🤖 EXECUTING EVENT-DRIVEN WORKFLOW WITH LLM INTELLIGENCE")
    print("=" * 80)

    flow = create_portfolio_analysis_flow()
    result = await flow.process(command)

    # Display final decision
    print_decision_event(result)


def print_menu() -> None:
    """Print menu options."""
    print("\n" + "=" * 80)
    print("🎯 PORTFOLIO ANALYSIS WITH LLM INTELLIGENCE")
    print("=" * 80)
    print("\n🧠 Using DSPy with OpenAI for real market analysis")
    print("\n📊 Pure Event-Driven Architecture:")
    print("- Single initiating command (StartAnalysisCommand)")
    print("- Events describe outcomes, not instructions")
    print("- Direct node routing without orchestrators")
    print("- Each node uses LLM for intelligent decisions")
    print("\nSelect market scenario:")
    print("1. Normal market conditions (default)")
    print("2. Bullish market (growth opportunities)")
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

    print(f"\n🚀 Running {scenario.upper()} market scenario with LLM analysis...")
    await run_portfolio_analysis(scenario)


if __name__ == "__main__":
    # Ensure we're in the right directory for .env loading
    example_dir = Path(__file__).parent
    if example_dir.exists():
        import os

        os.chdir(example_dir)

    asyncio.run(main())
