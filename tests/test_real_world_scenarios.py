"""Test real-world AI orchestration scenarios with ClearFlow.

This module tests realistic LLM agent scenarios including RAG pipelines,
tool-using agents, and multi-step workflows.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Flow, Node, NodeResult


class TestRealWorldScenarios:
    """Test realistic LLM agent scenarios."""

    @staticmethod
    async def test_rag_pipeline() -> None:
        """Test a Retrieval-Augmented Generation pipeline."""

        @dc(frozen=True)
        class RetrieverNode(Node[dict[str, object]]):
            """Simulates document retrieval."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                query = state.get("query", "")

                # Simulate retrieval
                if "machine learning" in str(query).lower():
                    docs = [
                        (
                            "ML is a subset of AI focused on algorithms that "
                            "improve through experience."
                        ),
                        (
                            "Common ML techniques include neural networks and "
                            "decision trees."
                        ),
                    ]
                else:
                    docs = ["No relevant documents found."]

                new_state = {**state, "retrieved_docs": docs}
                outcome = "docs_found" if len(docs) > 1 else "no_docs"
                return NodeResult(new_state, outcome=outcome)

        @dc(frozen=True)
        class GeneratorNode(Node[dict[str, object]]):
            """Simulates LLM generation with context."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                docs = state.get("retrieved_docs", [])

                if docs and docs[0] != "No relevant documents found.":
                    response = f"Based on the documents: {docs[0]}"
                else:
                    response = (
                        "I don't have enough information to answer that question."
                    )

                new_state = {**state, "response": response}
                return NodeResult(new_state, outcome="generated")

        # Build RAG pipeline
        retriever = RetrieverNode()
        generator = GeneratorNode()

        rag_pipeline = (
            Flow[dict[str, object]]("RAGPipeline")
            .start_with(retriever)
            .route(retriever, "docs_found", generator)
            .route(retriever, "no_docs", generator)
            .route(generator, "generated", None)
            .build()
        )

        # Test with relevant query
        result = await rag_pipeline({"query": "What is machine learning?"})
        assert "ML is a subset of AI" in result.state["response"]

        # Test with irrelevant query
        result = await rag_pipeline({"query": "What's for dinner?"})
        assert "don't have enough information" in result.state["response"]

    @staticmethod
    async def test_agent_with_tools() -> None:
        """Test an agent that can use tools."""

        @dc(frozen=True)
        class PlannerNode(Node[dict[str, object]]):
            """Plans which tool to use."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                task = state.get("task", "")

                if "calculate" in str(task).lower():
                    tool = "calculator"
                elif "search" in str(task).lower():
                    tool = "web_search"
                elif "code" in str(task).lower():
                    tool = "code_interpreter"
                else:
                    tool = "none"

                new_state = {**state, "selected_tool": tool}
                return NodeResult(new_state, outcome=tool)

        @dc(frozen=True)
        class CalculatorNode(Node[dict[str, object]]):
            """Simulates calculator tool."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                # Simulate calculation
                new_state = {**state, "result": "42", "tool_used": "calculator"}
                return NodeResult(new_state, outcome="calculated")

        @dc(frozen=True)
        class SearchNode(Node[dict[str, object]]):
            """Simulates web search tool."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                # Simulate search
                new_state = {
                    **state,
                    "result": "Found 10 relevant results",
                    "tool_used": "web_search",
                }
                return NodeResult(new_state, outcome="searched")

        @dc(frozen=True)
        class ResponseNode(Node[dict[str, object]]):
            """Generates final response."""

            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                tool_used = state.get("tool_used", "none")
                result = state.get("result", "No result")

                if tool_used != "none":
                    response = f"Used {tool_used}: {result}"
                else:
                    response = "I can help with calculations, searches, and code."

                new_state = {**state, "final_response": response}
                return NodeResult(new_state, outcome="responded")

        # Build agent flow
        planner = PlannerNode()
        calculator = CalculatorNode()
        search = SearchNode()
        responder = ResponseNode()

        agent = (
            Flow[dict[str, object]]("ToolAgent")
            .start_with(planner)
            .route(planner, "calculator", calculator)
            .route(planner, "web_search", search)
            .route(planner, "code_interpreter", responder)  # Not implemented
            .route(planner, "none", responder)
            .route(calculator, "calculated", responder)
            .route(search, "searched", responder)
            .route(responder, "responded", None)
            .build()
        )

        # Test calculator path
        calc_result = await agent({"task": "Calculate 6 * 7"})
        assert calc_result.state["tool_used"] == "calculator"
        assert "calculator" in calc_result.state["final_response"]

        # Test search path
        search_result = await agent({"task": "Search for Python tutorials"})
        assert search_result.state["tool_used"] == "web_search"
        assert "web_search" in search_result.state["final_response"]

        # Test no tool path
        no_tool_result = await agent({"task": "Hello there"})
        assert no_tool_result.state.get("tool_used") is None
        assert "can help" in no_tool_result.state["final_response"]