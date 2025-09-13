"""Message nodes for portfolio analysis specialists."""

import secrets
from dataclasses import dataclass
from typing import Literal, override

from clearflow import MessageNode
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

# Constants for portfolio analysis
MAX_BULLISH_OPPORTUNITIES = 3
MAX_NEUTRAL_OPPORTUNITIES = 2
MAX_BEARISH_OPPORTUNITIES = 1

RISK_THRESHOLD = 0.7
RISK_SCORE_MAX = 0.9
MIN_POSITION_SIZE = 5.0
MAX_POSITION_SIZE_MULTIPLIER = 30.0

ALLOCATION_ACTION_THRESHOLD = 5.0
COMPLIANCE_CHANGE_LIMIT = 20.0
COMPLIANCE_CONCENTRATION_LIMIT = 40.0
COMPLIANCE_RISK_EXPOSURE_THRESHOLD = 0.8

BASE_ALLOCATION_SIZE = 10.0
BASE_CURRENT_ALLOCATION = 20.0


@dataclass(frozen=True)
class QuantAnalystNode(MessageNode[AnalyzeMarketCommand, MarketAnalyzedEvent | AnalysisFailedEvent]):
    """Quantitative analyst that identifies market opportunities."""

    name: str = "quant_analyst"

    @override
    async def process(self, message: AnalyzeMarketCommand) -> MarketAnalyzedEvent | AnalysisFailedEvent:
        """Analyze market data and identify opportunities.

        Returns:
            MarketAnalyzedEvent with identified opportunities or AnalysisFailedEvent on error.
        """
        try:
            # Simulate quant analysis based on market sentiment
            if message.market_sentiment == "bullish":
                # More opportunities in bullish market
                max_opps = MAX_BULLISH_OPPORTUNITIES
                opportunities = message.asset_symbols[:max_opps] if len(message.asset_symbols) > max_opps else message.asset_symbols
                scores = tuple(0.7 + secrets.SystemRandom().random() * 0.3 for _ in opportunities)
                trend: Literal["bullish", "bearish", "sideways"] = "bullish"
                confidence = 0.85
            elif message.market_sentiment == "bearish":
                # Fewer opportunities in bearish market
                max_opps = MAX_BEARISH_OPPORTUNITIES
                opportunities = message.asset_symbols[:max_opps] if message.asset_symbols else ()
                scores = tuple(0.4 + secrets.SystemRandom().random() * 0.2 for _ in opportunities)
                trend = "bearish"
                confidence = 0.65
            else:
                # Moderate opportunities in neutral market
                max_opps = MAX_NEUTRAL_OPPORTUNITIES
                opportunities = message.asset_symbols[:max_opps] if len(message.asset_symbols) > max_opps else message.asset_symbols
                scores = tuple(0.5 + secrets.SystemRandom().random() * 0.3 for _ in opportunities)
                trend = "sideways"
                confidence = 0.75

            return MarketAnalyzedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                identified_opportunities=opportunities,
                opportunity_scores=scores,
                market_trend=trend,
                analysis_confidence=confidence,
            )
        except ValueError as e:
            return AnalysisFailedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                failed_stage="quant_analysis",
                error_type="AnalysisError",
                error_message=str(e),
                can_retry=True,
            )


@dataclass(frozen=True)
class RiskAnalystNode(MessageNode[AssessRiskCommand, RiskAssessedEvent | AnalysisFailedEvent]):
    """Risk analyst that evaluates risk for opportunities."""

    name: str = "risk_analyst"

    @override
    async def process(self, message: AssessRiskCommand) -> RiskAssessedEvent | AnalysisFailedEvent:
        """Assess risk for identified opportunities.

        Returns:
            RiskAssessedEvent with risk scores or AnalysisFailedEvent on error.
        """
        try:
            # Simulate risk assessment based on volatility
            filtered_data = tuple(
                (symbol, confidence, min(RISK_SCORE_MAX, message.market_volatility + (1 - confidence) * 0.3))
                for symbol, confidence in zip(message.opportunity_symbols, message.confidence_scores, strict=True)
            )

            # Filter for acceptable risk and build tuples
            acceptable_data = tuple(
                (symbol, risk_score, max(MIN_POSITION_SIZE, MAX_POSITION_SIZE_MULTIPLIER * (1 - risk_score)))
                for symbol, confidence, risk_score in filtered_data
                if risk_score < RISK_THRESHOLD
            )

            acceptable_symbols = tuple(d[0] for d in acceptable_data)
            risk_scores = tuple(d[1] for d in acceptable_data)
            max_positions = tuple(d[2] for d in acceptable_data)

            # Determine overall risk level
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.5
            risk_level: Literal["low", "medium", "high"] = "high" if avg_risk > 0.6 else "medium" if avg_risk > 0.3 else "low"

            return RiskAssessedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                acceptable_symbols=tuple(acceptable_symbols),
                risk_scores=tuple(risk_scores),
                max_position_sizes=tuple(max_positions),
                overall_risk_level=risk_level,
            )
        except (ValueError, ZeroDivisionError) as e:
            return AnalysisFailedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                failed_stage="risk_assessment",
                error_type="RiskError",
                error_message=str(e),
                can_retry=True,
            )


@dataclass(frozen=True)
class PortfolioManagerNode(MessageNode[GenerateRecommendationsCommand, RecommendationsGeneratedEvent | AnalysisFailedEvent]):
    """Portfolio manager that generates allocation recommendations."""

    name: str = "portfolio_manager"

    @override
    async def process(self, message: GenerateRecommendationsCommand) -> RecommendationsGeneratedEvent | AnalysisFailedEvent:
        """Generate portfolio recommendations based on risk assessment.

        Returns:
            RecommendationsGeneratedEvent with actions or AnalysisFailedEvent on error.
        """
        try:
            # Build all data in single pass using function
            def process_allocation(data: tuple[str, float, float]) -> tuple[Literal["buy", "sell", "hold"], str, float]:
                symbol, risk_score, target_alloc = data
                current_alloc = secrets.SystemRandom().random() * BASE_CURRENT_ALLOCATION
                change = target_alloc - current_alloc
                if change > ALLOCATION_ACTION_THRESHOLD:
                    action: Literal["buy", "sell", "hold"] = "buy"
                elif change < -ALLOCATION_ACTION_THRESHOLD:
                    action = "sell"
                else:
                    action = "hold"
                return (action, symbol, change)

            processed_data = tuple(
                process_allocation((symbol, risk_score, target_alloc))
                for symbol, risk_score, target_alloc in zip(
                    message.acceptable_symbols,
                    message.risk_scores,
                    message.target_allocations,
                    strict=True,
                )
            )

            actions = tuple(d[0] for d in processed_data)
            symbols = tuple(d[1] for d in processed_data)
            changes = tuple(d[2] for d in processed_data)

            # Overall confidence based on risk levels
            avg_risk = sum(message.risk_scores) / len(message.risk_scores) if message.risk_scores else 0.5
            confidence = max(0.4, 1.0 - avg_risk)

            return RecommendationsGeneratedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                recommended_actions=tuple(actions),
                action_symbols=tuple(symbols),
                allocation_changes=tuple(changes),
                confidence_level=confidence,
            )
        except (ValueError, ZeroDivisionError) as e:
            return AnalysisFailedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                failed_stage="portfolio_management",
                error_type="RecommendationError",
                error_message=str(e),
                can_retry=False,
            )


@dataclass(frozen=True)
class ComplianceOfficerNode(MessageNode[ReviewComplianceCommand, ComplianceReviewedEvent | AnalysisFailedEvent]):
    """Compliance officer that reviews recommendations."""

    name: str = "compliance_officer"

    @override
    async def process(self, message: ReviewComplianceCommand) -> ComplianceReviewedEvent | AnalysisFailedEvent:
        """Review recommendations for compliance.

        Returns:
            ComplianceReviewedEvent with approval status or AnalysisFailedEvent on error.
        """
        try:
            # Process all compliance checks in single pass
            def check_compliance(item: tuple[str, float, float]) -> tuple[str, str, str]:
                symbol, current, recommended = item
                change = recommended - current
                if abs(change) > COMPLIANCE_CHANGE_LIMIT:
                    return (symbol, "rejected", f"{symbol}: Change too large ({change:.1f}%)")
                if recommended > COMPLIANCE_CONCENTRATION_LIMIT:
                    return (symbol, "rejected", f"{symbol}: Exceeds concentration limit")
                return (symbol, "approved", f"{symbol}: Approved")

            compliance_results = tuple(
                check_compliance(item)
                for item in message.recommended_changes
            )

            approved = tuple(r[0] for r in compliance_results if r[1] == "approved")
            rejected = tuple(r[0] for r in compliance_results if r[1] == "rejected")
            notes = tuple(r[2] for r in compliance_results)

            # Check if escalation needed
            requires_escalation = len(rejected) > len(approved) or message.risk_exposure > COMPLIANCE_RISK_EXPOSURE_THRESHOLD

            return ComplianceReviewedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                approved_symbols=tuple(approved),
                rejected_symbols=tuple(rejected),
                compliance_notes=tuple(notes),
                requires_escalation=requires_escalation,
            )
        except (ValueError, TypeError) as e:
            return AnalysisFailedEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                failed_stage="compliance_review",
                error_type="ComplianceError",
                error_message=str(e),
                can_retry=False,
            )


@dataclass(frozen=True)
class DecisionMakerNode(MessageNode[MakeDecisionCommand | AnalysisFailedEvent, DecisionMadeEvent]):
    """Decision maker that produces final trading decision."""

    name: str = "decision_maker"

    @override
    async def process(self, message: MakeDecisionCommand | AnalysisFailedEvent) -> DecisionMadeEvent:
        """Make final trading decision.

        Returns:
            DecisionMadeEvent with execution plan and approved trades.
        """
        if isinstance(message, AnalysisFailedEvent):
            # Handle error case with conservative decision
            return DecisionMadeEvent(
                triggered_by_id=message.id,
                flow_id=message.flow_id,
                execution_plan="HOLD - Analysis failed",
                approved_trades=(),
                decision_status="hold",
                monitoring_required=True,
            )

        # Build execution plan based on compliance status
        if message.compliance_status == "rejected":
            execution_plan = "HOLD - Compliance rejected"
            trades = ()
            status: Literal["execute", "hold", "escalate"] = "hold"
        elif message.compliance_status == "conditional":
            execution_plan = "ESCALATE - Requires senior approval"
            trades = ()
            status = "escalate"
        else:
            # Build trades from approved symbols
            trades_list = [
                (symbol, "BUY" if alloc > 0 else "SELL", abs(alloc))
                for symbol, alloc in zip(message.approved_symbols, message.approved_allocations, strict=True)
                if alloc != 0
            ]
            trades = tuple(trades_list)

            if trades:
                execution_plan = f"EXECUTE - {len(trades)} trades approved"
                status = "execute"
            else:
                execution_plan = "HOLD - No actionable trades"
                status = "hold"

        return DecisionMadeEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            execution_plan=execution_plan,
            approved_trades=tuple(trades),
            decision_status=status,
            monitoring_required=len(trades) > 0,
        )