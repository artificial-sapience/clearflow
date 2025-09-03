"""DSPy signatures for AI-powered financial specialists."""
# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

import dspy

from examples.portfolio_analysis.models_pydantic import (
    ComplianceError,
    ComplianceReview,
    MarketData,
    PortfolioRecommendations,
    QuantInsights,
    RiskAssessment,
    RiskLimitError,
    TradingDecision,
)


class QuantAnalystSignature(dspy.Signature):
    """Analyze market data to identify investment opportunities.

    You are a senior quantitative analyst at a top-tier investment firm.

    REGULATORY CONSTRAINTS (must be respected):
    - Maximum 15% allocation per individual asset
    - Maximum 40% allocation per sector
    - All allocations must be positive and sum to ≤100%

    Focus on:
    - Market momentum and technical indicators
    - Sector rotation opportunities
    - Risk-adjusted return potential
    - Short-term tactical positioning

    Provide specific, actionable insights that respect the above constraints.
    Include confidence levels for your recommendations.
    """

    market_data: MarketData = dspy.InputField(
        desc="Current market conditions including asset prices, volumes, and sentiment"
    )
    insights: QuantInsights = dspy.OutputField(
        desc="Quantitative analysis with trend assessment, opportunities, and confidence"
    )


class RiskAnalystSignature(dspy.Signature):
    """Perform holistic risk analysis using professional judgment.

    You are a senior risk analyst evaluating portfolio risks contextually.

    Be aware of regulatory constraints:
    - Maximum 15% per asset, 40% per sector
    - These are hard limits that cannot be exceeded

    Assess risks holistically considering:
    - VaR relative to portfolio size and investor risk tolerance
    - Drawdown risk in context of current market volatility
    - Concentration risks that could amplify losses
    - Systemic and correlation risks
    - Stress scenarios based on historical precedents

    Use your professional judgment to:
    - Set risk_level (low/medium/high/extreme) based on overall assessment
    - Generate realistic risk metrics appropriate for the portfolio
    - Identify material risks that need attention
    - Consider market conditions when evaluating acceptability

    Focus on actionable risk insights, not arbitrary thresholds.
    """

    quant_insights: QuantInsights = dspy.InputField(
        desc="Quantitative analysis with identified opportunities"
    )
    risk_assessment: RiskAssessment = dspy.OutputField(
        desc="Comprehensive risk metrics and warnings"
    )


class PortfolioManagerSignature(dspy.Signature):
    """Develop strategic portfolio allocation recommendations.

    You are a seasoned portfolio manager making allocation decisions.

    MANDATORY REGULATORY LIMITS:
    - Maximum 15% allocation per asset
    - Maximum 40% allocation per sector
    - Allocations must be non-negative and sum to ≤100%

    Consider:
    - Risk-adjusted returns across opportunities
    - Portfolio diversification requirements
    - Implementation complexity and costs
    - Market timing and execution strategy

    Balance opportunity with prudent risk management.
    """

    risk_assessment: RiskAssessment = dspy.InputField(
        desc="Risk analysis including metrics and warnings"
    )
    recommendations: PortfolioRecommendations = dspy.OutputField(
        desc="Strategic allocation changes with thesis and timeline"
    )


class ComplianceOfficerSignature(dspy.Signature):
    """Review portfolio recommendations for regulatory compliance.

    You are a chief compliance officer ensuring regulatory adherence.
    Check for:
    - Position limit violations (max 15% per asset)
    - Sector concentration limits (max 40% per sector)
    - Documentation requirements
    - Execution timeline appropriateness
    - Regulatory reporting needs

    Be thorough and conservative in compliance assessments.
    """

    recommendations: PortfolioRecommendations = dspy.InputField(
        desc="Portfolio manager's allocation recommendations"
    )
    compliance_review: ComplianceReview = dspy.OutputField(
        desc="Detailed compliance checks and overall approval status"
    )


class TradingDecisionSignature(dspy.Signature):
    """Finalize trading decision based on compliance review.

    You are the head of trading finalizing execution plans.
    Determine:
    - Which allocation changes to execute
    - Detailed execution instructions
    - Monitoring requirements
    - Escalation needs

    Create a clear, actionable trading plan.
    """

    compliance_review: ComplianceReview = dspy.InputField(
        desc="Compliance review with checks and approval status"
    )
    trading_decision: TradingDecision = dspy.OutputField(
        desc="Final trading decision with execution plan"
    )


# Alternative signatures for error handling paths
class RiskLimitSignature(dspy.Signature):
    """Evaluate if risk limits are exceeded and recommend mitigation."""

    risk_assessment: RiskAssessment = dspy.InputField(
        desc="Risk assessment with metrics"
    )
    risk_limit_check: RiskLimitError | None = dspy.OutputField(
        desc="Risk limit error if thresholds exceeded, None if acceptable"
    )


class ComplianceViolationSignature(dspy.Signature):
    """Identify compliance violations and required actions."""

    recommendations: PortfolioRecommendations = dspy.InputField(
        desc="Portfolio recommendations to check"
    )
    compliance_error: ComplianceError | None = dspy.OutputField(
        desc="Compliance error if violations found, None if compliant"
    )
