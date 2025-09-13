# Message Flow API Redesign Plan

## Executive Summary

Redesign the message_flow API to use explicit source nodes in routing (like the original flow API) instead of the `from_node()` grouping approach. This change improves UX by enabling sequential thinking about workflows.

**Status**: Phase 1 Complete ✅

## Current Implementation

The message_flow API now matches the original flow API pattern:

```python
# Message flow API (implemented)
message_flow("Name", start_node)
.route(from_node, outcome_type, to_node)
.end(from_node, outcome_type)
```

Key implementation details:
- Uses type erasure at routing boundaries for flexibility with union types
- Builder maintains stable types: `_MessageFlowBuilder[TStartMessage, TStartOut]`
- Runtime validation ensures correctness
- Type safety preserved at flow boundaries (input/output)

## Remaining Phases

### Phase 2: Documentation Updates ⏳

#### Task 2.1: Update API Documentation
- [ ] Update message_flow.py docstrings to reflect new signatures
- [ ] Document the explicit routing pattern with examples
- [ ] Explain type erasure approach and why it's needed
- [ ] Add examples showing loops, convergence, and error handling

#### Task 2.2: Create Migration Guide
- [ ] Document breaking changes from `from_node()` pattern
- [ ] Provide before/after examples for common patterns
- [ ] Explain how to handle union types
- [ ] Include troubleshooting section for type errors

### Phase 3: Final Validation 🔍

#### Task 3.1: Integration Testing
- [ ] Test chat example with real OpenAI API
- [ ] Test portfolio example with DSPy integration
- [ ] Test RAG example with FAISS vector search
- [ ] Verify error handling in all examples

#### Task 3.2: Performance Validation
- [ ] Profile before/after for any performance impact
- [ ] Ensure no memory leaks in routing
- [ ] Validate async performance characteristics

## Success Metrics

✅ **Achieved:**
- Intuitive API matching original flow pattern
- All patterns supported (loops, convergence, termination)
- Type safety with pragmatic flexibility
- 100% test coverage maintained
- Zero quality violations

⏳ **Pending:**
- Complete documentation updates
- Real-world integration testing
- Performance validation

## Next Priority

Complete Phase 2, Task 2.1: Update API documentation in message_flow.py to reflect the new routing pattern and explain the design decisions.