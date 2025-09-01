# ClearFlow Type Transformation Implementation Plan

## Overview
Transform ClearFlow from supporting only `Node[T]` to supporting type-transforming nodes `Node[TIn, TOut=TIn]`.

## Remaining Tasks

### Phase 1: Fix Test Type Specificity
**Status**: 🔴 Not Started  
**Priority**: CRITICAL - Blocking quality checks

The tests currently use `dict[str, object]` which defeats the educational purpose. Tests should demonstrate real-world usage with specific types.

#### Task 1.1: Update test_flow.py
- Replace `dict[str, object]` with specific TypedDict or dataclass types
- Each test should model a real scenario with proper types
- Examples: TicketState, WorkflowState, ChatState

#### Task 1.2: Update test_real_world_scenarios.py  
- Replace `dict[str, object]` with domain-specific types
- RAG pipeline should use RAGQueryState, RAGResponseState
- Tool agent should use ToolAgentState with proper fields

#### Task 1.3: Update test_error_handling.py
- Even error tests should use proper types
- Demonstrates that type safety works even in edge cases

### Phase 2: Fix Remaining Architecture Violations
**Status**: 🟡 In Progress  
**Priority**: HIGH

#### Task 2.1: Fix parameter violation in clearflow/__init__.py
- Line 134: `from_node: object` parameter needs suppression
- Add inline justification comment

#### Task 2.2: Verify all suppressions are working
- Ensure linter recognizes all `# clearflow: ignore[ARCH009]` comments
- Should have 0 violations with justified suppressions

### Phase 3: Create Type Transformation Examples
**Status**: 🔴 Not Started  
**Priority**: MEDIUM

#### Task 3.1: Create RAG Pipeline Example
**File**: `examples/rag_pipeline/`
- Show Query → SearchResults → Context → Response transformations
- Demonstrate type safety without isinstance checks
- Include README explaining the pattern

#### Task 3.2: Create Tool Orchestration Example
**File**: `examples/tool_orchestration/`
- Show ToolQuery → ToolPlan → ToolExecution → ToolResult
- Demonstrate how types prevent errors
- Show benefits vs "god object" pattern

### Phase 4: Documentation Updates
**Status**: 🔴 Not Started  
**Priority**: LOW

#### Task 4.1: Update README
- Add type transformation examples
- Document the `Node[TIn, TOut=TIn]` pattern
- Show migration from `Node[T]` (if any breaking changes)

#### Task 4.2: Write Blog Post or Tutorial
- "Type-Safe AI Orchestration Without God Objects"
- Show problems with dict[str, Any] everywhere
- Demonstrate ClearFlow's solution

## Success Metrics
- ✅ 100% test coverage maintained
- ❌ 0 architecture violations (currently 46)
- ✅ All tools using pyproject.toml where possible
- ✅ Examples use proper types (no Any)
- ❌ Tests use proper types (not object)
- ✅ Documentation explains type transformations clearly

## Next Session Priority
1. Fix test type specificity (Phase 1) - Educational value
2. Complete architecture compliance (Phase 2) 
3. Create examples (Phase 3) - Show real-world usage