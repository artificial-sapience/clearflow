"""Market data simulator for portfolio analysis example."""

# ruff: noqa: S311 - Using random for example data generation, not cryptographic purposes
# ruff: noqa: DTZ005 - Timezone not needed for example market date strings

import random
from datetime import datetime
from itertools import starmap
from typing import Literal

from examples.portfolio_analysis.models_pydantic import AssetData, MarketData

# Market simulation constants
PRICE_VARIANCE_MIN = 0.95
PRICE_VARIANCE_MAX = 1.05
TECH_FINANCE_BASE_VOLUME = 1_000_000
OTHER_SECTORS_BASE_VOLUME = 500_000
VOLUME_MULTIPLIER_MIN = 0.7
VOLUME_MULTIPLIER_MAX = 1.8
BASE_VOLATILITY = 0.15
VOLATILITY_MULTIPLIER_MIN = 0.8
VOLATILITY_MULTIPLIER_MAX = 1.4
MOMENTUM_MIN = -0.8
MOMENTUM_MAX = 0.8
PRECISION_DECIMAL_PLACES = 3

# Sector volatility multipliers
TECH_VOLATILITY_MULTIPLIER = 1.4
FINANCE_VOLATILITY_MULTIPLIER = 1.1
HEALTHCARE_VOLATILITY_MULTIPLIER = 0.9
ENERGY_VOLATILITY_MULTIPLIER = 1.3
UTILITIES_VOLATILITY_MULTIPLIER = 0.6
CONSUMER_VOLATILITY_MULTIPLIER = 0.8
DEFAULT_VOLATILITY_MULTIPLIER = 1.0

# Risk-free rate range
RISK_FREE_RATE_MIN = 0.025
RISK_FREE_RATE_MAX = 0.055

# Volatile market scenario constants
VOLATILE_PRICE_VARIANCE_MIN = 0.85
VOLATILE_PRICE_VARIANCE_MAX = 1.20
VOLATILE_BASE_VOLUME = 2_000_000
VOLATILE_VOLUME_MIN = 1.5
VOLATILE_VOLUME_MAX = 3.0
VOLATILE_VOLATILITY_MIN = 0.25
VOLATILE_VOLATILITY_MAX = 0.65
VOLATILE_MOMENTUM_MIN = -1.0
VOLATILE_MOMENTUM_MAX = 1.0
VOLATILE_RISK_FREE_RATE = 0.048

# Bullish market scenario constants
BULLISH_PRICE_VARIANCE_MIN = 1.02
BULLISH_PRICE_VARIANCE_MAX = 1.12
BULLISH_BASE_VOLUME = 1_500_000
BULLISH_VOLUME_MIN = 0.8
BULLISH_VOLUME_MAX = 1.4
BULLISH_VOLATILITY_MIN = 0.08
BULLISH_VOLATILITY_MAX = 0.25
BULLISH_MOMENTUM_MIN = 0.2
BULLISH_MOMENTUM_MAX = 0.9
BULLISH_RISK_FREE_RATE = 0.035

# Sector sets for membership testing
TECH_FINANCE_SECTORS = {"Technology", "Finance"}


def _generate_asset_data(symbol: str, sector: str, base_price: float) -> AssetData:
    """Generate simulated market data for a single asset."""
    # Add some market volatility
    price_variance = random.uniform(PRICE_VARIANCE_MIN, PRICE_VARIANCE_MAX)
    current_price = round(base_price * price_variance, 2)

    # Simulate volume based on asset type
    base_volume = (
        TECH_FINANCE_BASE_VOLUME
        if sector in TECH_FINANCE_SECTORS
        else OTHER_SECTORS_BASE_VOLUME
    )
    volume = int(
        base_volume * random.uniform(VOLUME_MULTIPLIER_MIN, VOLUME_MULTIPLIER_MAX)
    )

    # Generate realistic volatility (technology higher than utilities)
    volatility_multiplier = {
        "Technology": TECH_VOLATILITY_MULTIPLIER,
        "Finance": FINANCE_VOLATILITY_MULTIPLIER,
        "Healthcare": HEALTHCARE_VOLATILITY_MULTIPLIER,
        "Energy": ENERGY_VOLATILITY_MULTIPLIER,
        "Utilities": UTILITIES_VOLATILITY_MULTIPLIER,
        "Consumer": CONSUMER_VOLATILITY_MULTIPLIER,
    }.get(sector, DEFAULT_VOLATILITY_MULTIPLIER)

    volatility = round(
        BASE_VOLATILITY
        * volatility_multiplier
        * random.uniform(VOLATILITY_MULTIPLIER_MIN, VOLATILITY_MULTIPLIER_MAX),
        PRECISION_DECIMAL_PLACES,
    )

    # Generate momentum indicator (-1 to 1)
    momentum = round(
        random.uniform(MOMENTUM_MIN, MOMENTUM_MAX), PRECISION_DECIMAL_PLACES
    )

    return AssetData(
        symbol=symbol,
        price=current_price,
        volume=volume,
        volatility=volatility,
        momentum=momentum,
        sector=sector,
    )


def create_sample_market_data() -> MarketData:
    """Create simulated market data for a diversified portfolio."""

    # Define sample assets across sectors
    sample_assets = [
        ("AAPL", "Technology", 175.50),
        ("MSFT", "Technology", 380.25),
        ("GOOGL", "Technology", 140.80),
        ("JPM", "Finance", 165.30),
        ("BAC", "Finance", 42.15),
        ("JNJ", "Healthcare", 162.40),
        ("PFE", "Healthcare", 28.90),
        ("XOM", "Energy", 108.75),
        ("CVX", "Energy", 152.60),
        ("NEE", "Utilities", 82.35),
        ("SO", "Utilities", 75.20),
        ("AMZN", "Consumer", 155.90),
        ("WMT", "Consumer", 82.45),
    ]

    # Generate market data for each asset
    assets = tuple(starmap(_generate_asset_data, sample_assets))

    # Simulate overall market conditions
    market_sentiments: tuple[Literal["bullish", "bearish", "neutral"], ...] = (
        "bullish",
        "bearish",
        "neutral",
    )
    market_sentiment = random.choice(market_sentiments)

    # Current risk-free rate (e.g., 10-year treasury)
    risk_free_rate = round(random.uniform(RISK_FREE_RATE_MIN, RISK_FREE_RATE_MAX), 4)

    return MarketData(
        assets=assets,
        market_date=datetime.now().strftime("%Y-%m-%d"),
        risk_free_rate=risk_free_rate,
        market_sentiment=market_sentiment,
    )


def create_volatile_market_data() -> MarketData:
    """Create market data simulating high volatility conditions."""

    sample_assets = [
        ("AAPL", "Technology", 175.50),
        ("MSFT", "Technology", 380.25),
        ("TSLA", "Technology", 195.30),  # High volatility stock
        ("JPM", "Finance", 165.30),
        ("NVDA", "Technology", 875.40),  # High momentum stock
        ("XOM", "Energy", 108.75),
        ("COIN", "Finance", 240.80),  # Crypto-related volatility
        ("NEE", "Utilities", 82.35),
        ("AMZN", "Consumer", 155.90),
        ("SPY", "Index", 485.60),  # Market index
    ]

    # Generate high volatility scenario using immutable operations
    def _create_volatile_asset(
        symbol: str, sector: str, base_price: float
    ) -> AssetData:
        # Increase volatility and momentum ranges for stress testing
        price_variance = random.uniform(
            VOLATILE_PRICE_VARIANCE_MIN, VOLATILE_PRICE_VARIANCE_MAX
        )  # More extreme price moves
        current_price = round(base_price * price_variance, 2)

        volume = int(
            VOLATILE_BASE_VOLUME
            * random.uniform(VOLATILE_VOLUME_MIN, VOLATILE_VOLUME_MAX)
        )  # High volume

        # Higher volatility across all sectors
        volatility = round(
            random.uniform(VOLATILE_VOLATILITY_MIN, VOLATILE_VOLATILITY_MAX),
            PRECISION_DECIMAL_PLACES,
        )

        # More extreme momentum (market stress)
        momentum = round(
            random.uniform(VOLATILE_MOMENTUM_MIN, VOLATILE_MOMENTUM_MAX),
            PRECISION_DECIMAL_PLACES,
        )

        return AssetData(
            symbol=symbol,
            price=current_price,
            volume=volume,
            volatility=volatility,
            momentum=momentum,
            sector=sector,
        )

    assets = tuple(starmap(_create_volatile_asset, sample_assets))

    return MarketData(
        assets=tuple(assets),
        market_date=datetime.now().strftime("%Y-%m-%d"),
        risk_free_rate=VOLATILE_RISK_FREE_RATE,  # Higher rates during stress
        market_sentiment="bearish",
    )


def create_bullish_market_data() -> MarketData:
    """Create market data simulating strong bullish conditions."""

    sample_assets = [
        ("AAPL", "Technology", 175.50),
        ("MSFT", "Technology", 380.25),
        ("GOOGL", "Technology", 140.80),
        ("NVDA", "Technology", 875.40),
        ("JPM", "Finance", 165.30),
        ("GS", "Finance", 425.80),
        ("JNJ", "Healthcare", 162.40),
        ("UNH", "Healthcare", 512.90),
        ("XOM", "Energy", 108.75),
        ("NEE", "Utilities", 82.35),
        ("AMZN", "Consumer", 155.90),
        ("TSLA", "Technology", 195.30),
    ]

    def _create_bullish_asset(symbol: str, sector: str, base_price: float) -> AssetData:
        # Positive price momentum in bull market
        price_variance = random.uniform(
            BULLISH_PRICE_VARIANCE_MIN, BULLISH_PRICE_VARIANCE_MAX
        )  # Upward bias
        current_price = round(base_price * price_variance, 2)

        volume = int(
            BULLISH_BASE_VOLUME * random.uniform(BULLISH_VOLUME_MIN, BULLISH_VOLUME_MAX)
        )

        # Lower volatility in stable bull market
        volatility = round(
            random.uniform(BULLISH_VOLATILITY_MIN, BULLISH_VOLATILITY_MAX),
            PRECISION_DECIMAL_PLACES,
        )

        # Positive momentum across most assets
        momentum = round(
            random.uniform(BULLISH_MOMENTUM_MIN, BULLISH_MOMENTUM_MAX),
            PRECISION_DECIMAL_PLACES,
        )

        return AssetData(
            symbol=symbol,
            price=current_price,
            volume=volume,
            volatility=volatility,
            momentum=momentum,
            sector=sector,
        )

    assets = tuple(starmap(_create_bullish_asset, sample_assets))

    return MarketData(
        assets=tuple(assets),
        market_date=datetime.now().strftime("%Y-%m-%d"),
        risk_free_rate=BULLISH_RISK_FREE_RATE,  # Lower rates support bull market
        market_sentiment="bullish",
    )
