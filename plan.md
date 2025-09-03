# ClearFlow Development Plan

## Current Branch: support-state-type-transformations

## Immediate Priority: Type Safety Improvements
- [ ] Add targeted type ignores for DSPy dynamic attributes while preserving type safety for Pydantic models
- [ ] Run quality checks to ensure type checking works properly with targeted ignores

## Documentation Tasks  
- [ ] Document the DSPy integration pattern in examples README
- [ ] Add explanation of AI vs hard-coded rules philosophy
- [ ] Create brief guide on "When to use regulatory validators vs AI judgment"

## Testing & Validation
- [ ] Consider adding integration tests to catch runtime issues that static analysis misses
- [ ] Test portfolio example end-to-end with real OpenAI API
- [ ] Verify all three scenarios work correctly (normal, bullish, volatile)

## Recently Completed in This Session ✅
- Enhanced AI output display in Node.post() methods to show detailed insights from each team member
- Refactored display methods from Grade B/C complexity to Grade A through targeted helper extraction
- Fixed AttributeError: `market_regime` → `market_trend` (runtime bug missed by static analysis)
- Analyzed why linters missed the AttributeError: overly broad file-level type suppressions
- Removed broad pyright suppressions from nodes.py (`reportAttributeAccessIssue=false`, etc.)
- Copied DSPy type stubs from Sociocracy project to `/typings/dspy/`
- Updated pyproject.toml to use DSPy type stubs (`stubPath = "typings"`, `mypy_path = "typings"`)
- All quality checks passing except for 48 legitimate type errors that need targeted handling

## Key Insights from This Session
- **Static analysis limitation**: Pydantic runtime field validation vs static dataclass analysis
- **Suppression scope matters**: Broad file-level suppressions hide real bugs, targeted line-level suppressions are better
- **Integration testing gaps**: Need runtime tests for DSPy+Pydantic+OpenAI integration
- **Type stub effectiveness**: DSPy stubs help but dynamic attributes still need targeted handling