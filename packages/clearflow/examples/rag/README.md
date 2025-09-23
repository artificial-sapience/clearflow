# RAG Example

Retrieval-Augmented Generation pipeline using ClearFlow's message-driven architecture.

This example simulates an environmental research organization's knowledge base containing documents about PFAS contamination and mycelium-based remediation methods.

## Flows

### Indexing Flow

```mermaid
graph LR
    Start([IndexDocumentsCommand]) --> Chunker[DocumentChunkerNode]
    Chunker -->|DocumentsChunkedEvent| Embedder[ChunkEmbedderNode]
    Embedder -->|ChunksEmbeddedEvent| Indexer[IndexCreatorNode]
    Indexer -->|IndexCreatedEvent| End([Complete])
```

### Query Flow

```mermaid
graph LR
    Start([QueryCommand]) --> QueryEmbed[QueryEmbedderNode]
    QueryEmbed -->|QueryEmbeddedEvent| Retriever[DocumentRetrieverNode]
    Retriever -->|DocumentsRetrievedEvent| Generator[AnswerGeneratorNode]
    Generator -->|AnswerGeneratedEvent| End([Complete])
```

## Quick Start

```bash
# From project root directory

# 1. Set up your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Install dependencies
uv sync --all-extras

# 3. Run the example
cd examples/rag
uv run python main.py
# With custom query:
uv run python main.py "How does HI-271 compare to traditional methods?"
```

## How It Works

RAG combines document retrieval with language model generation. This example uses two message-driven flows:

### Indexing

1. **DocumentChunkerNode** - Splits documents into overlapping chunks (500 chars)
2. **ChunkEmbedderNode** - Creates OpenAI embeddings for each chunk
3. **IndexCreatorNode** - Builds FAISS vector index for similarity search

### Query

1. **QueryEmbedderNode** - Converts user query to embedding
2. **DocumentRetrieverNode** - Finds most similar chunks via cosine similarity
3. **AnswerGeneratorNode** - Uses GPT-4 with retrieved context to answer

## Key Features

- **Message-driven** - Commands trigger actions, Events record results
- **Two-phase architecture** - Separate indexing and query flows
- **Type-safe messages** - Each node produces specific event types
- **Vector search** - FAISS for efficient similarity matching
- **Observable** - Progress spinners during async operations

## Files

- `main.py` - Entry point and flow orchestration
- `rag_flows.py` - Message-driven flow definitions
- `nodes.py` - All node implementations
- `messages.py` - Command and Event types
- `utils.py` - OpenAI API and chunking utilities
