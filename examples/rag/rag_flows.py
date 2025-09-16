"""Message-driven RAG flow construction."""

from clearflow import Node, create_flow
from examples.rag.messages import (
    AnswerGeneratedEvent,
    ChunksEmbeddedEvent,
    DocumentsChunkedEvent,
    DocumentsRetrievedEvent,
    IndexCreatedEvent,
    IndexDocumentsCommand,
    QueryCommand,
    QueryEmbeddedEvent,
)
from examples.rag.nodes import (
    AnswerGeneratorNode,
    ChunkEmbedderNode,
    DocumentChunkerNode,
    DocumentRetrieverNode,
    IndexCreatorNode,
    QueryEmbedderNode,
)


def create_indexing_flow() -> Node[IndexDocumentsCommand, IndexCreatedEvent]:
    """Create message-driven document indexing flow.

    This flow processes documents through these steps:
    1. IndexDocumentsCommand -> DocumentChunkerNode -> DocumentsChunkedEvent
    2. DocumentsChunkedEvent -> ChunkEmbedderNode -> ChunksEmbeddedEvent
    3. ChunksEmbeddedEvent -> IndexCreatorNode -> IndexCreatedEvent

    Returns:
        MessageFlow for document indexing.

    """
    chunker = DocumentChunkerNode()
    embedder = ChunkEmbedderNode()
    indexer = IndexCreatorNode()

    return (
        create_flow("DocumentIndexing", chunker)
        .route(chunker, DocumentsChunkedEvent, embedder)
        .route(embedder, ChunksEmbeddedEvent, indexer)
        .end_flow(IndexCreatedEvent)  # Terminal type
    )


def create_query_flow() -> Node[QueryCommand, AnswerGeneratedEvent]:
    """Create message-driven query processing flow.

    This flow processes queries through these steps:
    1. QueryCommand -> QueryEmbedderNode -> QueryEmbeddedEvent
    2. QueryEmbeddedEvent -> DocumentRetrieverNode -> DocumentsRetrievedEvent
    3. DocumentsRetrievedEvent -> AnswerGeneratorNode -> AnswerGeneratedEvent

    Returns:
        MessageFlow for query processing.

    """
    query_embedder = QueryEmbedderNode()
    retriever = DocumentRetrieverNode()
    generator = AnswerGeneratorNode()

    return (
        create_flow("QueryProcessing", query_embedder)
        .route(query_embedder, QueryEmbeddedEvent, retriever)
        .route(retriever, DocumentsRetrievedEvent, generator)
        .end_flow(AnswerGeneratedEvent)  # Terminal type
    )
