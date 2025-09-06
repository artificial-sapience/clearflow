# ClearFlow Development Plan

## Current Branch: `support-state-type-transformations`

## Immediate Priority: Fix Portfolio Example Issues 🚨

### 1. Critical Bugs in Portfolio Analysis Example
- [ ] Fix market sentiment randomization in "normal" scenario
  - `market_data.py:147` should use "neutral" for normal scenario, not random
- [ ] Constrain LLM outputs to provided ticker symbols
  - Update ALL DSPy signatures to explicitly state: "You MUST ONLY use symbols from the provided data"
  - QuantAnalyst: "Only analyze these assets: [list]"
  - RiskAnalyst: "Only assess risks for these assets: [list]"
  - PortfolioManager: "Only recommend changes for these symbols: [list]"
  - Pass symbol list as part of each agent's input/context
- [ ] Add validation to AllocationChange model to verify symbols exist in input
- [ ] Test all three scenarios to ensure consistent behavior

### 2. Examples Review 🛡️
- [ ] Review chat example for similar issues
- [ ] Verify all examples follow best practices
- [ ] Ensure no LLM hallucination can leak real-world data

### 3. Final Code Review 🔍
- [ ] Review all type transformations for correctness
- [ ] Verify Node protocol implementation is solid
- [ ] Ensure documentation matches implementation

### 4. PR Preparation 📋
- [ ] Final quality-check.sh run
- [ ] Create detailed PR description including:
  - Type transformation support  
  - Flow builder validation (reachability & duplicate routes)
  - Custom linters for mission-critical compliance
  - Documentation improvements
  - Portfolio example bug fixes
- [ ] Submit PR for review

## Recently Completed (This Session)
- ✅ Added build-time validation for flow builder
- ✅ Implemented reachability checking for nodes
- ✅ Added duplicate route detection
- ✅ Refactored validation logic to eliminate duplication
- ✅ Updated README with new tagline: "Type-safe orchestration for unpredictable AI"
- ✅ Fixed T-800 example in quickstart