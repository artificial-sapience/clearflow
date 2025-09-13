"""Message-driven portfolio analysis example."""

from examples.portfolio_analysis_message_driven.messages import (
    AnalysisFailedEvent,
    AnalyzeMarketCommand,
    AssessRiskCommand,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    GenerateRecommendationsCommand,
    MakeDecisionCommand,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    ReviewComplianceCommand,
    RiskAssessedEvent,
)
from examples.portfolio_analysis_message_driven.portfolio_flow import create_portfolio_analysis_flow

__all__ = [
    # Commands
    "AnalyzeMarketCommand",
    "AssessRiskCommand",
    "GenerateRecommendationsCommand",
    "ReviewComplianceCommand",
    "MakeDecisionCommand",
    # Events
    "MarketAnalyzedEvent",
    "RiskAssessedEvent",
    "RecommendationsGeneratedEvent",
    "ComplianceReviewedEvent",
    "DecisionMadeEvent",
    "AnalysisFailedEvent",
    # Flow
    "create_portfolio_analysis_flow",
]
