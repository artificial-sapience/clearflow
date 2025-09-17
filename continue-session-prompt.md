# Continue Session: Magic String Detection & Type Safety

## Context
See `session-context.md` for the full details of our type safety improvements and documentation enhancements.

## Summary of Completed Work
- ✅ Added alpha version warning to README.md with pinning recommendation
- ✅ Enhanced all Pydantic models with LLM-friendly field descriptions
- ✅ Implemented Literal types for compile-time validation in portfolio analysis
- ✅ Researched existing linter solutions for magic string detection

## Your Next Mission
Help implement automated detection of magic strings and hardcoded literals that should use Literal types or constants. See `plan.md` for the current task list.

## Primary Implementation Options

### Option 1: Configure Existing Linters
Enable and configure ruff's PLR2004 (magic-value-comparison) rule:
- Add to pyproject.toml ruff configuration
- Configure allowed magic values
- Test on existing codebase

### Option 2: Create Custom ClearFlow Linter
Build a specialized linter for ClearFlow-specific patterns:
- Detect fields that should use NodeName/ErrorType literals
- Check for string assignments to known enumerated fields
- Integrate with quality-check.sh pipeline

### Option 3: Hybrid Approach
Combine both for maximum coverage:
- Use ruff PLR2004 for general magic string detection
- Add custom linter for domain-specific rules
- Document when to use each approach

## Specific Tasks

1. **Implement Magic String Detection**
   - Choose implementation approach
   - Configure or create linter
   - Add to quality-check.sh pipeline
   - Test on portfolio analysis example

2. **Expand Literal Type Usage**
   - Review other examples for string literal usage
   - Identify additional candidates for Literal types
   - Create type aliases where appropriate

3. **Documentation Updates**
   - Update contributing guidelines with type safety rules
   - Document how to add new Literal types
   - Create migration guide for existing code

## Success Criteria
- [ ] Magic strings are automatically detected in CI/CD
- [ ] All examples use appropriate Literal types
- [ ] Type safety patterns are well-documented
- [ ] Quality checks include type safety validation

## Start By
1. Review the existing linter architecture in `linters/` directory
2. Test ruff's PLR2004 rule on the codebase
3. Identify ClearFlow-specific patterns that need custom detection
4. Implement chosen solution with tests

Please consider the trade-offs between simplicity (using existing tools) and specificity (custom linter) before proceeding.