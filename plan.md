# ClearFlow Implementation Plan

## Critical Discovery: Flow Output Type Tracking

### Phase 1: Fix Flow Output Type Tracking ⚠️ NEW CRITICAL ISSUE
**Status**: 🔴 Not Started  
**Priority**: URGENT - Fundamental design flaw discovered

#### Task 1.1: Track termination node's output type
- Currently using `_Flow[TIn, object]` - erasing known type information
- Should be `_Flow[TIn, TOut]` where TOut comes from the termination node
- The single termination rule means we KNOW the output type statically!

#### Implementation approach:
1. In `build()`, identify the termination node (the one routing to None)
2. Extract its output type
3. Use that type for the Flow instead of `object`
4. This will dramatically improve type safety

### Phase 2: Update Tests to New API
**Status**: 🔴 Not Started  
**Priority**: HIGH (after fixing type tracking)

#### Task 2.1: Update test_flow.py
- Change from `Flow[T]("name").start_with(node)` to `flow("name", node)`
- Replace `dict[str, object]` with specific types (TicketState, WorkflowState)
- Ensure tests demonstrate real-world patterns

#### Task 2.2: Update test_real_world_scenarios.py
- Update to use flow() function
- Replace generic types with domain-specific types (RAGQueryState, ToolAgentState)
- Show educational patterns

#### Task 2.3: Update test_error_handling.py
- Update to new API
- Use proper types even in error scenarios
- Demonstrate type safety in edge cases

#### Task 2.4: Update remaining test files
- test_node_lifecycle.py
- test_async_operations.py  
- test_node.py
- Ensure all use new flow() API and proper types

### Phase 3: Update Examples
**Status**: 🔴 Not Started  
**Priority**: LOW (focus on core library first)

#### Task 3.1: Update all examples to new API
- Update to use flow() function instead of Flow class
- Showcase improved type safety once type tracking is fixed

## Completed Tasks ✅
- Fixed _Flow.exec() complexity (now rank A)
- Removed object.__setattr__ mutation
- Replaced hasattr with Protocol types (NodeBase)
- Simplified _FlowBuilder (removed misleading TCurrent)
- Reduced suppressions from 14 to 4 (71% reduction)
- Core library passes all quality checks

## Success Metrics
- ⏳ Fix flow output type tracking (discovered fundamental issue)
- ⏳ Update all tests to new flow() API  
- ⏳ Maintain 100% test coverage
- ⏳ Update examples to showcase type safety