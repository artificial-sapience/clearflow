#!/usr/bin/env python
"""Main entry point for message-driven RAG example."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.rag.flows import create_indexing_flow, create_query_flow
from examples.rag.messages import AnswerGeneratedEvent, IndexDocumentsCommand, QueryCommand
from tests.conftest import create_run_id


def get_sample_documents() -> tuple[tuple[str, str], ...]:
    """Get sample documents with titles for indexing.

    Returns:
        Tuple of (title, content) pairs simulating an environmental research organization's knowledge base.

    """
    return (
        # Overview document
        (
            "PFAS Contamination Overview - Research Brief 2024",
            """Per- and polyfluoroalkyl substances (PFAS) are synthetic chemicals used since the 1940s.
        Known as 'forever chemicals' due to their inability to break down naturally.
        Found in 45% of US drinking water according to 2024 EPA studies.
        Health impacts include cancer, liver damage, decreased fertility, and increased cholesterol.
        Traditional remediation methods like activated carbon have 60-90% effectiveness but high costs.""",
        ),
        # Main research breakthrough
        (
            "Mycelium Strain HI-271 - Breakthrough in PFAS Remediation",
            """Harlow Institute's genetically engineered Mycelium Strain HI-271 achieves 99.7% PFAS removal.
        The fungi's modified enzymes break carbon-fluorine bonds previously thought unbreakable.
        Creates symbiotic networks with native soil bacteria enhancing breakdown efficiency.
        Complete mineralization of PFAS compounds occurs within 60 days of inoculation.
        No toxic byproducts detected in comprehensive metabolite analysis.""",
        ),
        # Comparative analysis
        (
            "Remediation Methods Comparison Study - Q3 2024",
            """Traditional excavation and disposal: $300-500 per ton, creates secondary waste.
        Activated carbon filtration: $150-200 per ton, 60-90% effective, requires regeneration.
        Incineration: $400-600 per ton, energy-intensive, potential air emissions.
        Chemical oxidation: $200-350 per ton, 70-85% effective, may create byproducts.
        Mycelium HI-271: $50-80 per ton, 99.7% effective, self-sustaining process.""",
        ),
        # Field test results
        (
            "Michigan Industrial Site - Field Test Report",
            """Former automotive plant with severe PFAS contamination (>10,000 ppt).
        HI-271 deployed across 5-acre test zone in April 2024.
        Week 2: Mycelium network established, 15% PFAS reduction measured.
        Week 4: Symbiotic bacteria colonies detected, 67% PFAS reduction.
        Week 8: 99.2% total PFAS reduction, soil pH normalized, native plants returning.
        Control zones using activated carbon showed only 71% reduction in same period.""",
        ),
        # Implementation guide
        (
            "HI-271 Deployment Protocol - Standard Operating Procedures",
            """Site preparation: Test soil pH (optimal 5.5-7.5), moisture content (30-40%).
        Inoculation rate: 100kg spawn per acre for heavy contamination (>5000 ppt PFAS).
        Temperature requirements: Maintain 15-25°C for optimal enzyme activity.
        Monitoring: Weekly PFAS levels, fungal biomass, and bacterial colony counts.
        Supplementation: Add agricultural waste monthly to sustain fungal growth.
        Timeline: Expect 95% reduction by week 6, full remediation by week 10.""",
        ),
    )


async def run_indexing_phase() -> tuple[tuple[str, ...], tuple[tuple[float, ...], ...]]:
    """Run the document indexing phase.

    Returns:
        Tuple containing (chunks, embeddings) for query phase.

    """
    print("\n📚 DOCUMENT INDEXING PHASE")
    print("=" * 60)
    print("Loading Harlow Institute's Environmental Remediation Knowledge Base...")
    print("\nDocuments being indexed:\n")

    # Create indexing flow
    indexing_flow = create_indexing_flow()

    # Get and display documents
    doc_pairs = get_sample_documents()
    documents: tuple[str, ...] = ()
    for i, (title, content) in enumerate(doc_pairs, 1):
        print(f"{i}. 📄 {title}")
        preview_length = 100
        print(f"   {content[:preview_length]}..." if len(content) > preview_length else f"   {content}")
        documents = (*documents, content)

    print(f"\n🔧 Processing {len(documents)} documents through RAG pipeline...")

    # Create indexing command
    index_command = IndexDocumentsCommand(
        triggered_by_id=None,
        run_id=create_run_id(),
        documents=documents,
    )

    # Process indexing
    index_result = await indexing_flow.process(index_command)

    print("\n✅ SUCCESS: Created searchable knowledge base")
    print(f"   • Split into {len(index_result.chunks)} searchable chunks")
    print(f"   • Generated {len(index_result.embeddings)} vector embeddings")
    print("   • Ready for semantic similarity search")

    return index_result.chunks, index_result.embeddings


def _print_query_instructions() -> None:
    """Print instructions for the query phase."""
    print("\n\n🔍 QUERY PHASE - Semantic Search of Knowledge Base")
    print("=" * 60)
    print("Ask questions about PFAS remediation and the HI-271 mycelium solution.")
    print("\nExample questions about our specific research data:")
    print("  • What were the week-by-week results at the Michigan site?")
    print("  • How much does HI-271 cost compared to incineration?")
    print("  • What's the optimal soil pH for HI-271 deployment?")
    print("  • What percentage of PFAS did HI-271 remove in field tests?")
    print("  • How does HI-271 break down the carbon-fluorine bonds?")
    print("  • What inoculation rate is needed for heavy contamination?")
    print("\nThe RAG system uses semantic search to find relevant information")
    print("and generates answers based on the indexed research documents.")
    print("\nType 'quit' to exit.")


def _print_query_results(answer_result: AnswerGeneratedEvent) -> None:
    """Print the results of a query."""
    print(f"\n💡 Answer: {answer_result.answer}")

    if answer_result.relevant_chunks:
        print("\n📚 Source context (most relevant chunk):")
        context_preview = 150
        print(f'   "{answer_result.relevant_chunks[0][:context_preview]}..."')

    print(f"\n📊 Search metrics: Found {len(answer_result.relevant_chunks)} relevant chunk(s)")


async def run_query_phase(chunks: tuple[str, ...], embeddings: tuple[tuple[float, ...], ...]) -> None:
    """Run the query processing phase.

    Args:
        chunks: Text chunks from indexing
        embeddings: Vector embeddings from indexing

    """
    _print_query_instructions()

    # Create query flow
    query_flow = create_query_flow()

    while True:
        try:
            query_text = await asyncio.to_thread(input, "\n❓ Your question: ")
            query_text = query_text.strip()

            if query_text.lower() in {"quit", "exit", "bye"}:
                print("\n👋 Thank you for trying the RAG example!")
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
            print("\n⚙️  RAG Pipeline Processing:")
            print("   1. Converting question to embedding...")
            print("   2. Searching for similar chunks...")
            print("   3. Generating answer from context...")

            answer_result = await query_flow.process(query_command)
            _print_query_results(answer_result)

        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Thank you for trying the RAG example!")
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

    print("\n" + "=" * 70)
    print("🧪 HARLOW INSTITUTE - ENVIRONMENTAL REMEDIATION KNOWLEDGE BASE")
    print("=" * 70)
    print("\nThis RAG example simulates how a research organization uses")
    print("Retrieval-Augmented Generation to query their internal documents.")
    print("\nRAG Pipeline Steps:")
    print("1. INDEX: Split research documents into searchable chunks")
    print("2. EMBED: Convert text to vector representations")
    print("3. SEARCH: Find relevant chunks using cosine similarity")
    print("4. GENERATE: Create answers using only retrieved context")

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
