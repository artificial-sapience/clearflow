"""Test Flow orchestration features of ClearFlow.

This module tests the Flow class functionality including linear flows,
branching, single termination enforcement, and flow composition.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Flow, Node, NodeResult
from tests.conftest import ValidationState


class TestFlow:
    """Test the Flow orchestration."""

    @staticmethod
    async def test_linear_flow() -> None:
        """Test a linear RAG indexing flow with type transformations."""

        @dc(frozen=True)
        class RawText:
            """Raw text to be processed."""
            content: str
            source: str

        @dc(frozen=True) 
        class TokenizedText:
            """Text split into tokens."""
            raw: RawText
            tokens: tuple[str, ...]

        @dc(frozen=True)
        class IndexedDocument:
            """Final indexed document."""
            tokenized: TokenizedText
            token_count: int
            indexed: bool = True

        @dc(frozen=True)
        class TokenizerNode(Node[RawText, TokenizedText]):
            """Transforms raw text to tokenized text."""
            
            @override
            async def exec(self, state: RawText) -> NodeResult[TokenizedText]:
                tokens = tuple(state.content.split())
                tokenized = TokenizedText(raw=state, tokens=tokens)
                return NodeResult(tokenized, outcome="tokenized")

        @dc(frozen=True)
        class IndexerNode(Node[TokenizedText, IndexedDocument]):
            """Transforms tokenized text to indexed document."""
            
            @override
            async def exec(self, state: TokenizedText) -> NodeResult[IndexedDocument]:
                indexed = IndexedDocument(
                    tokenized=state,
                    token_count=len(state.tokens)
                )
                return NodeResult(indexed, outcome="indexed")

        # Build the flow - note the type transformation chain!
        tokenizer = TokenizerNode()
        indexer = IndexerNode()

        # This won't work directly with Flow because of type mismatch
        # We need a wrapper flow that handles the full transformation
        @dc(frozen=True)
        class IndexingFlow(Node[RawText, IndexedDocument]):
            """Complete indexing pipeline."""
            
            @override
            async def exec(self, state: RawText) -> NodeResult[IndexedDocument]:
                # First transformation: RawText -> TokenizedText
                tokenized_result = await tokenizer(state)
                
                # Second transformation: TokenizedText -> IndexedDocument  
                indexed_result = await indexer(tokenized_result.state)
                
                return indexed_result

        # Execute the flow
        flow = IndexingFlow()
        initial = RawText(content="Natural language processing", source="test.txt")
        result = await flow(initial)

        assert result.outcome == "indexed"
        assert isinstance(result.state, IndexedDocument)
        assert result.state.token_count == 3
        assert result.state.indexed is True
        assert result.state.tokenized.raw == initial  # Original preserved

    @staticmethod
    async def test_branching_flow() -> None:
        """Test flow with conditional branching based on outcomes."""

        @dc(frozen=True)
        class ClassifierNode(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                content = state.get("content", "")

                if "urgent" in str(content).lower():
                    outcome = "urgent"
                elif "question" in str(content).lower():
                    outcome = "question"
                else:
                    outcome = "normal"

                new_state = {**state, "classification": outcome}
                return NodeResult(new_state, outcome=outcome)

        @dc(frozen=True)
        class UrgentHandler(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                new_state = {**state, "priority": "high", "handled_by": "urgent_team"}
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class QuestionHandler(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                new_state = {
                    **state,
                    "priority": "medium",
                    "handled_by": "support_team",
                }
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class NormalHandler(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                new_state = {**state, "priority": "low", "handled_by": "bot"}
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class CompleteHandler(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                new_state = {**state, "status": "completed"}
                return NodeResult(new_state, outcome="done")

        # Build branching flow with single termination
        classifier = ClassifierNode()
        urgent = UrgentHandler()
        question = QuestionHandler()
        normal = NormalHandler()
        complete = CompleteHandler()

        flow = (
            Flow[dict[str, object]]("TicketRouter")
            .start_with(classifier)
            .route(classifier, "urgent", urgent)
            .route(classifier, "question", question)
            .route(classifier, "normal", normal)
            .route(urgent, "handled", complete)  # Converge to complete
            .route(question, "handled", complete)  # Converge to complete
            .route(normal, "handled", complete)  # Converge to complete
            .route(complete, "done", None)  # Single termination
            .build()
        )

        # Test urgent path
        urgent_result = await flow({"content": "URGENT: Server is down!"})
        assert urgent_result.state["priority"] == "high"
        assert urgent_result.state["handled_by"] == "urgent_team"
        assert urgent_result.state["status"] == "completed"
        assert urgent_result.outcome == "done"

        # Test question path
        question_result = await flow({"content": "Question about billing"})
        assert question_result.state["priority"] == "medium"
        assert question_result.state["handled_by"] == "support_team"
        assert question_result.state["status"] == "completed"
        assert question_result.outcome == "done"

        # Test normal path
        normal_result = await flow({"content": "Monthly newsletter"})
        assert normal_result.state["priority"] == "low"
        assert normal_result.state["handled_by"] == "bot"
        assert normal_result.state["status"] == "completed"
        assert normal_result.outcome == "done"

    @staticmethod
    async def test_single_termination_enforcement() -> None:
        """Test that flows must have exactly one termination point."""
        
        @dc(frozen=True)
        class TestNode(Node[ValidationState]):
            """Simple node for testing flow construction."""
            
            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="done")
        
        node_a = TestNode()

        # This should fail - multiple termination points
        with pytest.raises(ValueError, match="multiple termination points"):
            (
                Flow[ValidationState]("InvalidFlow")
                .start_with(node_a)
                .route(node_a, "done", None)  # First termination
                .route(node_a, "error", None)  # Second termination - should fail
                .build()
            )

    @staticmethod
    async def test_nested_flows() -> None:
        """Test that flows can be composed as nodes."""

        @dc(frozen=True)
        class StartNode(Node[dict[str, str]]):
            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                new_state = {**state, "started": "true"}
                return NodeResult(new_state, outcome="ready")

        @dc(frozen=True)
        class EndNode(Node[dict[str, str]]):
            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                new_state = {**state, "completed": "true"}
                return NodeResult(new_state, outcome="done")

        # Create inner flow
        start = StartNode()
        end = EndNode()

        inner_flow = (
            Flow[dict[str, str]]("InnerFlow")
            .start_with(start)
            .route(start, "ready", end)
            .route(end, "done", None)
            .build()
        )

        # Use inner flow as a node in outer flow
        outer_flow = (
            Flow[dict[str, str]]("OuterFlow")
            .start_with(inner_flow)
            .route(inner_flow, "done", None)
            .build()
        )

        result = await outer_flow({"initial": "value"})

        assert result.state["started"] == "true"
        assert result.state["completed"] == "true"
        assert result.outcome == "done"