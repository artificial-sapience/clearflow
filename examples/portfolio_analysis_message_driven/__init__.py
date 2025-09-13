"""Message-driven portfolio analysis example with pure event-driven architecture."""

from examples.portfolio_analysis_message_driven.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    PortfolioConstraints,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)
from examples.portfolio_analysis_message_driven.portfolio_flow import create_portfolio_analysis_flow

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
