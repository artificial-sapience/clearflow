"""Message definitions for RAG application."""

from dataclasses import dataclass

from clearflow import Command, Event


@dataclass(frozen=True, kw_only=True)
class IndexDocumentsCommand(Command):
    """Command to index documents for RAG."""

    documents: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class DocumentsChunkedEvent(Event):
    """Event when documents are chunked."""

    chunks: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class ChunksEmbeddedEvent(Event):
    """Event when chunks are embedded."""

    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, kw_only=True)
class IndexCreatedEvent(Event):
    """Event when vector index is created."""

    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]
    index_ready: bool = True


@dataclass(frozen=True, kw_only=True)
class QueryCommand(Command):
    """Command to query the RAG system."""

    query: str
    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, kw_only=True)
class QueryEmbeddedEvent(Event):
    """Event when query is embedded."""

    query: str
    query_embedding: tuple[float, ...]
    chunks: tuple[str, ...]
    embeddings: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, kw_only=True)
class DocumentsRetrievedEvent(Event):
    """Event when relevant documents are retrieved."""

    query: str
    relevant_chunks: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class AnswerGeneratedEvent(Event):
    """Event when answer is generated."""

    query: str
    answer: str
    relevant_chunks: tuple[str, ...]