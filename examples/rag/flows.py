"""Message-driven RAG flow construction."""

from typing import override

from rich.console import Console

from clearflow import Message, Node, Observer, create_flow
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


class SimpleSpinnerObserver(Observer):
    """Simple spinner observer for async operations."""

    def __init__(self) -> None:
        """Initialize the spinner observer."""
        self._console = Console()
        self._spinner = None

    @override
    async def on_node_start(self, node_name: str, message: Message) -> None:
        """Start spinner when any node starts processing."""
        self._spinner = self._console.status(f"[cyan]{node_name}[/cyan] processing...", spinner="dots")
        self._spinner.start()

    @override
    async def on_node_end(self, node_name: str, message: Message, error: Exception | None) -> None:
        """Stop spinner when node completes."""
        if self._spinner:
            self._spinner.stop()
            self._spinner = None


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
        .observe(SimpleSpinnerObserver())
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
        .observe(SimpleSpinnerObserver())
        .route(query_embedder, QueryEmbeddedEvent, retriever)
        .route(retriever, DocumentsRetrievedEvent, generator)
        .end_flow(AnswerGeneratedEvent)  # Terminal type
    )
