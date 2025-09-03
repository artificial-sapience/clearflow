# Portfolio Analysis Example

AI-powered portfolio management team demonstrating mission-critical financial decision-making workflows.

## Overview

This example showcases **multiple AI specialists** working together as a coordinated team to analyze market conditions and make portfolio allocation decisions. Each node represents a different financial expert with specialized reasoning capabilities.

## Business Value

Demonstrates the type of **mission-critical AI orchestration** that financial institutions need:

- **Multi-agent coordination** - Different AI specialists with distinct expertise
- **Type-safe financial workflows** - Precise data flow between analysis stages  
- **Risk management integration** - Comprehensive checks before trading decisions
- **Regulatory compliance** - Automated validation against financial rules
- **Audit trail** - Clear reasoning chain for regulatory review

## AI Team Members

Each node uses language model intelligence for specialized financial reasoning:

### 1. **QuantAnalyst**

- Analyzes market trends and technical indicators
- Calculates momentum, volatility, and correlation metrics
- Identifies investment opportunities with confidence scores

### 2. **RiskAnalyst**

- Performs stress testing and scenario analysis
- Calculates Value-at-Risk (VaR) and exposure limits
- Assesses portfolio concentration and correlation risks

### 3. **PortfolioManager**

- Synthesizes quantitative and risk analysis
- Makes strategic allocation decisions based on investment thesis
- Balances returns, risk, and client objectives

### 4. **ComplianceOfficer**

- Reviews proposed trades against regulatory requirements
- Validates position limits and client mandates
- Ensures adherence to investment policies

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
```

## Usage

```bash
python main.py
```

The system will:

1. Load simulated market data for major asset classes
2. Run quantitative analysis to identify opportunities
3. Perform risk assessment and stress testing
4. Generate portfolio allocation recommendations
5. Validate compliance with investment policies
6. Display the complete analysis chain with reasoning

## Flow Structure

```mermaid
graph LR
    Start([Market Data]) --> Q[QuantAnalyst]
    Q -->|insights| R[RiskAnalyst]
    Q -->|analysis_failed| E[ErrorHandler]
    R -->|risk_assessed| P[PortfolioManager]
    R -->|high_risk| E
    P -->|recommendations| C[ComplianceOfficer]
    P -->|no_opportunities| T[Terminal]
    C -->|approved| T[Terminal]
    C -->|rejected| E
    E -->|handled| T
    T -->|completed| End([Final Decision])
```

**Node Outcomes:**

- `QuantAnalyst`: insights/analysis_failed
- `RiskAnalyst`: risk_assessed/high_risk  
- `PortfolioManager`: recommendations/no_opportunities
- `ComplianceOfficer`: approved/rejected
- `ErrorHandler`: handled
- `Terminal`: completed (→ End)

## Key Features

- **Multiple LM calls** - Each specialist uses AI reasoning, not just data processing
- **Type-safe transformations** - `MarketData → QuantInsights → RiskAssessment → Recommendations → Compliance → Decision`
- **Intelligent error handling** - AI-powered recovery and escalation
- **Mission-critical reliability** - Proper validation and audit trails
- **Real business logic** - Actual portfolio management decision-making

## Example Output

```text
🏦 AI PORTFOLIO MANAGEMENT TEAM
════════════════════════════════

📊 Quantitative Analysis:
• Market momentum: Bullish trend in technology sector
• Volatility: Elevated in emerging markets (22% vs 15% historical)  
• Opportunities: Growth stocks showing oversold conditions

⚠️ Risk Assessment:
• Portfolio VaR: $1.2M (within $2M limit)
• Concentration risk: High exposure to tech sector (35%)
• Correlation: Increased during market stress

🎯 Portfolio Recommendations:
• Reduce tech allocation from 35% → 25%
• Increase defensive positions (utilities, healthcare)
• Hedge emerging market exposure

✅ Compliance Review:
• All recommendations within client mandate
• Position limits respected
• ESG criteria maintained

💼 Final Decision: APPROVED
• Execute rebalancing over 3-day period
• Monitor for adverse market movements
• Review allocation in 30 days
```

## Customization

- **Market Data**: Modify `market_data.py` to simulate different market conditions
- **Risk Limits**: Adjust parameters in `RiskAnalyst` node
- **Investment Strategy**: Update logic in `PortfolioManager` node  
- **Compliance Rules**: Configure policies in `ComplianceOfficer` node

This example demonstrates how ClearFlow orchestrates **specialized AI reasoning** for mission-critical financial applications - exactly what our target audience builds for banks, hedge funds, and asset managers.
