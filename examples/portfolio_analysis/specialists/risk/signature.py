"""DSPy signatures for Risk Analyst."""

import dspy

from examples.portfolio_analysis.specialists.quant.models import QuantInsights
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment


class RiskAnalystSignature(dspy.Signature):
    """Perform holistic risk analysis using professional judgment.

    You are a senior risk analyst evaluating portfolio risks contextually.

    CRITICAL REQUIREMENT:
    You MUST ONLY assess risks for the assets identified in the quant_insights.
    Do NOT reference any ticker symbols that are not in the top_signals provided.
    Focus your analysis exclusively on the symbols present in the input.

    Be aware of regulatory constraints:
    - Maximum 15% per asset, 40% per sector
    - These are hard limits that cannot be exceeded

    Assess risks holistically considering:
    - VaR relative to portfolio size and investor risk tolerance
    - Sharpe ratio for risk-adjusted return assessment
    - Concentration risks that could amplify losses
    - Stress scenarios based on historical precedents

    Use your professional judgment to:
    - Set risk_level (low/medium/high/extreme) based on overall assessment
    - Generate realistic risk metrics appropriate for the portfolio
    - Identify concentration risks by sector or asset
    - Consider market conditions when evaluating acceptability

    Focus on actionable risk insights, not arbitrary thresholds.
    Your concentration_risks MUST reference ONLY symbols from the quant insights.
    """

    quant_insights: QuantInsights = dspy.InputField(desc="Quantitative analysis with identified signals")
    risk_assessment: RiskAssessment = dspy.OutputField(desc="Comprehensive risk metrics and warnings")
