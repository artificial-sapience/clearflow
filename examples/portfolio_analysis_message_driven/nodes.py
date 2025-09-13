"""Message nodes for portfolio analysis specialists with DSPy LLM intelligence.

Pure business logic implementation without console logging.
Observability will be handled separately via Observer pattern.
"""

from dataclasses import dataclass, field
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import MessageNode
from examples.portfolio_analysis_message_driven.messages import (
    AnalysisFailedEvent,
    ComplianceReviewedEvent,
    DecisionMadeEvent,
    MarketAnalyzedEvent,
    RecommendationsGeneratedEvent,
    RiskAssessedEvent,
    StartAnalysisCommand,
)
from examples.portfolio_analysis_message_driven.specialists.compliance.signature import ComplianceOfficerSignature
from examples.portfolio_analysis_message_driven.specialists.decision.models import TradingDecision
from examples.portfolio_analysis_message_driven.specialists.decision.signature import TradingDecisionSignature
from examples.portfolio_analysis_message_driven.specialists.portfolio.signature import PortfolioManagerSignature
from examples.portfolio_analysis_message_driven.specialists.quant.signature import QuantAnalystSignature
from examples.portfolio_analysis_message_driven.specialists.risk.signature import RiskAnalystSignature


@dataclass(frozen=True)
class QuantAnalystNode(MessageNode[StartAnalysisCommand, MarketAnalyzedEvent | AnalysisFailedEvent]):
    """Quantitative analyst that identifies market opportunities using DSPy.

    Uses LLM to analyze market data and identify investment opportunities.
    """

    name: str = "quant_analyst"
    _predictor: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor with quantitative analyst signature."""
        super().__post_init__()
        object.__setattr__(self, "_predictor", dspy.Predict(QuantAnalystSignature))

    @override
    async def process(self, message: StartAnalysisCommand) -> MarketAnalyzedEvent | AnalysisFailedEvent:
        """Analyze market data using LLM to identify opportunities.

        Args:
            message: Command containing market data and constraints.

        Returns:
            MarketAnalyzedEvent with LLM-identified opportunities or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get structured insights from LLM
            prediction = self._predictor(market_data=message.market_data)

            return MarketAnalyzedEvent(
                insights=prediction.insights,
                market_data=message.market_data,
                constraints=message.portfolio_constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            return AnalysisFailedEvent(
                failed_stage="quant_analyst",
                error_type=type(exc).__name__,
                error_message=str(exc),
                partial_results=None,
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.portfolio_constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


@dataclass(frozen=True)
class RiskAnalystNode(MessageNode[MarketAnalyzedEvent, RiskAssessedEvent | AnalysisFailedEvent]):
    """Risk analyst that evaluates risk using DSPy.

    Uses LLM to assess risk for identified opportunities.
    """

    name: str = "risk_analyst"
    _predictor: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor with risk analyst signature."""
        super().__post_init__()
        object.__setattr__(self, "_predictor", dspy.Predict(RiskAnalystSignature))

    @override
    async def process(self, message: MarketAnalyzedEvent) -> RiskAssessedEvent | AnalysisFailedEvent:
        """Assess risk using LLM for identified opportunities.

        Args:
            message: Event containing market analysis results.

        Returns:
            RiskAssessedEvent with LLM risk assessment or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get risk assessment from LLM
            prediction = self._predictor(
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
                failed_stage="risk_analyst",
                error_type=type(exc).__name__,
                error_message=str(exc),
                partial_results={"opportunities_count": len(message.insights.opportunities)},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


@dataclass(frozen=True)
class PortfolioManagerNode(MessageNode[RiskAssessedEvent, RecommendationsGeneratedEvent | AnalysisFailedEvent]):
    """Portfolio manager that generates recommendations using DSPy.

    Uses LLM to optimize portfolio allocations.
    """

    name: str = "portfolio_manager"
    _predictor: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor with portfolio manager signature."""
        super().__post_init__()
        object.__setattr__(self, "_predictor", dspy.Predict(PortfolioManagerSignature))

    @override
    async def process(self, message: RiskAssessedEvent) -> RecommendationsGeneratedEvent | AnalysisFailedEvent:
        """Generate portfolio recommendations using LLM.

        Args:
            message: Event containing risk assessment results.

        Returns:
            RecommendationsGeneratedEvent with LLM recommendations or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get portfolio recommendations from LLM
            prediction = self._predictor(
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
                failed_stage="portfolio_manager",
                error_type=type(exc).__name__,
                error_message=str(exc),
                partial_results={"risk_level": message.assessment.risk_level},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=message.market_data,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


@dataclass(frozen=True)
class ComplianceOfficerNode(MessageNode[RecommendationsGeneratedEvent, ComplianceReviewedEvent | AnalysisFailedEvent]):
    """Compliance officer that reviews recommendations using DSPy.

    Uses LLM to ensure regulatory and policy compliance.
    """

    name: str = "compliance_officer"
    _predictor: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor with compliance signature."""
        super().__post_init__()
        object.__setattr__(self, "_predictor", dspy.Predict(ComplianceOfficerSignature))

    @override
    async def process(self, message: RecommendationsGeneratedEvent) -> ComplianceReviewedEvent | AnalysisFailedEvent:
        """Review recommendations for compliance using LLM.

        Args:
            message: Event containing portfolio recommendations.

        Returns:
            ComplianceReviewedEvent with compliance review or AnalysisFailedEvent.

        """
        try:
            # Use DSPy to get compliance review from LLM
            prediction = self._predictor(
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
                failed_stage="compliance_officer",
                error_type=type(exc).__name__,
                error_message=str(exc),
                partial_results={"recommendations_available": bool(message.recommendations)},
                can_retry=isinstance(exc, openai.OpenAIError),
                fallback_action="hold",
                market_data=None,
                constraints=message.constraints,
                run_id=message.run_id,
                triggered_by_id=message.id,
            )


@dataclass(frozen=True)
class DecisionMakerNode(MessageNode[ComplianceReviewedEvent | AnalysisFailedEvent, DecisionMadeEvent]):
    """Decision maker that makes final trading decisions using DSPy.

    Uses LLM to make the final go/no-go decision.
    """

    name: str = "decision_maker"
    _predictor: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor with decision maker signature."""
        super().__post_init__()
        object.__setattr__(self, "_predictor", dspy.Predict(TradingDecisionSignature))

    @override
    async def process(self, message: ComplianceReviewedEvent | AnalysisFailedEvent) -> DecisionMadeEvent:
        """Make final trading decision using LLM.

        Args:
            message: Event containing compliance review or analysis failure.

        Returns:
            DecisionMadeEvent with final trading decision.

        """
        if isinstance(message, AnalysisFailedEvent):
            # Conservative decision on failure - create minimal TradingDecision
            conservative_decision = TradingDecision(
                approved_changes=(),
                execution_plan=f"Analysis failed at {message.failed_stage}: {message.error_message}. Taking conservative approach - holding all positions.",
                monitoring_requirements=("Monitor system health", "Retry analysis when stable"),
                audit_trail=f"System error: {message.error_type}. Defaulting to hold position for safety.",
                decision_status="hold",
            )

            return DecisionMadeEvent(
                decision=conservative_decision,
                review=None,  # No compliance review available
                run_id=message.run_id,
                triggered_by_id=message.id,
            )

        try:
            # Use DSPy to get final decision from LLM
            prediction = self._predictor(
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
                approved_changes=(),
                execution_plan=f"Decision process error: {exc!s}. Taking conservative approach - holding all positions.",
                monitoring_requirements=("Monitor decision system health", "Review error logs"),
                audit_trail=f"Decision error: {type(exc).__name__}. Defaulting to hold position for safety.",
                decision_status="hold",
            )

            return DecisionMadeEvent(
                decision=conservative_decision,
                review=None,  # No review available on error path
                run_id=message.run_id,
                triggered_by_id=message.id,
            )
