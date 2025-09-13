"""Message-driven RAG node implementations."""

import re
from dataclasses import dataclass
from operator import itemgetter
from typing import override

from openai import AsyncOpenAI

from clearflow import MessageNode
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

# Constants for chunking
MAX_CHUNK_LENGTH = 200


def _should_start_new_chunk(current_chunk: str, sentence: str) -> bool:
    """Determine if a new chunk should be started.

    Returns:
        True if new chunk should be started.

    """
    return len(current_chunk) + len(sentence) > MAX_CHUNK_LENGTH and bool(current_chunk)


def _process_document_sentences(sentences: tuple[str, ...]) -> tuple[str, ...]:
    """Process sentences into chunks for a single document.

    Returns:
        Tuple of text chunks for the document.

    """
    current_chunk = ""
    doc_chunks = ()

    for raw_sentence in sentences:
        sentence = raw_sentence.strip()
        if not sentence:
            continue

        # If adding this sentence would make chunk too long, start a new chunk
        if _should_start_new_chunk(current_chunk, sentence):
            doc_chunks = (*doc_chunks, current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = (current_chunk + " " + sentence).strip()

    # Add the last chunk if it exists
    if current_chunk.strip():
        doc_chunks = (*doc_chunks, current_chunk.strip())

    return doc_chunks


def _chunk_documents(documents: tuple[str, ...]) -> tuple[str, ...]:
    """Split documents into smaller chunks.

    Returns:
        Tuple of text chunks.

    """
    all_chunks = ()
    for doc in documents:
        # Simple sentence-based chunking
        sentences = tuple(re.split(r"[.!?]+", doc))
        doc_chunks = _process_document_sentences(sentences)
        all_chunks = (*all_chunks, *doc_chunks)

    return all_chunks


async def _embed_texts(texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    """Embed texts using OpenAI API.

    Returns:
        Tuple of embedding vectors.

    """
    client = AsyncOpenAI()

    embeddings = ()
    for text in texts:
        response = await client.embeddings.create(model="text-embedding-3-small", input=text)
        embedding = tuple(response.data[0].embedding)
        embeddings = (*embeddings, embedding)

    return embeddings


def _calculate_vector_magnitude(vector: tuple[float, ...]) -> float:
    """Calculate the magnitude of a vector.

    Returns:
        Vector magnitude.

    """
    return sum(x**2 for x in vector) ** 0.5


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Calculate cosine similarity between two vectors.

    Returns:
        Cosine similarity score between 0 and 1.

    """
    dot_product = sum(x * y for x, y in zip(a, b, strict=True))
    magnitude_a = _calculate_vector_magnitude(a)
    magnitude_b = _calculate_vector_magnitude(b)

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def _retrieve_relevant_chunks(
    query_embedding: tuple[float, ...], chunks: tuple[str, ...], embeddings: tuple[tuple[float, ...], ...]
) -> tuple[str, ...]:
    """Retrieve most relevant chunks for query.

    Returns:
        Tuple of relevant chunks (top 3).

    """
    similarities = tuple(
        (_cosine_similarity(query_embedding, chunk_emb), chunk)
        for chunk_emb, chunk in zip(embeddings, chunks, strict=True)
    )

    # Sort by similarity and take top 3
    sorted_similarities = tuple(sorted(similarities, reverse=True, key=itemgetter(0)))
    return tuple(chunk for _, chunk in sorted_similarities[:3])


async def _generate_answer(query: str, context_chunks: tuple[str, ...]) -> str:
    """Generate answer using OpenAI API with retrieved context.

    Returns:
        Generated answer string.

    """
    client = AsyncOpenAI()

    context = "\\n".join(context_chunks)
    prompt = f"""Answer the question based on the provided context.

Context:
{context}

Question: {query}

Answer:"""

    response = await client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


@dataclass(frozen=True, kw_only=True)
class DocumentChunkerNode(MessageNode[IndexDocumentsCommand, DocumentsChunkedEvent]):
    """Node that chunks documents into smaller pieces."""

    name: str = "document_chunker"

    @override
    async def process(self, message: IndexDocumentsCommand) -> DocumentsChunkedEvent:
        """Chunk documents into smaller pieces.

        Returns:
            DocumentsChunkedEvent with chunked text.

        """
        chunks = _chunk_documents(message.documents)

        return DocumentsChunkedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            chunks=chunks,
        )


@dataclass(frozen=True, kw_only=True)
class ChunkEmbedderNode(MessageNode[DocumentsChunkedEvent, ChunksEmbeddedEvent]):
    """Node that embeds text chunks using OpenAI API."""

    name: str = "chunk_embedder"

    @override
    async def process(self, message: DocumentsChunkedEvent) -> ChunksEmbeddedEvent:
        """Embed text chunks.

        Returns:
            ChunksEmbeddedEvent with embeddings.

        """
        embeddings = await _embed_texts(message.chunks)

        return ChunksEmbeddedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            chunks=message.chunks,
            embeddings=embeddings,
        )


@dataclass(frozen=True, kw_only=True)
class IndexCreatorNode(MessageNode[ChunksEmbeddedEvent, IndexCreatedEvent]):
    """Node that creates a vector index from embeddings."""

    name: str = "index_creator"

    @override
    async def process(self, message: ChunksEmbeddedEvent) -> IndexCreatedEvent:
        """Create vector index from embeddings.

        Returns:
            IndexCreatedEvent indicating index is ready.

        """
        return IndexCreatedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            chunks=message.chunks,
            embeddings=message.embeddings,
        )


@dataclass(frozen=True, kw_only=True)
class QueryEmbedderNode(MessageNode[QueryCommand, QueryEmbeddedEvent]):
    """Node that embeds query text."""

    name: str = "query_embedder"

    @override
    async def process(self, message: QueryCommand) -> QueryEmbeddedEvent:
        """Embed the query text.

        Returns:
            QueryEmbeddedEvent with query embedding.

        """
        query_embeddings = await _embed_texts((message.query,))
        query_embedding = query_embeddings[0]

        return QueryEmbeddedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            query=message.query,
            query_embedding=query_embedding,
            chunks=message.chunks,
            embeddings=message.embeddings,
        )


@dataclass(frozen=True, kw_only=True)
class DocumentRetrieverNode(MessageNode[QueryEmbeddedEvent, DocumentsRetrievedEvent]):
    """Node that retrieves relevant documents based on query embedding."""

    name: str = "document_retriever"

    @override
    async def process(self, message: QueryEmbeddedEvent) -> DocumentsRetrievedEvent:
        """Retrieve relevant documents for the query.

        Returns:
            DocumentsRetrievedEvent with relevant chunks.

        """
        relevant_chunks = _retrieve_relevant_chunks(
            message.query_embedding,
            message.chunks,
            message.embeddings,
        )

        return DocumentsRetrievedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            query=message.query,
            relevant_chunks=relevant_chunks,
        )


@dataclass(frozen=True, kw_only=True)
class AnswerGeneratorNode(MessageNode[DocumentsRetrievedEvent, AnswerGeneratedEvent]):
    """Node that generates answers using retrieved documents."""

    name: str = "answer_generator"

    @override
    async def process(self, message: DocumentsRetrievedEvent) -> AnswerGeneratedEvent:
        """Generate answer from query and relevant documents.

        Returns:
            AnswerGeneratedEvent with generated answer.

        """
        answer = await _generate_answer(message.query, message.relevant_chunks)

        return AnswerGeneratedEvent(
            triggered_by_id=message.id,
            flow_id=message.flow_id,
            query=message.query,
            answer=answer,
            relevant_chunks=message.relevant_chunks,
        )
