"""Orchestrator nodes that transform messages between specialists."""

from dataclasses import dataclass
from typing import override

from clearflow import MessageNode
from examples.portfolio_analysis_message_driven.messages import (
    AssessRiskCommand,
    ComplianceReviewedEvent,
    GenerateRecommendationsCommand,
    MakeDecisionCommand,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    ReviewComplianceCommand,
    RiskAssessedEvent,
)


@dataclass(frozen=True)
class PrepareRiskAssessmentNode(MessageNode[MarketAnalyzedEvent, AssessRiskCommand]):
    """Transform market analysis into risk assessment command."""

    name: str = "prepare_risk_assessment"

    @override
    async def process(self, message: MarketAnalyzedEvent) -> AssessRiskCommand:
        """Prepare risk assessment from market analysis."""
        # Calculate market volatility from analysis confidence
        market_volatility = 1.0 - message.analysis_confidence

        return AssessRiskCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            opportunity_symbols=message.identified_opportunities,
            confidence_scores=message.opportunity_scores,
            market_volatility=market_volatility,
        )


@dataclass(frozen=True)
class PrepareRecommendationsNode(MessageNode[RiskAssessedEvent, GenerateRecommendationsCommand]):
    """Transform risk assessment into recommendation generation command."""

    name: str = "prepare_recommendations"

    @override
    async def process(self, message: RiskAssessedEvent) -> GenerateRecommendationsCommand:
        """Prepare recommendation generation from risk assessment."""
        # Use max position sizes as target allocations
        return GenerateRecommendationsCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            acceptable_symbols=message.acceptable_symbols,
            risk_scores=message.risk_scores,
            target_allocations=message.max_position_sizes,
        )


@dataclass(frozen=True)
class PrepareComplianceReviewNode(MessageNode[RecommendationsGeneratedEvent, ReviewComplianceCommand]):
    """Transform recommendations into compliance review command."""

    name: str = "prepare_compliance"

    @override
    async def process(self, message: RecommendationsGeneratedEvent) -> ReviewComplianceCommand:
        """Prepare compliance review from recommendations."""
        # Build recommendation changes tuples
        changes = tuple(
            (symbol, max(0.0, 20.0 - abs(change)), max(0.0, 20.0 - abs(change)) + change)
            for symbol, action, change in zip(
                message.action_symbols,
                message.recommended_actions,
                message.allocation_changes,
                strict=True,
            )
        )

        # Calculate risk exposure from confidence
        risk_exposure = 1.0 - message.confidence_level

        return ReviewComplianceCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            recommended_changes=changes,
            risk_exposure=risk_exposure,
        )


@dataclass(frozen=True)
class PrepareDecisionNode(MessageNode[ComplianceReviewedEvent, MakeDecisionCommand]):
    """Transform compliance review into final decision command."""

    name: str = "prepare_decision"

    @override
    async def process(self, message: ComplianceReviewedEvent) -> MakeDecisionCommand:
        """Prepare final decision from compliance review."""
        # Determine compliance status
        if message.rejected_symbols and not message.approved_symbols:
            compliance_status = "rejected"
        elif message.requires_escalation:
            compliance_status = "conditional"
        else:
            compliance_status = "approved"

        # Calculate approved allocations (simplified)
        allocations = tuple(10.0 for _ in message.approved_symbols)

        return MakeDecisionCommand(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            approved_symbols=message.approved_symbols,
            approved_allocations=allocations,
            compliance_status=compliance_status,
        )
