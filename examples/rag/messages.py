"""Message definitions for RAG application."""

from clearflow import Command, Event


class IndexDocumentsCommand(Command):
    """Command to index documents for RAG."""

    documents: tuple[str, ...]


class DocumentsChunkedEvent(Event):
    """Event when documents are chunked."""

    chunks: tuple[str, ...]


class ChunksEmbeddedEvent(Event):
    """Event when chunks are embedded."""

    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


class IndexCreatedEvent(Event):
    """Event when vector index is created."""

    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]
    index_ready: bool = True


class QueryCommand(Command):
    """Command to query the RAG system."""

    query: str
    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


class QueryEmbeddedEvent(Event):
    """Event when query is embedded."""

    query: str
    query_embedding: tuple[float, ...]
    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


class DocumentsRetrievedEvent(Event):
    """Event when relevant documents are retrieved."""

    query: str
    relevant_chunks: tuple[str, ...]


class AnswerGeneratedEvent(Event):
    """Event when answer is generated."""

    query: str
    answer: str
    relevant_chunks: tuple[str, ...]
