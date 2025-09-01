"""Test immutability features of ClearFlow.

This module tests that ClearFlow properly handles immutable state,
demonstrating mission-critical AI orchestration patterns with deep immutability.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Node, NodeResult
from tests.conftest import (
    AgentState, Document, EmbeddedDocument, Message
)


@dc(frozen=True)
class EmbeddingNode(Node[Document, EmbeddedDocument]):
    """Transforms document to embedded document (type transformation example)."""
    
    @override
    async def exec(self, state: Document) -> NodeResult[EmbeddedDocument]:
        # Simulate embedding generation (in practice, would call embedding API)
        mock_embedding = tuple(hash(state.content) % 100 / 100.0 for _ in range(3))
        embedded = EmbeddedDocument(document=state, embedding=mock_embedding)
        return NodeResult(embedded, outcome="embedded")


class TestImmutableAIOrchestration:
    """Test mission-critical AI orchestration with deep immutability."""

    @staticmethod
    async def test_rag_document_embedding() -> None:
        """Test document embedding for RAG pipeline with type transformation."""

        # This demonstrates Node[TIn, TOut] where TIn != TOut
        node = EmbeddingNode()
        
        # Create immutable document
        doc = Document(
            content="Functional programming emphasizes immutability.",
            source="fp_guide.md",
            metadata=(("author", "Rich Hickey"), ("year", "2020"))
        )
        
        result = await node(doc)
        
        # Verify type transformation worked
        assert isinstance(result.state, EmbeddedDocument)
        assert result.state.document == doc
        assert len(result.state.embedding) == 3
        assert all(0 <= x <= 1 for x in result.state.embedding)
        assert result.outcome == "embedded"
        
        # Original document remains unchanged (immutable)
        assert doc.content == "Functional programming emphasizes immutability."

    @staticmethod
    async def test_agent_message_handling() -> None:
        """Test multi-agent message handling with immutable state."""

        @dc(frozen=True)
        class AgentResponseNode(Node[AgentState]):
            """Pure function node for agent responses."""
            
            @override
            async def exec(self, state: AgentState) -> NodeResult[AgentState]:
                # Pure transformation: analyze last message and respond
                last_msg = state.messages[-1] if state.messages else None
                
                if last_msg and "help" in last_msg.content.lower():
                    response = Message(role="assistant", content="I'll help you with that.")
                    outcome = "help_requested"
                else:
                    response = Message(role="assistant", content="Please clarify your request.")
                    outcome = "needs_clarification"
                
                # Create new immutable state
                new_state = AgentState(
                    messages=state.messages + (response,),
                    context=state.context,
                    temperature=state.temperature
                )
                return NodeResult(new_state, outcome=outcome)

        node = AgentResponseNode()
        initial = AgentState(
            messages=(Message(role="user", content="I need help with Python"),),
            context="programming_assistance"
        )
        result = await node(initial)

        assert len(result.state.messages) == 2
        assert result.state.messages[-1].role == "assistant"
        assert "help" in result.state.messages[-1].content.lower()
        assert result.outcome == "help_requested"
        
        # Verify deep immutability
        assert len(initial.messages) == 1
        assert initial.messages[0].content == "I need help with Python"

    @staticmethod
    async def test_dataclass_state() -> None:
        """Test with frozen dataclasses for immutability."""

        @dc(frozen=True)
        class WorkflowState:
            documents: tuple[str, ...]
            processed: bool = False

        class DataclassNode(Node[WorkflowState]):
            @override
            async def exec(self, state: WorkflowState) -> NodeResult[WorkflowState]:
                # Create new instance (immutable)
                new_state = WorkflowState(documents=state.documents, processed=True)
                return NodeResult(new_state, outcome="processed")

        node = DataclassNode()
        initial = WorkflowState(documents=("doc1", "doc2"))
        result = await node(initial)

        assert result.state.processed is True
        assert initial.processed is False  # Original unchanged

    @staticmethod
    async def test_primitive_state() -> None:
        """Test with primitive types as state."""

        class CounterNode(Node[int]):
            @override
            async def exec(self, state: int) -> NodeResult[int]:
                return NodeResult(state + 1, outcome="incremented")

        node = CounterNode()
        result = await node(42)

        assert result.state == 43
        assert result.outcome == "incremented"