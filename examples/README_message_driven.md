# Message-Driven Examples

These examples demonstrate ClearFlow's message-driven architecture with observable flows.

## Architecture Overview

The message-driven architecture uses:

- **Messages**: `Command` and `Event` types for explicit communication
- **MessageNode**: Processes messages and returns new messages  
- **message_flow**: Creates workflows with message-based routing
- **Observer**: Pattern for side effects without affecting routing

## Examples

### Chat (Message-Driven)

**Location**: `chat_message_driven/`

A conversational AI application using message-driven patterns:

- **UserInputCommand** → **UserInputNode** → **UserResponseEvent**/**QuitRequestEvent** 
- **UserResponseEvent** → **UserResponseToGenerateNode** → **GenerateResponseCommand**
- **GenerateResponseCommand** → **ResponseGeneratorNode** → **ResponseGeneratedEvent**
- **ResponseGeneratedEvent** → **ResponseToDisplayNode** → **DisplayResponseCommand**
- **DisplayResponseCommand** → **DisplayResponseNode** → **UserInputCommand** (loop)
- **QuitRequestEvent** → **ConversationCompleteNode** → **ConversationCompleteEvent**

**Run**: `python -m examples.chat_message_driven.main`

### RAG (Message-Driven)

**Location**: `rag_message_driven/`

A Retrieval-Augmented Generation system with two separate flows:

**Indexing Flow**:
- **IndexDocumentsCommand** → **DocumentChunkerNode** → **DocumentsChunkedEvent**
- **DocumentsChunkedEvent** → **ChunkEmbedderNode** → **ChunksEmbeddedEvent**
- **ChunksEmbeddedEvent** → **IndexCreatorNode** → **IndexCreatedEvent**

**Query Flow**:
- **QueryCommand** → **QueryEmbedderNode** → **QueryEmbeddedEvent**
- **QueryEmbeddedEvent** → **DocumentRetrieverNode** → **DocumentsRetrievedEvent**
- **DocumentsRetrievedEvent** → **AnswerGeneratorNode** → **AnswerGeneratedEvent**

**Run**: `python -m examples.rag_message_driven.main`

## Key Differences from Legacy Architecture

### Legacy (Node-Flow-State)
```python
from clearflow import Node, NodeResult, flow

@dataclass(frozen=True)
class MyNode(Node[StateType]):
    name: str = "my_node"
    
    async def exec(self, state: StateType) -> NodeResult[StateType]:
        return NodeResult(new_state, outcome="done")

flow_instance = flow("Pipeline", start_node).end(end_node, "complete")
```

### Message-Driven
```python
from clearflow import MessageNode, Command, Event, message_flow

@dataclass(frozen=True, kw_only=True)
class ProcessCommand(Command):
    data: str

@dataclass(frozen=True, kw_only=True)
class ProcessedEvent(Event):
    result: str

@dataclass(frozen=True, kw_only=True)
class ProcessorNode(MessageNode[ProcessCommand, ProcessedEvent]):
    name: str = "processor"
    
    async def process(self, message: ProcessCommand) -> ProcessedEvent:
        return ProcessedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            result=f"processed: {message.data}"
        )

flow_instance = (
    message_flow("Pipeline", processor)
    .from_node(processor)
    .end(ProcessedEvent)
)
```

## Benefits of Message-Driven Architecture

1. **Explicit Message Types**: Clear contracts between components
2. **Event Sourcing**: Natural audit trail of all messages
3. **Observable Flows**: Add observers for logging, monitoring, security
4. **Type Safety**: Full generic type checking for message transformations
5. **Immutable Messages**: All messages are frozen dataclasses
6. **Causality Tracking**: Built-in `triggered_by_id` and `flow_id` fields

## Prerequisites

All examples require:
- Python 3.13+
- OpenAI API key in `.env` file or environment

```bash
# Install dependencies
pip install clearflow openai python-dotenv

# Set API key
echo "OPENAI_API_KEY=your_key_here" > .env
```