# ClearFlow Callback Specification

Version: 1.0.0
Status: Draft
Date: 2025-01-13

## Executive Summary

This specification defines the callback interface for ClearFlow, enabling integration with observability platforms, debugging tools, and user interfaces without introducing dependencies or affecting flow execution.

## 1. Analysis

### 1.1 Problem Statement

ClearFlow orchestrates message-driven workflows for GenAI applications. These workflows require:

- Real-time visibility during development and debugging
- Production observability for monitoring and optimization
- Integration with industry-standard tracing platforms
- User-facing progress indicators

### 1.2 Industry Context

Modern orchestration frameworks provide callback mechanisms as standard integration points:

- **LangChain**: Callbacks for every LLM call, tool use, and chain execution
- **LlamaIndex**: Event system for indexing, retrieval, and synthesis
- **DSPy**: Hooks for optimization and execution tracking

Observability platforms expect these callbacks:

- **MLflow**: Requires callbacks for auto-tracing (not monkey-patching)
- **OpenTelemetry**: Instruments via hooks and callbacks
- **Datadog/New Relic**: Consume callback events for APM

### 1.3 Design Principles

1. **Non-invasive**: Callbacks must not affect flow execution or message routing
2. **Zero dependencies**: Core callback interface requires only Python stdlib
3. **Type-safe**: Full typing for all callback methods and parameters
4. **Async-first**: All callbacks are async for non-blocking operation
5. **Fail-safe**: Callback failures must not crash flows

## 2. Design

### 2.1 Architecture

```text
┌─────────────────┐
│   MessageFlow   │
│                 │
│  ┌───────────┐  │
│  │   Node A  │  │──callback──> on_node_start(node_a, message)
│  └───────────┘  │──callback──> on_node_end(node_a, result)
│        ↓        │
│  ┌───────────┐  │
│  │   Node B  │  │──callback──> on_node_start(node_b, message)
│  └───────────┘  │──callback──> on_node_end(node_b, result)
│                 │
└─────────────────┘
```

### 2.2 Callback Lifecycle

1. **Flow Start**: When process() is called on a flow
2. **Node Start**: Before each node's process() method
3. **Node End**: After each node's process() method (success or failure)
4. **Flow End**: When flow reaches termination or error

### 2.3 Integration Points

Callbacks are injected during flow building, before termination:

```python
flow = message_flow("name", starting_node)
    .with_callbacks(handler)  # Optional callback attachment
    .route(...)
    .end(...)  # Returns MessageFlow, must be last
```

## 3. Requirements

### 3.1 Core Interface Requirements

**REQ-001**: The callback system SHALL define an abstract `CallbackHandler` base class with lifecycle methods.

**REQ-002**: The `CallbackHandler` SHALL include the following async methods:

- `on_flow_start(flow_name: str, message: Message) -> None`
- `on_flow_end(flow_name: str, message: Message, error: Exception | None) -> None`
- `on_node_start(node_name: str, message: Message) -> None`
- `on_node_end(node_name: str, message: Message, error: Exception | None) -> None`

**REQ-003**: All callback methods SHALL be optional (default no-op implementation).

**REQ-004**: The callback interface SHALL use only Python standard library types.

### 3.2 Execution Requirements

**REQ-005**: Callback execution SHALL be wrapped in try-except to prevent callback errors from affecting flow execution.

**REQ-006**: Callback errors SHALL be logged to stderr but not propagated.

**REQ-007**: Callbacks SHALL execute synchronously in the order: flow_start → node_start → node_end → ... → flow_end.

**REQ-008**: Multiple callback handlers SHALL be supported via a `CompositeHandler` that executes handlers in registration order.

### 3.3 Integration Requirements

**REQ-009**: MessageFlow SHALL accept an optional `callbacks` parameter of type `CallbackHandler | None`.

**REQ-010**: MessageFlow SHALL invoke callbacks at the specified lifecycle points if a handler is provided.

**REQ-011**: Nested flows SHALL propagate callbacks to inner flows automatically.

**REQ-012**: The callback system SHALL NOT require modification of existing Node implementations.

### 3.4 Type Safety Requirements

**REQ-013**: All callback methods SHALL be fully typed with no `Any` types.

**REQ-014**: Message parameters SHALL preserve their concrete types (not erased to base `Message`).

**REQ-015**: The callback system SHALL pass pyright strict mode type checking.

### 3.5 Performance Requirements

**REQ-016**: Callback overhead SHALL be zero when no handler is attached.

**REQ-017**: Callback execution SHALL not block node execution (async operations).

**REQ-018**: The callback system SHALL NOT retain references to messages after callback completion.

## 4. Test Requirements

Each requirement above must have at least one corresponding test:

- `test_callback_handler_interface` - REQ-001, REQ-002, REQ-003
- `test_callback_stdlib_only` - REQ-004
- `test_callback_error_handling` - REQ-005, REQ-006
- `test_callback_execution_order` - REQ-007
- `test_composite_handler` - REQ-008
- `test_flow_callback_integration` - REQ-009, REQ-010
- `test_nested_flow_callbacks` - REQ-011
- `test_no_node_modification` - REQ-012
- `test_callback_type_safety` - REQ-013, REQ-014, REQ-015
- `test_callback_zero_overhead` - REQ-016
- `test_callback_async_execution` - REQ-017
- `test_callback_no_retention` - REQ-018

## 5. Implementation Notes

### 5.1 Error Handling Pattern

```python
async def _safe_callback(self, method: str, *args) -> None:
    """Execute callback safely without affecting flow."""
    if not self.callbacks:
        return  # REQ-016: Zero overhead

    try:
        callback = getattr(self.callbacks, method)
        await callback(*args)
    except Exception as e:
        # REQ-006: Log but don't propagate
        print(f"Callback {method} failed: {e}", file=sys.stderr)
```

### 5.2 Integration Example

```python
# Console output for examples
class ConsoleHandler(CallbackHandler):
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        if error:
            print(f"❌ {node_name}: {error}")
        elif isinstance(message, MarketAnalyzedEvent):
            print(f"📊 {node_name}: Found {len(message.opportunities)} opportunities")

# MLflow tracing (in clearflow-mlflow package)
class MLflowHandler(CallbackHandler):
    async def on_node_start(self, node_name: str, message: Message) -> None:
        self.spans[node_name] = mlflow.start_span(node_name)

    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        mlflow.end_span(self.spans[node_name], message, error)
```

## 6. Migration Path

1. **Phase 1**: Implement callbacks.py with CallbackHandler
2. **Phase 2**: Update MessageFlow to invoke callbacks
3. **Phase 3**: Migrate examples from Observer to CallbackHandler
4. **Phase 4**: Remove observer.py and related tests
5. **Phase 5**: Create clearflow-mlflow package using callbacks

## 7. Future Considerations

- **Filtering**: Add message type filters to reduce callback invocations
- **Context**: Pass flow context (depth, parent) for nested flows
- **Metrics**: Built-in timing and counter callbacks
- **Sampling**: Statistical sampling for high-volume flows

## Appendix A: Comparison with Observer Pattern

| Aspect | Observer (Current) | Callbacks (Proposed) |
|--------|-------------------|---------------------|
| Purpose | "Observation" (misleading) | Integration hooks |
| Control Flow | Can halt flows | Never affects flow |
| Exceptions | Propagate (fail-fast) | Logged only |
| Interface | Complex type matching | Simple lifecycle |
| Integration | Custom | Industry standard |
| Use Cases | Security (?), Logging | Tracing, UI, Debugging |

## Appendix B: References

- [MLflow Tracing Integration Guide](https://mlflow.org/docs/latest/genai/tracing/integrations/contribute/)
- [LangChain Callbacks](https://python.langchain.com/docs/how_to/#callbacks)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
