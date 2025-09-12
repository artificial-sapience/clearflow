# Message-Driven ClearFlow: Architecture Refactoring Proposal

## Executive Summary

This proposal outlines a refactoring of ClearFlow to make it explicitly message-driven, where workflow outcomes are strongly typed messages rather than strings. This evolution enhances type safety while maintaining ClearFlow's core philosophy of explicit routing and minimal complexity.

## Current Architecture Analysis

### Current State

- **Outcomes as strings**: Nodes return `NodeResult[T]` with `outcome: str`
- **String-based routing**: Flow routes match on `(node_name, outcome_string)` tuples
- **Type transformation**: Supports `Node[TIn, TOut]` for state transformations
- **Runtime validation**: Route mismatches only caught at runtime

### Strengths

- Simple and explicit
- Already supports type transformations
- Minimal API surface
- Zero dependencies

### Limitations

- String outcomes lack type safety
- No compile-time validation of route compatibility
- Nodes can return any string outcome
- No explicit contract for what messages a node produces

## Proposed Message-Driven Architecture

### Core Concept: Messages as First-Class Citizens

Instead of:

```python
NodeResult(state=new_state, outcome="processed")
```

We have:

```python
TMessageOut
```

### Key Design Principles

1. **AI Agency**: Nodes can embody AI intelligence that decides what to do next
2. **Flexible Output**: Nodes can produce Commands (intent/delegation) or Events (facts)
3. **Type Safety**: Message routing validated at compile time
4. **Explicit Contracts**: Node signatures declare exact message types
5. **Data Locality**: Messages carry their own data, no separate state
6. **Exhaustiveness**: Type system ensures all messages are handled

## Detailed Design

### 1. Message System Foundation

```python
from abc import ABC
from dataclasses import dataclass

def _utc_now() -> datetime:
    """Create a timezone-aware datetime in UTC.

    Returns:
        Current UTC time as datetime.

    """
    return datetime.now(UTC)

@dataclass(frozen=True, kw_only=True)
class Message(ABC):
    
    @property
    def message_type(self) -> type["Message"]:
        """Return the concrete message type for routing."""
        return type(self)

    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Auto-generated unique ID
    triggered_by_id: uuid.UUID | None  # Must be explicitly set - None for initial commands, UUID for all others
    timestamp: datetime = field(default_factory=_utc_now)  # Auto-generated timestamp
    flow_id: uuid.UUID  # Must be explicitly set - identifies the flow session

@dataclass(frozen=True, kw_only=True)
class Event(ABC, Message):
    """Base Event extending Message for causality tracking. Captures facts.

    All events are immutable frozen dataclasses with flow tracking
    and message causality. Events MUST have a triggered_by value (unlike commands).

        Inherits from Message:
        message_id: Unique identifier for this message
        triggered_by: UUID of the message that triggered this event (required for events)
        timestamp: Timezone-aware datetime for unambiguous event ordering
        flow_id: UUID identifying the flow session

    """

    # Override triggered_by_id to make it required for events (no default, no None allowed)
    triggered_by_id: uuid.UUID  # Required for events - must be set at creation time

@dataclass(frozen=True, kw_only=True)
class Command(ABC, Message):
    """Base Command extending Message for causality tracking. Captures intent.

    All commands are immutable frozen dataclasses with flow tracking
    and message causality.

    """
```

### 2. Updated Node Contract

```python
@dataclass(frozen=True)
class Node[TMessageIn: Message, TMessageOut: Message](ABC):
    """Orchestration node that can embody AI intelligence.
    
    Accepts: Commands or Events (triggers for processing)
    Produces: Commands (intent/delegation) or Events (completed facts)
    
    This flexibility allows AI agents to:
    - Orchestrate complex workflows via Commands
    - Record completion via Events  
    - Delegate to specialized agents/tools
    - Dynamically adapt their strategy
    """
    name: str
    
    @abstractmethod
    async def process(self, message: TMessageIn) -> TMessageOut:
        """Process message, potentially using AI intelligence to decide next action."""
        ...
```

### 3. Type-Safe Flow Builder

```python
class MessageFlowBuilder[TStartMessage: Message, TCurrentMessage: Message]:
    """Builder for type-safe message routing."""

    def route[TNextMessage: Message](
        self,
        from_message: type[TCurrentMessage],
        to_node: Node[TCurrentMessage, TNextMessage]
    ) -> MessageFlowBuilder[TStartMessage, TNextMessage]:
        """Route from current message type to next node."""
        # Type system ensures to_node accepts TCurrentMessage
        ...
    
    def end(self, terminal_message: type[TCurrentMessage]) -> MessageFlow[TStartMessage, TCurrentMessage]:
        """Mark terminal message type."""
        ...
```

## Implementation Examples

### Example 1: AI Orchestration with Commands and Events

```python
# AI agent that analyzes data and orchestrates work
@dataclass(frozen=True)
class AIAnalystNode(Node[DataRequestEvent, Message]):
    """AI that analyzes data and decides what to do next."""
    name: str = "ai_analyst"
    
    async def process(self, event: DataRequestEvent) -> Message:
        analysis = await self.llm.analyze(event.data)
        
        if analysis.needs_more_context:
            # AI decides it needs more info - issues a command
            return GatherContextCommand(
                sources=analysis.suggested_sources,
                triggered_by_id=event.id,
                flow_id=event.flow_id
            )
        elif analysis.requires_specialist:
            # AI decides to delegate - issues a command
            return InvokeSpecialistCommand(
                specialist_type=analysis.specialist_type,
                task=analysis.task_description,
                triggered_by_id=event.id,
                flow_id=event.flow_id
            )
        else:
            # AI completes analysis - emits an event
            return AnalysisCompletedEvent(
                findings=analysis.findings,
                triggered_by_id=event.id,
                flow_id=event.flow_id
            )

# Strategic planner that creates execution plans
@dataclass(frozen=True) 
class StrategicPlannerNode(Node[GoalDefinedEvent, ExecuteStepCommand]):
    """AI that creates and orchestrates execution plans."""
    name: str = "strategic_planner"
    
    async def process(self, event: GoalDefinedEvent) -> ExecuteStepCommand:
        # AI creates a plan with multiple steps
        plan = await self.llm.create_plan(event.goal)
        
        # Issues command to execute first step
        return ExecuteStepCommand(
            step=plan.first_step,
            remaining_steps=plan.remaining_steps,
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )
```

### Example 2: RAG Pipeline with Messages

Based on the current RAG example in `examples/rag/`, here's how it would look with the message-driven architecture:

```python
# Define domain messages for RAG pipeline
@dataclass(frozen=True, kw_only=True)
class DocumentsLoadedEvent(Event):
    """Documents loaded and ready for processing."""
    documents: tuple[str, ...]
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class DocumentsChunkedEvent(Event):
    """Documents split into chunks."""
    documents: tuple[str, ...]
    chunks: tuple[str, ...]
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class ChunksEmbeddedEvent(Event):
    """Chunks converted to embeddings."""
    chunks: tuple[str, ...]
    embeddings: npt.NDArray[np.float32]
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class IndexCreatedEvent(Event):
    """Search index created from embeddings."""
    index: faiss.Index
    chunks: tuple[str, ...]
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class QueryCommand(Command):
    """User query to process."""
    query: str
    index: faiss.Index
    chunks: tuple[str, ...]
    triggered_by_id: uuid.UUID | None = None  # Initial command
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class QueryEmbeddedEvent(Event):
    """Query converted to embedding."""
    query: str
    query_embedding: npt.NDArray[np.float32]
    index: faiss.Index
    chunks: tuple[str, ...]
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class DocumentRetrievedEvent(Event):
    """Relevant document chunk retrieved."""
    query: str
    retrieved_text: str
    retrieval_score: float
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

@dataclass(frozen=True, kw_only=True)
class AnswerGeneratedEvent(Event):
    """Answer generated from context."""
    query: str
    answer: str
    source_text: str
    triggered_by_id: uuid.UUID
    flow_id: uuid.UUID

# Define nodes with explicit message contracts
@dataclass(frozen=True)
class ChunkDocumentsNode(Node[DocumentsLoadedEvent, DocumentsChunkedEvent]):
    """Splits documents into smaller chunks for processing."""
    name: str = "chunk_documents"
    
    async def process(self, event: DocumentsLoadedEvent) -> DocumentsChunkedEvent:
        all_chunks = tuple(
            chunk 
            for doc in event.documents 
            for chunk in fixed_size_chunk(doc)
        )
        
        return DocumentsChunkedEvent(
            documents=event.documents,
            chunks=all_chunks,
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )

@dataclass(frozen=True)
class EmbedDocumentsNode(Node[DocumentsChunkedEvent, ChunksEmbeddedEvent]):
    """Creates embeddings for all document chunks."""
    name: str = "embed_documents"
    
    async def process(self, event: DocumentsChunkedEvent) -> ChunksEmbeddedEvent:
        embeddings = np.array(
            [get_embedding(chunk) for chunk in event.chunks],
            dtype=np.float32
        )
        
        return ChunksEmbeddedEvent(
            chunks=event.chunks,
            embeddings=embeddings,
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )

@dataclass(frozen=True)
class CreateIndexNode(Node[ChunksEmbeddedEvent, IndexCreatedEvent]):
    """Creates a FAISS index from document embeddings."""
    name: str = "create_index"
    
    async def process(self, event: ChunksEmbeddedEvent) -> IndexCreatedEvent:
        dimension = event.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(event.embeddings)
        
        return IndexCreatedEvent(
            index=index,
            chunks=event.chunks,
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )

@dataclass(frozen=True)
class EmbedQueryNode(Node[QueryCommand, QueryEmbeddedEvent]):
    """Converts query to embedding for search."""
    name: str = "embed_query"
    
    async def process(self, command: QueryCommand) -> QueryEmbeddedEvent:
        query_embedding = get_embedding(command.query)
        
        return QueryEmbeddedEvent(
            query=command.query,
            query_embedding=query_embedding,
            index=command.index,
            chunks=command.chunks,
            triggered_by_id=command.id,
            flow_id=command.flow_id
        )

@dataclass(frozen=True)
class RetrieveDocumentNode(Node[QueryEmbeddedEvent, DocumentRetrievedEvent]):
    """Retrieves most relevant document chunk."""
    name: str = "retrieve"
    
    async def process(self, event: QueryEmbeddedEvent) -> DocumentRetrievedEvent:
        distances, indices = event.index.search(
            event.query_embedding.reshape(1, -1), 
            k=1
        )
        
        retrieved_text = event.chunks[indices[0][0]]
        
        return DocumentRetrievedEvent(
            query=event.query,
            retrieved_text=retrieved_text,
            retrieval_score=float(distances[0][0]),
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )

@dataclass(frozen=True)
class GenerateAnswerNode(Node[DocumentRetrievedEvent, AnswerGeneratedEvent]):
    """Generates answer using retrieved context."""
    name: str = "generate_answer"
    
    async def process(self, event: DocumentRetrievedEvent) -> AnswerGeneratedEvent:
        prompt = f"Context: {event.retrieved_text}\n\nQuestion: {event.query}\n\nAnswer:"
        answer = await call_llm(prompt)
        
        return AnswerGeneratedEvent(
            query=event.query,
            answer=answer,
            source_text=event.retrieved_text,
            triggered_by_id=event.id,
            flow_id=event.flow_id
        )

# Build type-safe flows

# Offline indexing flow
indexing_flow = (
    message_flow("IndexDocuments", ChunkDocumentsNode())
    .route(DocumentsChunkedEvent, EmbedDocumentsNode())
    .route(ChunksEmbeddedEvent, CreateIndexNode())
    .end(IndexCreatedEvent)
)

# Online query flow
query_flow = (
    message_flow("AnswerQuery", EmbedQueryNode())
    .route(QueryEmbeddedEvent, RetrieveDocumentNode())
    .route(DocumentRetrievedEvent, GenerateAnswerNode())
    .end(AnswerGeneratedEvent)
)
```

### Example 3: Error Handling with Message Unions

```python
@dataclass(frozen=True)
class ValidationErrorEvent(Message[ValidationError]):
    """Validation failed."""
    pass

@dataclass(frozen=True)
class ProcessingNode(Node[InputEvent, SuccessEvent | ValidationErrorEvent]):
    """Node that can succeed or fail with validation error."""
    
    async def process(self, message: InputEvent) -> EventResult[SuccessEvent | ValidationErrorEvent]:
        try:
            result = self.validate_and_process(message.data)
            return EventResult(SuccessEvent(data=result))
        except ValidationError as e:
            return EventResult(ValidationErrorEvent(data=e))

# Flow handles both success and error paths
flow = (
    message_flow("Pipeline", ProcessingNode())
    .route(SuccessEvent, NextNode())
    .route(ValidationErrorEvent, ErrorHandler())
    .end(FinalEvent)
)
```

## Layered Architecture for Observation

### The Challenge: Cross-Cutting Concerns

While explicit routing provides clarity for business logic, real systems need cross-cutting concerns:

- Logging and auditing
- Metrics collection
- Event sourcing
- Notifications
- Fraud detection

The solution: A **layered architecture** that preserves explicit routing while enabling flexible observation.

### Layer 1: Core Message Flow

The foundational layer with explicit routing and type-safe transformations:

```python
# Pure business logic flow
core_flow = (
    message_flow("OrderProcessing", ValidateOrderNode())
    .route(OrderValidatedEvent, ProcessPaymentNode())
    .route(PaymentProcessedEvent, ShipOrderNode())
    .end(OrderShippedEvent)
)
```

### Layer 2: Observable Flow

Wraps the core flow to add observation capabilities without modifying business logic:

```python
@dataclass(frozen=True)
class Observer[TMessage: Message](ABC):
    """Observer that processes messages without affecting flow.
    
    Observers:
    - Cannot modify messages
    - Cannot affect routing
    - Execute asynchronously
    - Errors don't break main flow
    """
    name: str
    
    @abstractmethod
    async def observe(self, message: TMessage) -> None:
        """Process message for side effects only."""
        ...

@dataclass(frozen=True)
class ObservableFlow[TStart: Message, TEnd: Message]:
    """Wraps a core flow to add observation capabilities."""
    
    core_flow: MessageFlow[TStart, TEnd]
    observers: dict[type[Message], tuple[Observer, ...]] = field(default_factory=dict)
    
    def observe[TMsg: Message](
        self,
        message_type: type[TMsg],
        observer: Observer[TMsg]
    ) -> "ObservableFlow[TStart, TEnd]":
        """Add an observer for a specific message type."""
        current = self.observers.get(message_type, ())
        new_observers = {
            **self.observers,
            message_type: (*current, observer)
        }
        return replace(self, observers=new_observers)
    
    async def execute(self, start_message: TStart) -> TEnd:
        """Execute flow with automatic observation."""
        # Wrap node execution to intercept messages
        return await self._execute_with_interception(start_message)
```

### Message Interception Mechanism

The key innovation: **ObservableFlow wraps node execution** to intercept messages:

```python
class ObservableFlow[TStart: Message, TEnd: Message]:
    """Implementation details of message interception."""
    
    async def _execute_with_interception(self, start_message: TStart) -> TEnd:
        """Execute core flow while intercepting all messages."""
        current_message = start_message
        current_node = self.core_flow.start_node
        
        while current_node is not None:
            # Execute node
            output_message = await current_node.process(current_message)
            
            # INTERCEPT: Notify observers asynchronously
            await self._notify_observers(output_message)
            
            # Continue routing
            current_node = self.core_flow.get_next_node(output_message)
            current_message = output_message
        
        return current_message
    
    async def _notify_observers(self, message: Message) -> None:
        """Notify all observers registered for this message type."""
        # Get observers for exact type and base types
        observers = self._get_observers_for(type(message))
        
        if observers:
            # Run observers in parallel, don't wait, don't fail main flow
            tasks = [self._safe_observe(obs, message) for obs in observers]
            asyncio.create_task(asyncio.gather(*tasks))
    
    async def _safe_observe(self, observer: Observer, message: Message) -> None:
        """Execute observer with error isolation."""
        try:
            await observer.observe(message)
        except Exception as e:
            # Log but don't propagate
            logger.error(f"Observer {observer.name} failed: {e}")
    
    def _get_observers_for(self, message_type: type[Message]) -> tuple[Observer, ...]:
        """Get all observers that can handle this message type."""
        observers = []
        
        # Check exact type
        observers.extend(self.observers.get(message_type, ()))
        
        # Check base types (e.g., Observer[Event] handles all Events)
        for obs_type, obs_list in self.observers.items():
            if obs_type != message_type and issubclass(message_type, obs_type):
                observers.extend(obs_list)
        
        return tuple(observers)
```

### Practical Observer Examples

```python
# Event logger for audit trail
@dataclass(frozen=True)
class EventLogger(Observer[Event]):
    """Logs all events to structured log."""
    name: str = "event_logger"
    log_level: str = "INFO"
    
    async def observe(self, event: Event) -> None:
        await async_logger.log(self.log_level, {
            "event_type": event.__class__.__name__,
            "event_id": str(event.id),
            "triggered_by": str(event.triggered_by_id),
            "flow_id": str(event.flow_id),
            "timestamp": event.timestamp.isoformat(),
            "data": self._serialize_event(event)
        })

# Metrics collector
@dataclass(frozen=True)
class MetricsCollector(Observer[Message]):
    """Collects metrics for all messages."""
    name: str = "metrics"
    
    async def observe(self, message: Message) -> None:
        metrics.increment(f"message.{message.__class__.__name__}.count")
        metrics.histogram(f"message.size", len(str(message)))

# Fraud detector for payments
@dataclass(frozen=True)
class FraudDetector(Observer[PaymentProcessedEvent]):
    """Analyzes payments for fraud patterns."""
    name: str = "fraud_detector"
    ml_model: FraudModel
    
    async def observe(self, event: PaymentProcessedEvent) -> None:
        risk_score = await self.ml_model.analyze(event)
        if risk_score > 0.8:
            # Don't block payment, but flag for review
            await fraud_queue.send(FraudAlert(
                payment_id=event.payment_id,
                risk_score=risk_score,
                triggered_at=event.timestamp
            ))

# Customer notifier
@dataclass(frozen=True)
class CustomerNotifier(Observer[OrderShippedEvent]):
    """Sends shipping notifications to customers."""
    name: str = "customer_notifier"
    
    async def observe(self, event: OrderShippedEvent) -> None:
        await email_service.send_async(
            to=event.customer_email,
            template="order_shipped",
            data={"tracking_number": event.tracking_number}
        )

# Event store for event sourcing
@dataclass(frozen=True)
class EventStoreObserver(Observer[Event]):
    """Persists all events for event sourcing."""
    name: str = "event_store"
    store: EventStore
    
    async def observe(self, event: Event) -> None:
        await self.store.append(
            stream_id=str(event.flow_id),
            event_type=event.__class__.__name__,
            event_data=event,
            event_id=event.id,
            timestamp=event.timestamp
        )
```

### Complete Usage Example

```python
# 1. Define core business flow
core_flow = (
    message_flow("OrderProcessing", ValidateOrderNode())
    .route(OrderValidatedEvent, CheckInventoryNode())
    .route(InventoryConfirmedEvent, ProcessPaymentNode())
    .route(PaymentProcessedEvent, ShipOrderNode())
    .route(PaymentFailedEvent, CancelOrderNode())
    .end(OrderCompletedEvent)
)

# 2. Add cross-cutting concerns via observers
observable_flow = (
    ObservableFlow(core_flow)
    # Logging
    .observe(Event, EventLogger(log_level="INFO"))
    # Metrics
    .observe(Message, MetricsCollector())
    # Event sourcing
    .observe(Event, EventStoreObserver(store=postgres_event_store))
    # Business observers
    .observe(PaymentProcessedEvent, FraudDetector(ml_model=fraud_model))
    .observe(OrderShippedEvent, CustomerNotifier())
    .observe(OrderCompletedEvent, InventoryUpdater())
    # Error tracking
    .observe(PaymentFailedEvent, ErrorTracker())
)

# 3. Execute with all observers active
result = await observable_flow.execute(
    CreateOrderCommand(
        order_id=uuid.uuid4(),
        customer_id=customer_id,
        items=items,
        flow_id=uuid.uuid4()
    )
)
```

### Benefits of Layered Architecture

1. **Separation of Concerns**
   - Core flow contains only business logic
   - Observers handle cross-cutting concerns
   - Easy to test each layer independently

2. **Non-Invasive Observation**
   - Add observers without modifying nodes
   - No changes to business logic required
   - Observers can be added/removed dynamically

3. **Type Safety Preserved**
   - Observers are typed to specific messages
   - Compile-time checking of observer compatibility
   - IDE autocomplete for message fields

4. **Performance Optimization**
   - Observers run asynchronously
   - Don't block main flow execution
   - Can be parallelized automatically

5. **Error Isolation**
   - Observer failures don't affect business flow
   - Each observer fails independently
   - Main flow continues even if all observers fail

6. **Composability**

   ```python
   # Combine multiple observable flows
   monitoring = ObservableFlow(core_flow)
       .observe(Event, EventLogger())
       .observe(Message, MetricsCollector())
   
   production = monitoring
       .observe(Event, EventStoreObserver(store))
       .observe(PaymentProcessedEvent, FraudDetector(model))
   
   debug = production
       .observe(Message, DebugLogger(verbose=True))
   ```

### Observer vs Handler Distinction

- **Handlers** (Nodes): Transform messages, affect flow routing, must succeed
- **Observers**: Side effects only, cannot affect flow, may fail silently

This distinction maintains ClearFlow's explicit routing while enabling flexible observation patterns.

## Migration Strategy

### Phase 1: Parallel Implementation

- Implement message system alongside existing string-based system
- Both APIs coexist with clear namespacing
- No breaking changes

### Phase 2: Compatibility Layer

```python
# Adapter to use string-based nodes in message flows
class StringOutcomeAdapter(Node[TMessageIn, StringOutcomeEvent]):
    def __init__(self, legacy_node: Node, outcome_mapping: dict[str, type[Message]]):
        self.legacy_node = legacy_node
        self.outcome_mapping = outcome_mapping
    
    async def process(self, message: TMessageIn) -> EventResult[Message]:
        result = await self.legacy_node(message.data)
        message_type = self.outcome_mapping[result.outcome]
        return EventResult(message_type(data=result.state))
```

### Phase 3: Migration Tools

- Automated script to convert string outcomes to messages
- Static analysis to suggest message types
- Gradual migration path

### Phase 4: Deprecation

- Mark string-based API as deprecated
- Provide timeline for removal
- Maintain backwards compatibility for major version

## Benefits Analysis

### Type Safety Improvements

1. **Compile-time route validation**: Invalid routes caught by pyright
2. **Exhaustive matching**: Type checker ensures all messages handled
3. **Clear contracts**: Node signatures show exact inputs/outputs
4. **No magic strings**: Messages are concrete types

### Developer Experience

1. **IDE support**: Autocomplete for message types and fields
2. **Refactoring safety**: Rename messages with confidence
3. **Documentation**: Message types serve as documentation
4. **Debugging**: Clear message flow in stack traces

### Architecture Benefits

1. **Single Responsibility**: Nodes handle one concern
2. **Decoupling**: Messages decouple nodes from each other
3. **Testability**: Easy to test with mock messages
4. **Extensibility**: Add new messages without breaking existing code

## Potential Challenges

### 1. Increased Verbosity

**Challenge**: More code to define messages
**Mitigation**:

- Message definition is one-time cost
- Provides documentation value
- Consider message factory helpers

### 2. Learning Curve

**Challenge**: New concepts for users
**Mitigation**:

- Comprehensive examples
- Migration guide
- Keep simple use cases simple

### 3. Type Complexity

**Challenge**: Union types can get complex
**Mitigation**:

- Type aliases for common unions
- Clear naming conventions
- Limit union size through design

## Performance Considerations

### Memory

- Messages are frozen dataclasses (same as current state)
- No additional memory overhead
- Messages can be optimized with `__slots__`

### Runtime

- Type checking happens at development time
- No runtime type validation needed
- Message dispatch can be optimized

## Alternative Approaches Considered

### 1. Enum-Based Outcomes

```python
class Outcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
```

**Rejected because**: Still strings at runtime, limited data carrying

### 2. Generic Message Container

```python
Message[TData, TOutcome]
```

**Rejected because**: Loses type safety on outcome types

### 3. Inheritance-Based Messages

```python
class SuccessEvent(Message): pass
class FailureEvent(Message): pass
```

**Rejected because**: Too rigid, doesn't compose well

## Implementation Timeline

### Week 1-2: Foundation

- Implement Message base class
- Create EventResult type
- Build message matching utilities

### Week 3-4: Core Integration

- Update Node class for messages
- Implement EventFlowBuilder
- Create type-safe routing

### Week 5-6: Migration Support

- Build compatibility layer
- Create migration tools
- Write migration guide

### Week 7-8: Testing & Documentation

- Comprehensive test suite
- Update all examples
- Complete documentation

## Decision Points

### 1. Message Data Structure

**Option A**: Messages contain data field

```python
@dataclass(frozen=True)
class QueryEvent(Message[str]):
    data: str
```

**Option B**: Messages are data

```python
@dataclass(frozen=True)
class QueryEvent(Message):
    query: str
    max_results: int
```

**Recommendation**: Option B - more natural, less nesting

### 2. Error Handling

**Option A**: Special error message types
**Option B**: Union types for errors
**Option C**: Separate error channel

**Recommendation**: Option B - explicit in type system

### 3. Backwards Compatibility

**Option A**: Maintain forever
**Option B**: Deprecate after major version
**Option C**: Clean break

**Recommendation**: Option B - balanced approach

## Conclusion

This message-driven refactoring transforms ClearFlow into a true AI orchestration framework where:

1. **AI agents have agency**: They can issue Commands to orchestrate work
2. **Type safety is paramount**: All message routing is compile-time verified
3. **Flexibility meets structure**: Nodes can produce Commands or Events as needed
4. **Explicit remains core**: All routing decisions are visible and intentional

The ability for nodes to produce both Commands (expressing intent and delegation) and Events (recording facts) makes ClearFlow ideal for AI orchestration, where intelligent agents need to dynamically decide what to do next based on their analysis and reasoning.

The migration path ensures existing users can adopt gradually, and the benefits in type safety and AI orchestration capabilities justify the implementation effort.

## Next Steps

1. Review and discuss this proposal
2. Create proof-of-concept implementation
3. Gather feedback from users
4. Refine based on feedback
5. Begin phased implementation

## Appendix: Comparison with Current API

### Current API

```python
# Define node
class MyNode(Node[StateIn, StateOut]):
    async def exec(self, state: StateIn) -> NodeResult[StateOut]:
        return NodeResult(state=new_state, outcome="success")

# Build flow
flow = (
    flow("Pipeline", node1)
    .route(node1, "success", node2)
    .route(node1, "failure", error_handler)
    .end(node2, "done")
)
```

### Proposed Message API

```python
# Define node with AI orchestration
class MyNode(Node[InputEvent, SuccessEvent | FailureEvent | DelegateCommand]):
    async def process(self, message: InputEvent) -> SuccessEvent | FailureEvent | DelegateCommand:
        # AI can decide to:
        # - Complete with success (Event)
        # - Fail with error (Event)
        # - Delegate work (Command)
        if needs_specialist:
            return DelegateCommand(specialist="expert", task=message.data)
        elif success:
            return SuccessEvent(data=result)
        else:
            return FailureEvent(reason=error)

# Build flow
flow = (
    message_flow("Pipeline", node1)
    .route(SuccessEvent, node2)
    .route(FailureEvent, error_handler)
    .route(DelegateCommand, specialist_node)
    .end(CompleteEvent)
)
```

The evolution is natural and maintains ClearFlow's explicit, minimal philosophy while adding powerful type safety.
