# Retrieval-Augmented Generation (RAG) Example

This example demonstrates a complete RAG system using ClearFlow's type-safe orchestration.

## Overview

RAG combines document retrieval with language model generation to answer questions using specific context. This implementation follows the classic two-phase pattern:

1. **Offline Indexing**: Process and index documents for fast retrieval
2. **Online Query**: Retrieve relevant context and generate answers

## Flow

```mermaid
graph TD
    subgraph Offline Flow
        ChunkDocuments --> EmbedDocuments --> CreateIndex
    end
    
    subgraph Online Flow
        EmbedQuery --> RetrieveDocument --> GenerateAnswer
    end
```

### Offline Flow Nodes

- **ChunkDocumentsNode**: Splits documents into overlapping chunks (500 chars with 50 char overlap)
- **EmbedDocumentsNode**: Converts chunks to vector embeddings using OpenAI
- **CreateIndexNode**: Builds FAISS vector index for similarity search

### Online Flow Nodes

- **EmbedQueryNode**: Converts user query to embedding
- **RetrieveDocumentNode**: Finds most similar document chunk
- **GenerateAnswerNode**: Uses GPT-4 to generate answer with retrieved context

## State Transformations

ClearFlow's type system tracks state transformations through the pipeline:

```python
RAGState → ChunkedState → EmbeddedState → IndexedState
QueryState → RetrievedState → AnsweredState
```

Each transformation is immutable, creating new state objects with additional fields.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

```bash
# Run with default query
python main.py

# Run with custom query
python main.py "What is Q-Mesh protocol?"

# Alternative syntax
python main.py --How does NeurAlign M7 work?
```

## Key Features

- **Type Safety**: Full typing with state transformations
- **Immutable State**: Each node creates new state objects
- **Explicit Routing**: Clear flow definition with single termination
- **Error Handling**: Validates state at each step

## Comparison with PocketFlow RAG

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **State** | Immutable dataclasses | Mutable dict |
| **Typing** | Full type inference | Dynamic |
| **Routing** | Explicit with outcomes | Sequential `>>` |
| **Nodes** | Frozen dataclasses | Regular classes |

## Files

- `models.py` - State definitions with type hierarchy
- `nodes.py` - Node implementations for both flows
- `rag_flow.py` - Flow composition and routing
- `utils.py` - OpenAI integration utilities
- `main.py` - Entry point and orchestration