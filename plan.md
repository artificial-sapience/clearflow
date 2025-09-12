# ClearFlow Message-Driven Architecture Implementation Plan

## Current Sprint: Message-Driven Architecture

### 🔧 In Progress: Flow Builder Routing Fix

**Issue**: The `_MessageFlowBuilder` has a logic problem tracking which node produces which message type.

**Problem Details**:
- When calling `.route(MessageType, destination_node)`, the builder needs to know which node produces MessageType
- Current logic incorrectly searches existing routes to find the producer
- The builder assumes untracked messages come from the start node, which is incorrect for chained routes

**Test Failure**: `test_message_flow.py::TestMessageFlow::test_flow_with_routing`
- Error: "No route defined for message type 'ValidateCommand' from node 'transform'"
- The transform node outputs ValidateCommand, but the flow doesn't have the route registered correctly

**Root Cause Analysis**:
```python
# In _MessageFlowBuilder.route() around line 135:
for msg_type, node_name in self._routes:
    if msg_type == message_type:
        producing_node_name = node_name
        break
```
This searches existing routes to find who produces the message, but routes are keyed by (message_type, producer), so this logic is circular.

**Potential Solutions**:
1. Track the destination nodes from previous routes as potential producers
2. Require explicit "from_node" parameter in route() method
3. Infer from the order of route() calls (each destination becomes next producer)

### 📋 Remaining Tasks

1. **Fix Flow Builder Logic** (Priority: HIGH)
   - Fix the producing node tracking in `_MessageFlowBuilder.route()`
   - Ensure routes are correctly registered with proper (message_type, producer_node) keys
   - Make all flow routing tests pass

2. **Achieve 100% Test Coverage** (Priority: HIGH)
   - Current test files created:
     - test_message.py (16 tests passing)
     - test_message_node.py (9 tests passing) 
     - test_message_flow.py (1 failing due to routing issue)
     - test_observer.py (not yet run due to early failure)
   - Fix routing issue first, then ensure all tests pass
   - Add any missing test cases for edge conditions

3. **Integration Testing** (Priority: MEDIUM)
   - Test message flows with observer pattern
   - Test nested observable flows
   - Verify fail-fast behavior in complex scenarios

## Design Decisions Log

### Key Architectural Choices
1. **Flows as Nodes**: `_MessageFlow` extends `Node` for composability
2. **Observable Flows Only**: `ObservableFlow` decorates only `_MessageFlow`, not generic `Node`
3. **Fail-Fast Observers**: Exceptions propagate immediately, no error isolation
4. **Package-Internal Privacy**: `_MessageFlow` is private to external users but accessible within clearflow package

### API Design
- Public: `message_flow()` function returns builder
- Private: `_MessageFlow` and `_MessageFlowBuilder` classes
- Decorator: `ObservableFlow` wraps flows with observation