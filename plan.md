# ClearFlow Examples Improvement Plan

## Current Objective
Improve ClearFlow examples to demonstrate best practices while maintaining architectural constraints (immutability, stateless observers where possible, no suppressions).

## Active Task: DSPy Pydantic Model Refactoring
Refactoring portfolio analysis example to better leverage DSPy's structured output capabilities.

### In Progress
- [ ] **Updating specialist models** - Started with Quant Analyst
  - [x] Quant Analyst models simplified
  - [ ] Risk Analyst models
  - [ ] Portfolio Manager models
  - [ ] Compliance Officer models
  - [ ] Decision Maker models

### Pending Tasks
1. [ ] **Update DSPy signatures** to match new models
2. [ ] **Update events** to pass models directly without transformation
3. [ ] **Update nodes** to use new models
4. [ ] **Update observer** for console display (fail-fast, no error handling)
5. [ ] **Fix remaining pyright type errors** (83 errors related to attribute access)
6. [ ] **Run full quality check** and fix any remaining issues

## Key Constraints Discovered
- Observers need minimal state for spinners (single `_current_spinner` field)
- Must use `Sequence` instead of `list` for immutability
- Cannot use `Any` or `object` types
- Cannot suppress linting errors without explicit approval
- TYPE_CHECKING imports conflict with architecture linter

## Completed Tasks
✅ Added Rich-based SpinnerContext for async operations
✅ Created AsyncSpinnerObserver for node-specific spinners
✅ Fixed datetime timezone issues (using UTC)
✅ Converted static methods to module functions in portfolio observer
✅ Simplified complex _print_decision_summary method
✅ Added Returns sections to docstrings
✅ Removed Status type annotations to avoid TC002 issues