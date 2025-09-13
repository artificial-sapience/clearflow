# Message Flow API Redesign Plan

## Executive Summary

Redesign the message_flow API to use explicit source nodes in routing (like the original flow API) instead of the current `from_node()` grouping approach. This change will improve UX by enabling sequential thinking about workflows rather than node-centric thinking.

**Core Design Principle**: The message_flow API should provide the EXACT same UX as the original flow API, just with message types instead of state objects and message types instead of string outcomes. All constraints remain identical (single termination, orphan checking, reachability validation).

## Problem Statement

Current API forces awkward patterns:

- **Node-centric thinking**: Must group all routes from a node together
- **Single end() restriction**: Can only call `.end()` once, forcing reordering
- **Loop handling**: Awkward to express "some outputs continue, one terminates"
- **Breaks flow narrative**: Can't define routes in logical sequence

## Solution: Explicit Source Node API

Return to explicit source nodes in each route call, maintaining the EXACT same UX as the original flow API but with message types:

```python
# Original flow API (for reference)
flow("Name", start_node)
.route(source_node, "outcome_string", dest_node)
.end(final_node, "outcome_string")  # Single termination enforced

# New message_flow API (same UX, different types)
message_flow("Name", start_node)
.route(source_node, MessageType, dest_node)
.route(source_node, MessageType, dest_node)
.end(source_node, MessageType)  # Single termination enforced
```

**Key principle**: The message_flow API should feel IDENTICAL to the flow API, just replacing:

- State objects → Message types
- String outcomes → Event/Message types
- Everything else remains the same (single termination, orphan checking, reachability validation)

## What Stays the Same (from flow API)

These constraints and features from the original flow API MUST be preserved:

1. **Single termination enforcement** - Exactly one `.end()` call allowed
2. **Orphan node detection** - All nodes must be reachable from start
3. **Reachability validation** - Can only route from reachable nodes
4. **Route uniqueness** - Each (node, outcome) pair can only have one route
5. **Explicit routing** - All outcomes must be explicitly handled
6. **Builder pattern** - Fluent interface for flow construction
7. **Type safety** - Full type inference and checking

The ONLY changes are:

- Use message types instead of state objects
- Use message types instead of string outcomes for routing
- Nodes process messages instead of state

## Critical Quality Requirement

**EVERY task must end with running `./quality-check.sh` on affected files**

- No task is complete until quality checks pass 100%
- No suppressions allowed without explicit user approval
- Fix root causes, never suppress violations
- Cannot proceed to next task with any quality failures

## Implementation Phases

### Phase 1: Core API Redesign

#### Task 1.1: Update message_flow.py Core Classes

- [ ] Modify `_MessageFlowBuilder` to accept source node in `route()` method
- [ ] Remove `from_node()` method and `_MessageFlowBuilderContext` class
- [ ] Update `route()` signature: `route(from_node, message_type, to_node)`
- [ ] Update `end()` signature: `end(from_node, message_type)`
- [ ] **MAINTAIN single termination enforcement** (exactly one `.end()` call allowed)
- [ ] Keep orphan node detection and reachability validation (same as flow API)
- [ ] Update type parameter tracking for new signature
- [ ] **Run `./quality-check.sh clearflow/message_flow.py` - MUST PASS 100%**

#### Task 1.2: Update Route Storage and Validation

- [ ] Ensure route keys still use `(message_type, node_name)` tuple
- [ ] Update reachability tracking to work with explicit sources
- [ ] Validate that source nodes are reachable before adding routes
- [ ] Enforce single termination point (only one route to None)
- [ ] Detect and prevent orphan nodes (unreachable from start)
- [ ] **Run `./quality-check.sh clearflow/message_flow.py` - MUST PASS 100%**

#### Task 1.3: Type Safety Updates

- [ ] Ensure type inference works with explicit source nodes
- [ ] Validate message type compatibility between nodes
- [ ] Update generic type parameters to maintain type safety
- [ ] Test that pyright strict mode still passes
- [ ] **Run `./quality-check.sh clearflow/` - MUST PASS 100%**

### Phase 2: Testing and Validation

#### Task 2.1: Update Core Framework Tests

- [ ] Update all MessageFlow tests in tests/test_message_flow.py
- [ ] Add tests for single termination enforcement
- [ ] Add tests for loops with termination
- [ ] Add tests for orphan node detection
- [ ] Ensure 100% test coverage maintained
- [ ] **Run `./quality-check.sh tests/test_message_flow.py` - MUST PASS 100%**

#### Task 2.2: Full Codebase Quality Compliance

- [ ] **Run `./quality-check.sh` on entire codebase - MUST PASS 100%**
- [ ] Fix any architecture compliance violations (NO suppressions)
- [ ] Fix any immutability violations (NO suppressions)
- [ ] Fix any type checking errors (NO suppressions)
- [ ] Fix any linting issues (NO suppressions)
- [ ] Fix any complexity violations (NO suppressions)
- [ ] Fix any dead code issues (NO suppressions)
- [ ] Ensure 100% test coverage maintained
- [ ] **Final run: `./quality-check.sh` - MUST PASS with ZERO violations**

#### Task 2.3: Integration Testing

- [ ] Test chat example with real OpenAI API
- [ ] Test portfolio example with DSPy integration
- [ ] Test RAG example with FAISS vector search
- [ ] Verify all examples handle errors gracefully
- [ ] **Run `./quality-check.sh examples/` - MUST PASS 100%**

### Phase 3: Example Updates

#### Task 3.1: Update chat_message_driven Example

- [ ] Refactor chat_flow.py to use explicit source nodes
- [ ] Simplify the flow to natural sequence:

  ```python
  .route(user, UserMessageReceived, assistant)
  .route(assistant, AssistantMessageSent, user)
  .end(user, ChatEnded)
  ```

- [ ] Ensure example still demonstrates familiar chat pattern
- [ ] Verify the simplified architecture still works
- [ ] **Run `./quality-check.sh examples/chat_message_driven/` - MUST PASS 100%**

#### Task 3.2: Update portfolio_analysis_message_driven Example

- [ ] Refactor portfolio_flow.py to use explicit source nodes
- [ ] Maintain convergence pattern (multiple nodes → decision)
- [ ] Update all route definitions with source nodes
- [ ] Verify error handling paths still work
- [ ] **Run `./quality-check.sh examples/portfolio_analysis_message_driven/` - MUST PASS 100%**

#### Task 3.3: Update rag_message_driven Example

- [ ] Refactor rag_flows.py to use explicit source nodes
- [ ] Update both indexing and query flows
- [ ] Ensure the two-phase pattern still works
- [ ] Verify FAISS integration remains functional
- [ ] **Run `./quality-check.sh examples/rag_message_driven/` - MUST PASS 100%**

### Phase 4: Documentation

#### Task 4.1: Update API Documentation

- [ ] Update message_flow.py docstrings
- [ ] Document the explicit routing pattern
- [ ] Add examples showing loops and convergence
- [ ] Document migration from from_node() pattern
- [ ] **Run `./quality-check.sh clearflow/message_flow.py` - MUST PASS 100%**

#### Task 4.2: Update Example READMEs

- [ ] Create/update README for chat_message_driven
- [ ] Update README for portfolio_analysis_message_driven
- [ ] Update README for rag_message_driven
- [ ] Include clear flow diagrams
- [ ] **Run `./quality-check.sh examples/` - MUST PASS 100%**

### Phase 5: Migration Support

#### Task 5.1: Migration Guide

- [ ] Document breaking changes
- [ ] Provide before/after examples
- [ ] Show how to convert from_node() patterns
- [ ] Include common patterns (loops, convergence, termination)
- [ ] **Run `./quality-check.sh` on any new files - MUST PASS 100%**

#### Task 5.2: Final Validation

- [ ] Verify all examples run successfully
- [ ] Confirm backwards compatibility decisions
- [ ] Document upgrade path for existing code
- [ ] **FINAL: Run `./quality-check.sh` - MUST PASS 100% with ZERO violations**

## Success Criteria

1. **Intuitive API**: Flows read sequentially like a story (same as flow API)
2. **All patterns supported**: Loops, convergence, single termination enforced
3. **Type safety maintained**: Full pyright strict compliance
4. **Quality compliance**: Zero violations across entire codebase
5. **Examples work**: All three examples functional with real APIs
6. **Quality gates**: Every task passes `./quality-check.sh` 100%
7. **UX parity**: Feels identical to flow API, just with message types

## Risk Mitigation

- **Risk**: Breaking existing code
  - **Mitigation**: Clear migration guide, consider deprecation period

- **Risk**: Type inference complexity
  - **Mitigation**: Extensive testing, may need cast() in complex cases

- **Risk**: Performance impact
  - **Mitigation**: Profile before/after, optimize if needed

- **Risk**: Quality regressions
  - **Mitigation**: Run quality checks after EVERY change, fix immediately

## Timeline Estimate

- Phase 1 (Core API): 2-3 hours
- Phase 2 (Examples): 1-2 hours
- Phase 3 (Testing): 1-2 hours
- Phase 4 (Documentation): 1 hour
- Phase 5 (Migration): 1 hour

**Total: 6-9 hours of focused work**

## Next Immediate Steps

1. Start with Phase 1, Task 1.1 - modify core message_flow.py
2. **Run `./quality-check.sh clearflow/message_flow.py` - fix ALL violations**
3. Only proceed to next task after 100% quality compliance
4. Continue pattern: implement → quality check → fix → verify → next task
