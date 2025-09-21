"""Main entry point for message-driven portfolio analysis with AI-powered decisions."""

import asyncio
import sys
import uuid
from pathlib import Path
from types import TracebackType

from rich.console import Console

from examples.portfolio_analysis.flow import create_portfolio_analysis_flow
from examples.portfolio_analysis.market_data import (
    create_bullish_market_data,
    create_sample_market_data,
    create_volatile_market_data,
)
from examples.portfolio_analysis.messages import (
    PortfolioConstraints,
    StartAnalysisCommand,
)
from examples.portfolio_analysis.shared.config import configure_dspy


class SpinnerContext:
    """Simple spinner context manager for async operations."""

    def __init__(self, message: str = "Processing") -> None:
        """Initialize spinner with a message."""
        self.message = message
        self._console = Console()
        self._status = None

    async def __aenter__(self) -> "SpinnerContext":
        """Start the spinner.

        Returns:
            Self for context manager protocol.

        """
        self._status = self._console.status(self.message, spinner="dots")
        self._status.__enter__()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Stop the spinner."""
        if self._status:
            self._status.__exit__(None, None, None)


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
        run_id=uuid.uuid4(),  # Generate flow ID for this analysis session
    )


async def run_portfolio_analysis(scenario: str = "normal") -> None:
    """Run the portfolio analysis workflow.

    Args:
        scenario: Market scenario - "normal", "bullish", or "volatile"

    """
    # Configure DSPy with OpenAI
    async with SpinnerContext("Configuring DSPy..."):
        try:
            configure_dspy()
        except ValueError as e:
            print(f"\n❌ Configuration Error: {e}")
            print("\n📝 Setup Instructions:")
            print("1. Copy .env.example to .env")
            print("2. Add your OpenAI API key to .env")
            sys.exit(1)

    # Create market command
    command = create_market_scenario(scenario)

    # Create and run the flow - all output handled by observer
    flow = create_portfolio_analysis_flow()
    await flow.process(command)


def print_menu() -> None:
    """Print menu options."""
    print("\nPORTFOLIO ANALYSIS")
    print("Select market scenario:")
    print("  1. Normal market conditions (default)")
    print("  2. Bullish market (growth opportunities)")
    print("  3. Volatile market (high risk)")


async def main() -> None:
    """Run the main entry point with menu."""
    print_menu()
    choice = await asyncio.to_thread(input, "\nEnter choice (1-3, default=1): ")
    choice = choice.strip()

    scenarios = {
        "1": "normal",
        "2": "bullish",
        "3": "volatile",
    }

    scenario = scenarios.get(choice, "normal")

    await run_portfolio_analysis(scenario)


if __name__ == "__main__":
    # Ensure we're in the right directory for .env loading
    example_dir = Path(__file__).parent
    if example_dir.exists():
        import os

        os.chdir(example_dir)

    asyncio.run(main())
