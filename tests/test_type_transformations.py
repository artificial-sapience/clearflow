"""Test type transformation features of ClearFlow.

This module tests Node[TIn, TOut] type transformations for real AI pipelines,
demonstrating how to avoid "god objects" through type-safe transformations.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Node, NodeResult
from tests.conftest import Document


class TestTypeTransformations:
    """Test Node[TIn, TOut] type transformations for real AI pipelines."""
    
    @staticmethod
    async def test_rag_pipeline_transformations() -> None:
        """Test a complete RAG pipeline with multiple type transformations."""
        
        @dc(frozen=True)
        class Query:
            """User query for RAG system."""
            text: str
            max_results: int = 5
        
        @dc(frozen=True)
        class SearchResults:
            """Retrieved documents with scores."""
            query: Query
            documents: tuple[tuple[Document, float], ...]  # (doc, relevance_score)
        
        @dc(frozen=True)
        class Context:
            """Prepared context for generation."""
            query: Query
            relevant_texts: tuple[str, ...]
            total_tokens: int
        
        @dc(frozen=True)
        class Response:
            """Final generated response."""
            query: Query
            answer: str
            sources: tuple[str, ...]
        
        # Node 1: Query → SearchResults
        @dc(frozen=True)
        class RetrievalNode(Node[Query, SearchResults]):
            """Retrieves relevant documents."""
            
            @override
            async def exec(self, state: Query) -> NodeResult[SearchResults]:
                # Simulate retrieval
                mock_docs = (
                    (Document("AI is transforming industries", "doc1.pdf"), 0.95),
                    (Document("Machine learning applications", "doc2.pdf"), 0.87),
                )
                results = SearchResults(query=state, documents=mock_docs[:state.max_results])
                return NodeResult(results, outcome="retrieved")
        
        # Node 2: SearchResults → Context
        @dc(frozen=True)
        class ContextBuilder(Node[SearchResults, Context]):
            """Builds context from search results."""
            
            @override
            async def exec(self, state: SearchResults) -> NodeResult[Context]:
                texts = tuple(doc.content for doc, _ in state.documents)
                tokens = sum(len(text.split()) for text in texts)
                context = Context(query=state.query, relevant_texts=texts, total_tokens=tokens)
                outcome = "context_ready" if tokens < 1000 else "context_too_long"
                return NodeResult(context, outcome=outcome)
        
        # Node 3: Context → Response
        @dc(frozen=True)
        class GenerationNode(Node[Context, Response]):
            """Generates response from context."""
            
            @override
            async def exec(self, state: Context) -> NodeResult[Response]:
                # Simulate generation
                answer = f"Based on {len(state.relevant_texts)} sources: " + state.relevant_texts[0][:50]
                sources = tuple(f"doc{i+1}.pdf" for i in range(len(state.relevant_texts)))
                response = Response(query=state.query, answer=answer, sources=sources)
                return NodeResult(response, outcome="generated")
        
        # Test the pipeline transformations
        query = Query(text="How is AI transforming industries?", max_results=2)
        
        # Query → SearchResults
        retrieval = RetrievalNode()
        search_result = await retrieval(query)
        assert isinstance(search_result.state, SearchResults)
        assert len(search_result.state.documents) == 2
        
        # SearchResults → Context
        context_builder = ContextBuilder()
        context_result = await context_builder(search_result.state)
        assert isinstance(context_result.state, Context)
        assert context_result.state.total_tokens > 0
        
        # Context → Response
        generator = GenerationNode()
        final_result = await generator(context_result.state)
        assert isinstance(final_result.state, Response)
        assert final_result.state.query == query  # Original query preserved
        assert len(final_result.state.sources) > 0
    
    @staticmethod
    async def test_tool_use_transformation() -> None:
        """Test tool selection and execution with type transformations."""
        
        @dc(frozen=True)
        class ToolQuery:
            """Initial query requiring tool use."""
            question: str
            context: str = ""
        
        @dc(frozen=True)
        class ToolPlan:
            """Plan for which tool to use."""
            query: ToolQuery
            selected_tool: str
            parameters: tuple[tuple[str, str], ...]
        
        @dc(frozen=True)
        class ToolResult:
            """Result from tool execution."""
            plan: ToolPlan
            output: str
            success: bool
        
        # Node: ToolQuery → ToolPlan
        @dc(frozen=True)
        class PlannerNode(Node[ToolQuery, ToolPlan]):
            """Plans which tool to use based on query."""
            
            @override
            async def exec(self, state: ToolQuery) -> NodeResult[ToolPlan]:
                if "calculate" in state.question.lower():
                    tool = "calculator"
                    params = (("expression", state.question),)
                elif "search" in state.question.lower():
                    tool = "web_search"
                    params = (("query", state.question),)
                else:
                    tool = "none"
                    params = ()
                
                plan = ToolPlan(query=state, selected_tool=tool, parameters=params)
                outcome = "tool_selected" if tool != "none" else "no_tool_needed"
                return NodeResult(plan, outcome=outcome)
        
        # Node: ToolPlan → ToolResult
        @dc(frozen=True)
        class ExecutorNode(Node[ToolPlan, ToolResult]):
            """Executes the planned tool."""
            
            @override
            async def exec(self, state: ToolPlan) -> NodeResult[ToolResult]:
                # Simulate tool execution
                if state.selected_tool == "calculator":
                    output = "Result: 42"
                    success = True
                elif state.selected_tool == "web_search":
                    output = "Found 10 relevant results"
                    success = True
                else:
                    output = "No tool executed"
                    success = False
                
                result = ToolResult(plan=state, output=output, success=success)
                outcome = "execution_success" if success else "execution_failed"
                return NodeResult(result, outcome=outcome)
        
        # Test the transformation chain
        query = ToolQuery(question="Calculate 6 * 7")
        
        planner = PlannerNode()
        plan_result = await planner(query)
        assert isinstance(plan_result.state, ToolPlan)
        assert plan_result.state.selected_tool == "calculator"
        
        executor = ExecutorNode()
        exec_result = await executor(plan_result.state)
        assert isinstance(exec_result.state, ToolResult)
        assert exec_result.state.success is True
        assert exec_result.state.plan.query == query  # Original preserved through chain