"""Message-driven RAG flow construction."""

from clearflow import MessageFlow, message_flow
from examples.rag_message_driven.messages import (
    AnswerGeneratedEvent,
    ChunksEmbeddedEvent,
    DocumentsChunkedEvent,
    DocumentsRetrievedEvent,
    IndexCreatedEvent,
    IndexDocumentsCommand,
    QueryCommand,
    QueryEmbeddedEvent,
)
from examples.rag_message_driven.nodes import (
    AnswerGeneratorNode,
    ChunkEmbedderNode,
    DocumentChunkerNode,
    DocumentRetrieverNode,
    IndexCreatorNode,
    QueryEmbedderNode,
)


def create_indexing_flow() -> MessageFlow[IndexDocumentsCommand, IndexCreatedEvent]:
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
        message_flow("DocumentIndexing", chunker)
        .from_node(chunker)
        .route(DocumentsChunkedEvent, embedder)
        .from_node(embedder)
        .route(ChunksEmbeddedEvent, indexer)
        .from_node(indexer)
        .end(IndexCreatedEvent)
    )


def create_query_flow() -> MessageFlow[QueryCommand, AnswerGeneratedEvent]:
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
        message_flow("QueryProcessing", query_embedder)
        .from_node(query_embedder)
        .route(QueryEmbeddedEvent, retriever)
        .from_node(retriever)
        .route(DocumentsRetrievedEvent, generator)
        .from_node(generator)
        .end(AnswerGeneratedEvent)
    )