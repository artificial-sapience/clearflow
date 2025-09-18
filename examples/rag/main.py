#!/usr/bin/env python
"""Main entry point for message-driven RAG example."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.rag.messages import IndexDocumentsCommand, QueryCommand
from examples.rag.rag_flows import create_indexing_flow, create_query_flow
from tests.conftest import create_run_id


def get_sample_documents() -> tuple[str, ...]:
    """Get sample documents for indexing.

    Returns:
        Tuple of document strings

    """
    return (
        # ClearFlow framework
        """ClearFlow is a type-safe workflow orchestration framework for Python.
        It provides 100% test coverage and minimal dependencies.
        Nodes transform immutable state through explicit routing.
        Single termination enforcement ensures no ambiguous endings.
        To install: pip install clearflow""",
        # Fictional medical device
        """NeurAlign M7 is a revolutionary non-invasive neural alignment device.
        Targeted magnetic resonance technology increases neuroplasticity in specific brain regions.
        Clinical trials showed 72% improvement in PTSD treatment outcomes.
        Developed by Cortex Medical in 2024 as an adjunct to standard cognitive therapy.
        Portable design allows for in-home use with remote practitioner monitoring.""",
        # Made-up historical event
        """The Velvet Revolution of Caldonia (1967-1968) ended Generalissimo Verak's 40-year rule.
        Led by poet Eliza Markovian through underground literary societies.
        Culminated in the Great Silence Protest with 300,000 silent protesters.
        First democratic elections held in March 1968 with 94% voter turnout.
        Became a model for non-violent political transitions in neighboring regions.""",
        # Fictional technology
        """Q-Mesh is QuantumLeap Technologies' instantaneous data synchronization protocol.
        Utilizes directed acyclic graph consensus for 500,000 transactions per second.
        Consumes 95% less energy than traditional blockchain systems.
        Adopted by three central banks for secure financial data transfer.
        Released in February 2024 after five years of development in stealth mode.""",
        # Made-up scientific research
        """Harlow Institute's Mycelium Strain HI-271 removes 99.7% of PFAS from contaminated soil.
        Engineered fungi create symbiotic relationships with native soil bacteria.
        Breaks down "forever chemicals" into non-toxic compounds within 60 days.
        Field tests successfully remediated previously permanently contaminated industrial sites.
        Deployment costs 80% less than traditional chemical extraction methods.""",
    )


async def run_indexing_phase() -> tuple[tuple[str, ...], tuple[tuple[float, ...], ...]]:
    """Run the document indexing phase.

    Returns:
        Tuple containing (chunks, embeddings) for query phase.

    """
    print("📚 Indexing documents...")

    # Create indexing flow
    indexing_flow = create_indexing_flow()

    # Create indexing command
    documents = get_sample_documents()
    index_command = IndexDocumentsCommand(
        triggered_by_id=None,
        run_id=create_run_id(),
        documents=documents,
    )

    # Process indexing
    index_result = await indexing_flow.process(index_command)

    print(f"✅ Indexed {len(index_result.chunks)} chunks")
    return index_result.chunks, index_result.embeddings


async def run_query_phase(chunks: tuple[str, ...], embeddings: tuple[tuple[float, ...], ...]) -> None:
    """Run the query processing phase.

    Args:
        chunks: Text chunks from indexing
        embeddings: Vector embeddings from indexing

    """
    print("\\n🔍 Ready for queries!")
    print("Type 'quit' to exit.")

    # Create query flow
    query_flow = create_query_flow()

    while True:
        try:
            query_text = await asyncio.to_thread(input, "\\nEnter your question: ")
            query_text = query_text.strip()

            if query_text.lower() in {"quit", "exit", "bye"}:
                print("Goodbye!")
                break

            if not query_text:
                continue

            # Create query command
            query_command = QueryCommand(
                triggered_by_id=None,
                run_id=create_run_id(),
                query=query_text,
                chunks=chunks,
                embeddings=embeddings,
            )

            # Process query
            print("\\n🤔 Thinking...")
            answer_result = await query_flow.process(query_command)

            print(f"\\n💡 Answer: {answer_result.answer}")
            print(f"\\n📖 Based on {len(answer_result.relevant_chunks)} relevant sources")

        except (EOFError, KeyboardInterrupt):
            print("\\nGoodbye!")
            break


async def main() -> None:
    """Run the message-driven RAG application."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    print("🚀 Message-Driven RAG Example")
    print("=" * 50)

    try:
        # Run indexing phase
        chunks, embeddings = await run_indexing_phase()

        # Run query phase
        await run_query_phase(chunks, embeddings)

    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
