"""Message-driven portfolio analysis example."""

from examples.portfolio_analysis.flow import create_portfolio_analysis_flow
from examples.portfolio_analysis.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    PortfolioConstraints,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)

__all__ = [
    "AnalysisFailedEvent",
    "ComplianceReviewedEvent",
    "DecisionMadeEvent",
    "MarketAnalyzedEvent",
    "PortfolioConstraints",
    "RecommendationsGeneratedEvent",
    "RiskAssessedEvent",
    "StartAnalysisCommand",
    "create_portfolio_analysis_flow",
]
