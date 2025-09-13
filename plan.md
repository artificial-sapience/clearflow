# Message Flow API Redesign Plan

## Executive Summary

Redesign the message_flow API to use explicit source nodes in routing (like the original flow API) instead of the current `from_node()` grouping approach. This change will improve UX by enabling sequential thinking about workflows rather than node-centric thinking.

## Problem Statement

Current API forces awkward patterns:
- **Node-centric thinking**: Must group all routes from a node together
- **Single end() restriction**: Can only call `.end()` once, forcing reordering
- **Loop handling**: Awkward to express "some outputs continue, one terminates"
- **Breaks flow narrative**: Can't define routes in logical sequence

## Solution: Explicit Source Node API

Return to explicit source nodes in each route call:
```python
message_flow("Name", start_node)
.route(source_node, MessageType, dest_node)
.route(source_node, MessageType, dest_node)
.end(source_node, MessageType)
```

## Implementation Phases

### Phase 1: Core API Redesign

#### Task 1.1: Update message_flow.py Core Classes
- [ ] Modify `_MessageFlowBuilder` to accept source node in `route()` method
- [ ] Remove `from_node()` method and `_MessageFlowBuilderContext` class
- [ ] Update `route()` signature: `route(from_node, message_type, to_node)`
- [ ] Update `end()` signature: `end(from_node, message_type)`
- [ ] Remove the single termination restriction (allow multiple `end()` calls)
- [ ] Update type parameter tracking for new signature

#### Task 1.2: Update Route Storage and Validation
- [ ] Ensure route keys still use `(message_type, node_name)` tuple
- [ ] Update reachability tracking to work with explicit sources
- [ ] Validate that source nodes are reachable before adding routes
- [ ] Handle multiple termination points correctly

#### Task 1.3: Type Safety Updates
- [ ] Ensure type inference works with explicit source nodes
- [ ] Validate message type compatibility between nodes
- [ ] Update generic type parameters to maintain type safety
- [ ] Test that pyright strict mode still passes

### Phase 2: Example Updates

#### Task 2.1: Update chat_message_driven Example
- [ ] Refactor chat_flow.py to use explicit source nodes
- [ ] Simplify the flow to natural sequence:
  ```python
  .route(user, UserMessageReceived, assistant)
  .route(assistant, AssistantMessageSent, user)
  .end(user, ChatEnded)
  ```
- [ ] Ensure example still demonstrates familiar chat pattern
- [ ] Verify the simplified architecture still works

#### Task 2.2: Update portfolio_analysis_message_driven Example
- [ ] Refactor portfolio_flow.py to use explicit source nodes
- [ ] Maintain convergence pattern (multiple nodes ’ decision)
- [ ] Update all route definitions with source nodes
- [ ] Verify error handling paths still work

#### Task 2.3: Update rag_message_driven Example
- [ ] Refactor rag_flows.py to use explicit source nodes
- [ ] Update both indexing and query flows
- [ ] Ensure the two-phase pattern still works
- [ ] Verify FAISS integration remains functional

### Phase 3: Testing and Validation

#### Task 3.1: Update Core Framework Tests
- [ ] Update all MessageFlow tests in tests/test_message_flow.py
- [ ] Add tests for multiple termination points
- [ ] Add tests for loops with termination
- [ ] Ensure 100% test coverage maintained

#### Task 3.2: Quality Compliance
- [ ] Run `./quality-check.sh` on entire codebase
- [ ] Fix any architecture compliance violations
- [ ] Fix any immutability violations
- [ ] Fix any type checking errors
- [ ] Ensure all examples pass quality checks

#### Task 3.3: Integration Testing
- [ ] Test chat example with real OpenAI API
- [ ] Test portfolio example with DSPy integration
- [ ] Test RAG example with FAISS vector search
- [ ] Verify all examples handle errors gracefully

### Phase 4: Documentation

#### Task 4.1: Update API Documentation
- [ ] Update message_flow.py docstrings
- [ ] Document the explicit routing pattern
- [ ] Add examples showing loops and convergence
- [ ] Document migration from from_node() pattern

#### Task 4.2: Update Example READMEs
- [ ] Create/update README for chat_message_driven
- [ ] Update README for portfolio_analysis_message_driven
- [ ] Update README for rag_message_driven
- [ ] Include clear flow diagrams

### Phase 5: Migration Support

#### Task 5.1: Migration Guide
- [ ] Document breaking changes
- [ ] Provide before/after examples
- [ ] Show how to convert from_node() patterns
- [ ] Include common patterns (loops, convergence, termination)

#### Task 5.2: Backwards Compatibility Assessment
- [ ] Determine if we need deprecation warnings
- [ ] Consider if we should support both APIs temporarily
- [ ] Document upgrade path for existing code

## Success Criteria

1. **Intuitive API**: Flows read sequentially like a story
2. **All patterns supported**: Loops, convergence, multiple terminations
3. **Type safety maintained**: Full pyright strict compliance
4. **Quality compliance**: Zero violations across codebase
5. **Examples work**: All three examples functional with real APIs

## Risk Mitigation

- **Risk**: Breaking existing code
  - **Mitigation**: Clear migration guide, consider deprecation period

- **Risk**: Type inference complexity
  - **Mitigation**: Extensive testing, may need cast() in complex cases

- **Risk**: Performance impact
  - **Mitigation**: Profile before/after, optimize if needed

## Timeline Estimate

- Phase 1 (Core API): 2-3 hours
- Phase 2 (Examples): 1-2 hours
- Phase 3 (Testing): 1-2 hours
- Phase 4 (Documentation): 1 hour
- Phase 5 (Migration): 1 hour

**Total: 6-9 hours of focused work**

## Next Immediate Steps

1. Start with Phase 1, Task 1.1 - modify core message_flow.py
2. Update chat_message_driven as proof of concept
3. Run quality checks to validate approach
4. Proceed with remaining examples if successful