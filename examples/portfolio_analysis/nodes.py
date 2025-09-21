"""Message nodes for portfolio analysis specialists with DSPy integration.

Pure business logic implementation without console logging.
Observability will be handled separately via Observer pattern.
"""

from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node
from examples.portfolio_analysis.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)
from examples.portfolio_analysis.specialists.compliance.signature import ComplianceOfficerSignature
from examples.portfolio_analysis.specialists.decision.models import TradingDecision
from examples.portfolio_analysis.specialists.decision.signature import TradingDecisionSignature
from examples.portfolio_analysis.specialists.portfolio.signature import PortfolioManagerSignature
from examples.portfolio_analysis.specialists.quant.signature import QuantAnalystSignature
from examples.portfolio_analysis.specialists.risk.signature import RiskAnalystSignature


class QuantAnalystNode(Node[StartAnalysisCommand, MarketAnalyzedEvent | AnalysisFailedEvent]):
    """Quantitative analyst that identifies market opportunities using DSPy.

    Analyzes market data to identify investment opportunities using DSPy.
    """

    name: str = "quant_analyst"

    @override
    async def process(self, message: StartAnalysisCommand) -> MarketAnalyzedEvent | AnalysisFailedEvent:
        """Analyze market data to identify opportunities.

        Args:
            message: Command containing market data and constraints.

        Returns:
            MarketAnalyzedEvent with identified opportunities or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get structured insights from LLM
            predictor = dspy.Predict(QuantAnalystSignature)
            prediction = predictor(market_data=message.market_data)

            return MarketAnalyzedEvent(
                insights=prediction.insights,
                market_data=message.market_data,
                constraints=message.portfolio_constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            return AnalysisFailedEvent(
                failed_stage="QuantAnalystNode",
                error_type="APIError" if "API" in str(exc) else "DataError",
                error_message=str(exc),
                partial_results=None,
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.portfolio_constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


class RiskAnalystNode(Node[MarketAnalyzedEvent, RiskAssessedEvent | AnalysisFailedEvent]):
    """Risk analyst that evaluates risk using DSPy.

    Assesses risk for identified opportunities using DSPy.
    """

    name: str = "risk_analyst"

    @override
    async def process(self, message: MarketAnalyzedEvent) -> RiskAssessedEvent | AnalysisFailedEvent:
        """Assess risk for identified opportunities.

        Args:
            message: Event containing market analysis results.

        Returns:
            RiskAssessedEvent with risk assessment or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get risk assessment from LLM
            predictor = dspy.Predict(RiskAnalystSignature)
            prediction = predictor(
                quant_insights=message.insights,
            )

            return RiskAssessedEvent(
                assessment=prediction.risk_assessment,
                market_data=message.market_data,
                constraints=message.constraints,
                insights=message.insights,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            return AnalysisFailedEvent(
                failed_stage="RiskAnalystNode",
                error_type="LimitExceeded" if "limit" in str(exc).lower() else "ValidationError",
                error_message=str(exc),
                partial_results={"market_trend": message.insights.market_trend},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


class PortfolioManagerNode(Node[RiskAssessedEvent, RecommendationsGeneratedEvent | AnalysisFailedEvent]):
    """Portfolio manager that generates recommendations using DSPy.

    Optimizes portfolio allocations using DSPy.
    """

    name: str = "portfolio_manager"

    @override
    async def process(self, message: RiskAssessedEvent) -> RecommendationsGeneratedEvent | AnalysisFailedEvent:
        """Generate portfolio recommendations.

        Args:
            message: Event containing risk assessment results.

        Returns:
            RecommendationsGeneratedEvent with portfolio recommendations or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get portfolio recommendations from LLM
            predictor = dspy.Predict(PortfolioManagerSignature)
            prediction = predictor(
                risk_assessment=message.assessment,
                quant_insights=message.insights,
                portfolio_constraints=message.constraints,
            )

            return RecommendationsGeneratedEvent(
                recommendations=prediction.recommendations,
                assessment=message.assessment,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            return AnalysisFailedEvent(
                failed_stage="PortfolioManagerNode",
                error_type="ValidationError" if "validation" in str(exc).lower() else "DataError",
                error_message=str(exc),
                partial_results={"risk_level": message.assessment.risk_level},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


class ComplianceOfficerNode(Node[RecommendationsGeneratedEvent, ComplianceReviewedEvent | AnalysisFailedEvent]):
    """Compliance officer that reviews recommendations using DSPy.

    Ensures regulatory and policy compliance using DSPy.
    """

    name: str = "compliance_officer"

    @override
    async def process(self, message: RecommendationsGeneratedEvent) -> ComplianceReviewedEvent | AnalysisFailedEvent:
        """Review recommendations for compliance.

        Args:
            message: Event containing portfolio recommendations.

        Returns:
            ComplianceReviewedEvent with compliance review or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get compliance review from LLM
            predictor = dspy.Predict(ComplianceOfficerSignature)
            prediction = predictor(
                recommendations=message.recommendations,
            )

            return ComplianceReviewedEvent(
                review=prediction.compliance_review,
                recommendations=message.recommendations,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            return AnalysisFailedEvent(
                failed_stage="ComplianceOfficerNode",
                error_type="ValidationError" if "compliance" in str(exc).lower() else "DataError",
                error_message=str(exc),
                partial_results={"recommendations_available": bool(message.recommendations)},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=None,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


class DecisionMakerNode(Node[ComplianceReviewedEvent | AnalysisFailedEvent, DecisionMadeEvent]):
    """Decision maker that makes final trading decisions using DSPy.

    Makes the final go/no-go decision using DSPy.
    """

    name: str = "decision_maker"

    @override
    async def process(self, message: ComplianceReviewedEvent | AnalysisFailedEvent) -> DecisionMadeEvent:
        """Make final trading decision.

        Args:
            message: Event containing compliance review or analysis failure.

        Returns:
            DecisionMadeEvent with final trading decision.

        """
        if isinstance(message, AnalysisFailedEvent):
            # Conservative decision on failure - create minimal TradingDecision
            conservative_decision = TradingDecision(
                decision_status="rejected",
                approved_changes=(),
                execution_instructions=(
                    f"Analysis failed at {message.failed_stage}: {message.error_message}. Holding all positions.",
                ),
                risk_warnings=("System health issue - monitor and retry when stable",),
            )

            return DecisionMadeEvent(
                decision=conservative_decision,
                review=None,  # No compliance review available
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        try:
            # Use DSPy to get final decision from LLM
            predictor = dspy.Predict(TradingDecisionSignature)
            prediction = predictor(
                compliance_review=message.review,
            )

            return DecisionMadeEvent(
                decision=prediction.trading_decision,
                review=message.review,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Fallback to conservative decision on error
            conservative_decision = TradingDecision(
                decision_status="rejected",
                approved_changes=(),
                execution_instructions=(f"Decision process error: {exc!s}. Holding all positions.",),
                risk_warnings=("Decision system health issue - review error logs",),
            )

            return DecisionMadeEvent(
                decision=conservative_decision,
                review=None,  # No review available on error path
                run_id=message.run_id,
                triggered_by_id=message.id,
            )
