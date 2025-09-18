"""Message-driven RAG node implementations."""

from typing import override

import faiss
import numpy as np

from clearflow import Node
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
from examples.rag.utils import call_llm, fixed_size_chunk, get_embedding


class DocumentChunkerNode(Node[IndexDocumentsCommand, DocumentsChunkedEvent]):
    """Node that chunks documents into smaller pieces using overlap."""

    name: str = "document_chunker"

    @override
    async def process(self, message: IndexDocumentsCommand) -> DocumentsChunkedEvent:
        """Chunk documents into smaller pieces with overlap.

        Returns:
            DocumentsChunkedEvent with chunked text.

        """
        # Use proper chunking with overlap like the working RAG implementation
        all_chunks = tuple(chunk for doc in message.documents for chunk in fixed_size_chunk(doc))

        print(f"✅ Created {len(all_chunks)} chunks from {len(message.documents)} documents")

        return DocumentsChunkedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            chunks=all_chunks,
        )


class ChunkEmbedderNode(Node[DocumentsChunkedEvent, ChunksEmbeddedEvent]):
    """Node that embeds text chunks using OpenAI API with numpy arrays."""

    name: str = "chunk_embedder"

    @override
    async def process(self, message: DocumentsChunkedEvent) -> ChunksEmbeddedEvent:
        """Embed text chunks using proper numpy arrays.

        Returns:
            ChunksEmbeddedEvent with embeddings.

        """
        # Create embeddings using numpy arrays like the working implementation
        embeddings_tuple = tuple(get_embedding(chunk) for chunk in message.chunks)

        # Show progress
        for i in range(len(embeddings_tuple)):
            print(f"  Embedded chunk {i + 1}/{len(message.chunks)}", end="\r")

        embeddings = np.array(embeddings_tuple, dtype=np.float32)
        print(f"✅ Created {len(embeddings)} document embeddings")

        # Convert numpy array to tuple of tuples for message serialization
        embeddings_tuple = tuple(tuple(row.tolist()) for row in embeddings)

        return ChunksEmbeddedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            chunks=message.chunks,
            embeddings=embeddings_tuple,
        )


class IndexCreatorNode(Node[ChunksEmbeddedEvent, IndexCreatedEvent]):
    """Node that creates a FAISS index from embeddings."""

    name: str = "index_creator"

    @override
    async def process(self, message: ChunksEmbeddedEvent) -> IndexCreatedEvent:
        """Create FAISS index from embeddings.

        Returns:
            IndexCreatedEvent indicating index is ready.

        Raises:
            ValueError: If no embeddings are available to index.

        """
        print("🔍 Creating search index...")

        if not message.embeddings:
            msg = "No embeddings to index"
            raise ValueError(msg)

        # Convert tuple of tuples back to numpy array
        embeddings_array = np.array(message.embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]

        # Create a flat L2 index (same as working RAG)
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)

        print(f"✅ Index created with {index.ntotal} vectors")

        return IndexCreatedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            chunks=message.chunks,
            embeddings=message.embeddings,
        )


class QueryEmbedderNode(Node[QueryCommand, QueryEmbeddedEvent]):
    """Node that embeds query text."""

    name: str = "query_embedder"

    @override
    async def process(self, message: QueryCommand) -> QueryEmbeddedEvent:
        """Embed the query text.

        Returns:
            QueryEmbeddedEvent with query embedding.

        """
        print(f"🔍 Embedding query: {message.query}")

        query_embedding = get_embedding(message.query)
        # Convert to tuple for message serialization
        query_embedding_tuple = tuple(query_embedding.tolist())

        return QueryEmbeddedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            query=message.query,
            query_embedding=query_embedding_tuple,
            chunks=message.chunks,
            embeddings=message.embeddings,
        )


class DocumentRetrieverNode(Node[QueryEmbeddedEvent, DocumentsRetrievedEvent]):
    """Node that retrieves relevant documents using FAISS search."""

    name: str = "document_retriever"

    @override
    async def process(self, message: QueryEmbeddedEvent) -> DocumentsRetrievedEvent:
        """Retrieve the most relevant document chunk using FAISS.

        Returns:
            DocumentsRetrievedEvent with relevant chunk (single best match).

        """
        print("🔎 Searching for relevant documents...")

        # Reconstruct FAISS index and embeddings
        embeddings_array = np.array(message.embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]

        # Recreate the index
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)

        # Convert query embedding back to numpy array
        query_embedding_array = np.array([message.query_embedding], dtype=np.float32)

        # Search for the single most similar document (k=1 like working RAG)
        distances, indices = index.search(query_embedding_array, k=1)

        # Get the index and distance of the most similar document
        best_idx = int(indices[0][0])
        distance = float(distances[0][0])

        # Get the corresponding text
        most_relevant_text = message.chunks[best_idx]

        print(f"📄 Retrieved document (index: {best_idx}, distance: {distance:.4f})")
        print(f'📄 Most relevant text: "{most_relevant_text[:200]}..."')

        # Return single relevant chunk (not multiple chunks)
        relevant_chunks = (most_relevant_text,)

        return DocumentsRetrievedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            query=message.query,
            relevant_chunks=relevant_chunks,
        )


class AnswerGeneratorNode(Node[DocumentsRetrievedEvent, AnswerGeneratedEvent]):
    """Node that generates answers using retrieved documents."""

    name: str = "answer_generator"

    @override
    async def process(self, message: DocumentsRetrievedEvent) -> AnswerGeneratedEvent:
        """Generate answer from query and relevant documents.

        Returns:
            AnswerGeneratedEvent with generated answer.

        """
        # Use the same prompt format as working RAG
        context = "\n".join(message.relevant_chunks)
        prompt = f"""Briefly answer the following question based on the context provided:
Question: {message.query}
Context: {context}
Answer:"""

        answer = call_llm(prompt)

        print("\n🤖 Generated Answer:")
        print(answer)

        return AnswerGeneratedEvent(
            triggered_by_id=message.id,
            run_id=message.run_id,
            query=message.query,
            answer=answer,
            relevant_chunks=message.relevant_chunks,
        )
