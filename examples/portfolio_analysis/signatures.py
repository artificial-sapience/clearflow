"""DSPy signatures for AI-powered financial specialists."""
# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

import dspy

from examples.portfolio_analysis.models import (
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

    CRITICAL REQUIREMENT:
    You MUST ONLY analyze and recommend the assets that are present in the provided market_data.
    Do NOT introduce any ticker symbols that are not in the input data.
    The available assets will be clearly listed in the market_data.assets field.

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
    Your opportunities MUST reference ONLY symbols from the provided market data.
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

    CRITICAL REQUIREMENT:
    You MUST ONLY assess risks for the assets identified in the quant_insights.
    Do NOT reference any ticker symbols that are not in the opportunities provided.
    Focus your analysis exclusively on the symbols present in the input.

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
    Your concentration_risk MUST reference ONLY symbols from the quant insights.
    """

    quant_insights: QuantInsights = dspy.InputField(desc="Quantitative analysis with identified opportunities")
    risk_assessment: RiskAssessment = dspy.OutputField(desc="Comprehensive risk metrics and warnings")


class PortfolioManagerSignature(dspy.Signature):
    """Develop strategic portfolio allocation recommendations.

    You are a seasoned portfolio manager making allocation decisions.

    CRITICAL REQUIREMENT:
    You MUST ONLY recommend allocation changes for assets present in the risk_assessment.
    Do NOT introduce any new ticker symbols not found in the input data.
    Your allocation_changes MUST use ONLY the symbols that have been analyzed.

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
    All AllocationChange entries MUST reference ONLY symbols from the risk assessment.
    """

    risk_assessment: RiskAssessment = dspy.InputField(desc="Risk analysis including metrics and warnings")
    recommendations: PortfolioRecommendations = dspy.OutputField(
        desc="Strategic allocation changes with thesis and timeline"
    )


class ComplianceOfficerSignature(dspy.Signature):
    """Review portfolio recommendations for regulatory compliance.

    You are a chief compliance officer ensuring regulatory adherence.

    CRITICAL REQUIREMENT:
    You MUST ONLY review allocations for the symbols present in the recommendations.
    Do NOT reference any ticker symbols not found in the allocation_changes.

    Check for:
    - Position limit violations (max 15% per asset)
    - Sector concentration limits (max 40% per sector)
    - Documentation requirements
    - Execution timeline appropriateness
    - Regulatory reporting needs

    Be thorough and conservative in compliance assessments.
    Focus your review ONLY on the symbols provided in the portfolio recommendations.
    """

    recommendations: PortfolioRecommendations = dspy.InputField(desc="Portfolio manager's allocation recommendations")
    compliance_review: ComplianceReview = dspy.OutputField(
        desc="Detailed compliance checks and overall approval status"
    )


class TradingDecisionSignature(dspy.Signature):
    """Finalize trading decision based on compliance review.

    You are the head of trading finalizing execution plans.

    CRITICAL REQUIREMENT:
    You MUST ONLY approve changes for symbols that were in the compliance review.
    Do NOT introduce any new ticker symbols.

    Determine:
    - Which allocation changes to execute
    - Detailed execution instructions
    - Monitoring requirements
    - Escalation needs

    Create a clear, actionable trading plan.
    Your approved_changes MUST reference ONLY symbols from the compliance review.
    """

    compliance_review: ComplianceReview = dspy.InputField(desc="Compliance review with checks and approval status")
    trading_decision: TradingDecision = dspy.OutputField(desc="Final trading decision with execution plan")


# Alternative signatures for error handling paths
class RiskLimitSignature(dspy.Signature):
    """Evaluate if risk limits are exceeded and recommend mitigation."""

    risk_assessment: RiskAssessment = dspy.InputField(desc="Risk assessment with metrics")
    risk_limit_check: RiskLimitError | None = dspy.OutputField(
        desc="Risk limit error if thresholds exceeded, None if acceptable"
    )


class ComplianceViolationSignature(dspy.Signature):
    """Identify compliance violations and required actions."""

    recommendations: PortfolioRecommendations = dspy.InputField(desc="Portfolio recommendations to check")
    compliance_error: ComplianceError | None = dspy.OutputField(
        desc="Compliance error if violations found, None if compliant"
    )
