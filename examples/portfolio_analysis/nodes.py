"""Educational example nodes demonstrating workflow patterns with DSPy."""

from dataclasses import dataclass, field
from operator import itemgetter
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.models import (
    AllocationChange,
    AnalysisError,
    ComplianceCheck,
    ComplianceError,
    ComplianceReview,
    MarketData,
    OpportunitySignal,
    PortfolioRecommendations,
    QuantInsights,
    RiskAssessment,
    RiskLimitError,
    RiskMetrics,
    TradingDecision,
)
from examples.portfolio_analysis.signatures import (
    ComplianceOfficerSignature,
    PortfolioManagerSignature,
    QuantAnalystSignature,
    RiskAnalystSignature,
    TradingDecisionSignature,
)
from examples.portfolio_analysis.validators import (
    validate_allocation_sanity,
    validate_position_limits,
    validate_sector_concentration,
)


@dataclass(frozen=True)
class QuantAnalyst(Node[MarketData, QuantInsights | AnalysisError]):
    """AI-powered quantitative analyst using DSPy for structured analysis."""

    name: str = "quant_analyst"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        # Create predictor with signature
        object.__setattr__(self, "_predict", dspy.Predict(QuantAnalystSignature))

    @override
    async def prep(self, state: MarketData) -> MarketData:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 QUANTITATIVE ANALYST")
        print("   └─ Analyzing market trends and opportunities...")
        return state

    @staticmethod
    def _display_opportunities(opportunities: tuple[OpportunitySignal, ...]) -> None:
        """Display top investment opportunities."""
        if opportunities:
            print("   • Top Opportunities:")
            for opp in opportunities[:3]:
                print(f"     - {opp.symbol}: {opp.confidence:.0%} confidence")

    @staticmethod
    def _display_sector_analysis(sector_analysis: dict[str, float]) -> None:
        """Display sector outlook with sentiment analysis."""
        if sector_analysis:
            print("   • Sector Outlook:")
            sorted_sectors = sorted(sector_analysis.items(), key=itemgetter(1), reverse=True)
            for sector, score in sorted_sectors[:3]:
                sentiment = "bullish" if score > 0 else "bearish"
                print(f"     - {sector}: {sentiment} ({score:+.2f})")

    def _display_insights(self, insights: QuantInsights) -> None:
        """Display quantitative analysis insights."""
        print("\n   📊 Key Insights:")
        self._display_opportunities(insights.opportunities)
        self._display_sector_analysis(insights.sector_analysis)
        print(f"   • Market Regime: {insights.market_trend}")
        print(f"   • Summary: {insights.analysis_summary}")

    @override
    async def post(
        self, result: NodeResult[QuantInsights | AnalysisError]
    ) -> NodeResult[QuantInsights | AnalysisError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, AnalysisError):
            print("   ❌ Analysis failed")
        else:
            print("   ✔ Analysis complete")
            self._display_insights(result.state)
        return result

    @override
    async def exec(self, state: MarketData) -> NodeResult[QuantInsights | AnalysisError]:
        """Analyze market data using DSPy structured prediction.

        Returns:
            NodeResult with quantitative insights or analysis error.
        """

        if not state.assets:
            error = AnalysisError(
                error_type="no_market_data",
                error_message="No market data provided for analysis",
                failed_stage="QUANTITATIVE ANALYST (quant_analyst)",
                market_data=state,
            )
            return NodeResult(error, outcome="analysis_failed")

        try:
            # Extract available symbols for context
            symbols = tuple(asset.symbol for asset in state.assets)
            max_display = 5
            print(
                f"   • Analyzing {len(symbols)} assets: {', '.join(symbols[:max_display])}{'...' if len(symbols) > max_display else ''}"
            )

            # Use DSPy to get structured insights
            prediction = self._predict(market_data=state)
            insights: QuantInsights = prediction.insights

            return NodeResult(insights, outcome="analysis_complete")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            error = AnalysisError(
                error_type="prediction_failed",
                error_message=f"Quantitative analysis failed: {exc!s}",
                failed_stage="QUANTITATIVE ANALYST (quant_analyst)",
                market_data=state,
            )
            return NodeResult(error, outcome="analysis_failed")


@dataclass(frozen=True)
class RiskAnalyst(Node[QuantInsights, RiskAssessment | RiskLimitError]):
    """AI-powered risk analyst using DSPy for structured risk assessment."""

    name: str = "risk_analyst"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(RiskAnalystSignature))

    @override
    async def prep(self, state: QuantInsights) -> QuantInsights:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 RISK ANALYST")
        print("   └─ Evaluating portfolio risk metrics and stress testing...")
        return state

    @staticmethod
    def _display_risk_issues(error: RiskLimitError) -> None:
        """Display risk limit violations."""
        print("\n   ⚠️  Risk Issues:")
        for limit in error.exceeded_limits:
            print(f"   • {limit}")

    @staticmethod
    def _display_risk_assessment(assessment: RiskAssessment) -> None:
        """Display risk assessment details."""
        print("\n   🛡️ Risk Metrics:")
        metrics = assessment.risk_metrics
        print(f"   • Value at Risk (95%): ${metrics.value_at_risk:,.0f}")
        print(f"   • Max Drawdown: {metrics.max_drawdown:.1%}")
        print(f"   • Risk Level: {assessment.risk_level.upper()}")
        # Display concentration risks if any
        if metrics.concentration_risk:
            print("   • Concentration Risks:")
            for asset, concentration in list(metrics.concentration_risk.items())[:3]:
                print(f"     - {asset}: {concentration:.1%}")
        # Display top warnings
        if assessment.risk_warnings:
            print("   • Key Warnings:")
            for warning in assessment.risk_warnings[:2]:
                print(f"     - {warning}")
        print(f"   • Overall Assessment: {assessment.risk_summary}")

    @override
    async def post(
        self, result: NodeResult[RiskAssessment | RiskLimitError]
    ) -> NodeResult[RiskAssessment | RiskLimitError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, RiskLimitError):
            print("   ❌ Risk limits exceeded")
            self._display_risk_issues(result.state)
        else:
            print("   ✔ Risk assessment complete")
            self._display_risk_assessment(result.state)
        return result

    @override
    async def exec(self, state: QuantInsights) -> NodeResult[RiskAssessment | RiskLimitError]:
        """Perform risk analysis using DSPy structured prediction.

        Returns:
            NodeResult with risk assessment or risk limit error.
        """

        try:
            # Use DSPy to get structured risk assessment
            # The AI will determine risk acceptability based on context
            prediction = self._predict(quant_insights=state)
            assessment: RiskAssessment = prediction.risk_assessment

            # Let AI determine the outcome based on its risk assessment
            # High/extreme risks should be flagged by the AI's judgment
            if assessment.risk_level == "extreme":
                # AI has determined risks are unacceptable
                error = RiskLimitError(
                    exceeded_limits=tuple(assessment.risk_warnings[:3]),  # Top warnings
                    risk_metrics=assessment.risk_metrics,
                    recommendations=tuple(assessment.risk_warnings[3:6]),  # Recommendations
                    failed_stage="RISK ANALYST (risk_analyst)",
                )
                return NodeResult(error, outcome="risk_limits_exceeded")

            return NodeResult(assessment, outcome="risk_acceptable")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create minimal error for exception handling
            error_metrics = RiskMetrics(
                value_at_risk=0.01,  # Minimum positive value for validation
                max_drawdown=0.0,
                concentration_risk={},
                correlation_warning=False,
            )
            error = RiskLimitError(
                exceeded_limits=(f"Analysis failed: {exc!s}",),
                risk_metrics=error_metrics,
                recommendations=("Retry risk analysis", "Check input data quality"),
                failed_stage="RISK ANALYST (risk_analyst)",
            )
            return NodeResult(error, outcome="risk_limits_exceeded")


@dataclass(frozen=True)
class PortfolioManager(Node[RiskAssessment, PortfolioRecommendations | AnalysisError]):
    """AI-powered portfolio manager using DSPy for structured recommendations."""

    name: str = "portfolio_manager"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(PortfolioManagerSignature))

    @override
    async def prep(self, state: RiskAssessment) -> RiskAssessment:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 PORTFOLIO MANAGER")
        print("   └─ Developing strategic allocation recommendations...")
        return state

    @staticmethod
    def _group_allocation_changes(
        allocation_changes: tuple[AllocationChange, ...],
    ) -> tuple[tuple[AllocationChange, ...], tuple[AllocationChange, ...]]:
        """Group allocation changes into increases and decreases.

        Returns:
            Tuple of (increases, decreases) allocation changes.
        """
        increases = tuple(c for c in allocation_changes if c.recommended_allocation > c.current_allocation)
        decreases = tuple(c for c in allocation_changes if c.recommended_allocation < c.current_allocation)
        return increases, decreases

    @staticmethod
    def _display_allocation_increases(increases: tuple[AllocationChange, ...]) -> None:
        """Display recommended allocation increases."""
        if increases:
            print("   • Recommended Increases:")
            for change in increases[:3]:
                delta = change.recommended_allocation - change.current_allocation
                print(f"     - {change.symbol}: +{delta:.1f}% (to {change.recommended_allocation:.1f}%)")

    @staticmethod
    def _display_allocation_decreases(decreases: tuple[AllocationChange, ...]) -> None:
        """Display recommended allocation decreases."""
        if decreases:
            print("   • Recommended Decreases:")
            for change in decreases[:3]:
                delta = change.current_allocation - change.recommended_allocation
                print(f"     - {change.symbol}: -{delta:.1f}% (to {change.recommended_allocation:.1f}%)")

    def _display_portfolio_recommendations(self, recommendations: PortfolioRecommendations) -> None:
        """Display portfolio recommendation details."""
        print("\n   💼 Portfolio Adjustments:")
        increases, decreases = self._group_allocation_changes(recommendations.allocation_changes)
        self._display_allocation_increases(increases)
        self._display_allocation_decreases(decreases)
        print(f"   • Strategy: {recommendations.investment_thesis[:100]}...")
        print(f"   • Timeline: {recommendations.execution_timeline}")

    @override
    async def post(
        self, result: NodeResult[PortfolioRecommendations | AnalysisError]
    ) -> NodeResult[PortfolioRecommendations | AnalysisError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, AnalysisError):
            print("   ❌ Portfolio management failed")
        else:
            print("   ✔ Recommendations generated")
            self._display_portfolio_recommendations(result.state)
        return result

    @override
    async def exec(self, state: RiskAssessment) -> NodeResult[PortfolioRecommendations | AnalysisError]:
        """Generate portfolio recommendations using DSPy.

        Returns:
            NodeResult with portfolio recommendations or analysis error.
        """

        # Check if risk is too extreme for adjustments
        if state.risk_level == "extreme":
            error = AnalysisError(
                error_type="extreme_risk",
                error_message="Risk level too high for portfolio adjustments",
                failed_stage="PORTFOLIO MANAGER (portfolio_manager)",
                market_data=None,
            )
            return NodeResult(error, outcome="analysis_failed")

        try:
            # Use DSPy to get structured recommendations
            prediction = self._predict(risk_assessment=state)
            recommendations: PortfolioRecommendations = prediction.recommendations

            return NodeResult(recommendations, outcome="recommendations_ready")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            error = AnalysisError(
                error_type="pm_analysis_failed",
                error_message=f"Portfolio management analysis failed: {exc!s}",
                failed_stage="PORTFOLIO MANAGER (portfolio_manager)",
                market_data=None,
            )
            return NodeResult(error, outcome="analysis_failed")


@dataclass(frozen=True)
class ComplianceOfficer(Node[PortfolioRecommendations, ComplianceReview | ComplianceError]):
    """AI-powered compliance officer using DSPy for structured compliance review."""

    name: str = "compliance_officer"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(ComplianceOfficerSignature))

    @override
    async def prep(self, state: PortfolioRecommendations) -> PortfolioRecommendations:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 COMPLIANCE OFFICER")
        print("   └─ Reviewing recommendations for regulatory compliance...")
        return state

    @staticmethod
    def _display_compliance_violations(error: ComplianceError) -> None:
        """Display compliance violations."""
        print("\n   🚫 Violations:")
        for violation in error.violations:
            print(f"   • {violation.rule_name}: {violation.details}")

    @staticmethod
    def _display_passed_checks(compliance_checks: tuple[ComplianceCheck, ...]) -> None:
        """Display passed compliance checks."""
        passed_checks = [c for c in compliance_checks if c.status == "pass"]
        for check in passed_checks[:3]:
            print(f"   • ✓ {check.rule_name}: {check.details}")

    @staticmethod
    def _display_warning_checks(compliance_checks: tuple[ComplianceCheck, ...]) -> None:
        """Display warning compliance checks."""
        warning_checks = [c for c in compliance_checks if c.status == "warning"]
        if warning_checks:
            print("   • Warnings:")
            for check in warning_checks:
                print(f"     ⚠️  {check.details}")

    def _display_compliance_review(self, review: ComplianceReview) -> None:
        """Display compliance review details."""
        print("\n   ✅ Compliance Checks:")
        self._display_passed_checks(review.compliance_checks)
        self._display_warning_checks(review.compliance_checks)
        if review.regulatory_notes:
            print(f"   • Regulatory Notes: {review.regulatory_notes}")
        print(f"   • Summary: {review.compliance_summary}")

    @override
    async def post(
        self, result: NodeResult[ComplianceReview | ComplianceError]
    ) -> NodeResult[ComplianceReview | ComplianceError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, ComplianceError):
            print("   ❌ Compliance violations detected")
            self._display_compliance_violations(result.state)
        else:
            print("   ✔ Compliance review approved")
            self._display_compliance_review(result.state)
        return result

    @staticmethod
    def _run_regulatory_checks(allocation_changes: tuple[AllocationChange, ...]) -> tuple[ComplianceCheck, ...]:
        """Run all regulatory compliance checks.

        Returns:
            Tuple of compliance checks with pass/fail status.
        """
        return (
            validate_position_limits(allocation_changes),
            validate_sector_concentration(allocation_changes),
            validate_allocation_sanity(allocation_changes),
        )

    @staticmethod
    def _check_for_violations(checks: tuple[ComplianceCheck, ...]) -> tuple[ComplianceCheck, ...]:
        """Filter checks for failures.

        Returns:
            Tuple of failed compliance checks only.
        """
        return tuple(check for check in checks if check.status == "fail")

    @override
    async def exec(self, state: PortfolioRecommendations) -> NodeResult[ComplianceReview | ComplianceError]:
        """Review compliance using DSPy structured prediction.

        Returns:
            NodeResult with compliance review or compliance error.
        """

        try:
            # Run regulatory compliance checks
            regulatory_checks = self._run_regulatory_checks(state.allocation_changes)
            failures = self._check_for_violations(regulatory_checks)

            if failures:
                # Regulatory violations detected
                error = ComplianceError(
                    violations=failures,
                    required_actions=tuple(f"Fix: {check.details}" for check in failures),
                    escalation_required=True,
                    failed_stage="COMPLIANCE OFFICER (compliance_officer)",
                )
                return NodeResult(error, outcome="compliance_failed")

            # Use DSPy for additional compliance review
            prediction = self._predict(recommendations=state)
            review: ComplianceReview = prediction.compliance_review

            # Merge regulatory checks with AI review
            review = ComplianceReview(
                compliance_checks=regulatory_checks + review.compliance_checks,
                overall_status=review.overall_status,
                regulatory_notes=review.regulatory_notes,
                compliance_summary=review.compliance_summary,
            )

            return NodeResult(review, outcome="compliance_approved")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create compliance error
            error_check = ComplianceCheck(
                rule_name="analysis_error",
                status="fail",
                details=f"Compliance analysis failed: {exc!s}",
            )

            error = ComplianceError(
                violations=(error_check,),
                required_actions=(
                    "Retry compliance analysis",
                    "Review input recommendations",
                ),
                escalation_required=True,
                failed_stage="COMPLIANCE OFFICER (compliance_officer)",
            )
            return NodeResult(error, outcome="compliance_failed")


@dataclass(frozen=True)
class DecisionNode(Node[ComplianceReview, TradingDecision]):
    """Final decision node using DSPy for structured trading decision."""

    name: str = "final_decision"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(TradingDecisionSignature))

    @override
    async def exec(self, state: ComplianceReview) -> NodeResult[TradingDecision]:
        """Create final trading decision using DSPy.

        Returns:
            NodeResult with trading decision.
        """

        try:
            # Use DSPy to get structured trading decision
            prediction = self._predict(compliance_review=state)
            decision: TradingDecision = prediction.trading_decision

            return NodeResult(decision, outcome="decision_ready")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create minimal trading decision on error
            decision = TradingDecision(
                approved_changes=(),
                execution_plan="Hold - unable to process decision",
                monitoring_requirements=("Monitor system status",),
                audit_trail=f"Decision processing failed: {exc!s}",
                decision_status="hold",
            )
            return NodeResult(decision, outcome="decision_ready")


@dataclass(frozen=True)
class ErrorHandler(Node[AnalysisError | RiskLimitError | ComplianceError, TradingDecision]):
    """Error handler node that converts errors to a hold decision."""

    name: str = "error_handler"

    @override
    async def exec(self, state: AnalysisError | RiskLimitError | ComplianceError) -> NodeResult[TradingDecision]:
        """Convert error state to a conservative trading decision.

        Returns:
            NodeResult with hold trading decision.
        """
        # Create error message based on error type
        if isinstance(state, AnalysisError):
            error_msg = f"Analysis Error: {state.error_message}"
        elif isinstance(state, RiskLimitError):
            error_msg = f"Risk Limit Exceeded: {', '.join(state.exceeded_limits)}"
        else:  # ComplianceError
            error_msg = f"Compliance Violation: {len(state.violations)} violations"

        # Create hold decision
        decision = TradingDecision(
            approved_changes=(),
            execution_plan="HOLD - Error in analysis pipeline",
            monitoring_requirements=(
                "Monitor error resolution",
                "Review system status",
                f"Error details: {error_msg}",
            ),
            audit_trail=f"Decision halted due to: {error_msg} at {state.failed_stage}",
            decision_status="hold",
        )
        return NodeResult(decision, outcome="error_handled")
