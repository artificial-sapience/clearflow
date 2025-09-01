"""Test Flow orchestration features of ClearFlow.

This module tests the Flow class functionality including linear flows,
branching, single termination enforcement, and flow composition.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import TypedDict, override

from clearflow import Node, NodeResult, flow
from tests.conftest import ValidationState


class ChatState(TypedDict, total=False):
    """State for chat routing tests."""

    query: str
    intent: str
    agent: str
    response_type: str
    formatted: bool


class DocState(TypedDict):
    """State for document processing tests."""

    source: str
    loaded: str
    doc_count: str
    embedded: str
    embedding_dim: str
    stored: str


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
            """Tokenizes text for embedding generation."""

            name: str = "tokenizer"

            @override
            async def exec(self, state: RawText) -> NodeResult[TokenizedText]:
                tokens = tuple(state.content.split())
                tokenized = TokenizedText(raw=state, tokens=tokens)
                return NodeResult(tokenized, outcome="tokenized")

        @dc(frozen=True)
        class IndexerNode(Node[TokenizedText, IndexedDocument]):
            """Creates embeddings and indexes document."""

            name: str = "indexer"

            @override
            async def exec(self, state: TokenizedText) -> NodeResult[IndexedDocument]:
                indexed = IndexedDocument(
                    tokenized=state, token_count=len(state.tokens)
                )
                return NodeResult(indexed, outcome="indexed")

        # Build the flow using the new builder API
        tokenizer = TokenizerNode()
        indexer = IndexerNode()

        # Create a RAG indexing pipeline
        indexing_flow = (
            flow("RAGIndexer", tokenizer)
            .route(tokenizer, "tokenized", indexer)
            .end(indexer, "indexed")
        )

        # Execute the flow
        initial = RawText(content="Natural language processing", source="test.txt")
        result = await indexing_flow(initial)

        assert result.outcome == "indexed"
        assert isinstance(result.state, IndexedDocument)
        assert result.state.token_count == 3
        assert result.state.indexed is True
        assert result.state.tokenized.raw == initial  # Original preserved

    @staticmethod
    async def test_branching_flow() -> None:
        """Test AI chat routing flow with conditional branching."""

        @dc(frozen=True)
        class IntentClassifier(Node[ChatState]):
            """Classifies user intent for appropriate AI response."""

            name: str = "classifier"

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                query = state.get("query", "")

                # Classify intent (simulating LLM classification)
                if "code" in str(query).lower() or "bug" in str(query).lower():
                    intent = "technical"
                elif "?" in str(query):
                    intent = "question"
                else:
                    intent = "general"

                new_state: ChatState = {**state, "intent": intent}
                return NodeResult(new_state, outcome=intent)

        @dc(frozen=True)
        class TechnicalAgent(Node[ChatState]):
            """Handles technical queries with code examples."""

            name: str = "technical_agent"

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                new_state: ChatState = {
                    **state,
                    "agent": "technical",
                    "response_type": "code_example",
                }
                return NodeResult(new_state, outcome="responded")

        @dc(frozen=True)
        class QAAgent(Node[ChatState]):
            """Handles Q&A with retrieval augmented generation."""

            name: str = "qa_agent"

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                new_state: ChatState = {
                    **state,
                    "agent": "qa",
                    "response_type": "retrieved_answer",
                }
                return NodeResult(new_state, outcome="responded")

        @dc(frozen=True)
        class GeneralAgent(Node[ChatState]):
            """Handles general conversation."""

            name: str = "general_agent"

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                new_state: ChatState = {
                    **state,
                    "agent": "general",
                    "response_type": "chat",
                }
                return NodeResult(new_state, outcome="responded")

        @dc(frozen=True)
        class ResponseFormatter(Node[ChatState]):
            """Formats final response for user."""

            name: str = "formatter"

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                new_state: ChatState = {**state, "formatted": True}
                return NodeResult(new_state, outcome="complete")

        # Build AI chat routing flow using new API
        classifier = IntentClassifier()
        technical = TechnicalAgent()
        qa = QAAgent()
        general = GeneralAgent()
        formatter = ResponseFormatter()

        chat_flow = (
            flow("ChatRouter", classifier)
            .route(classifier, "technical", technical)
            .route(classifier, "question", qa)
            .route(classifier, "general", general)
            .route(
                technical, "responded", formatter
            )  # All agents converge to formatter
            .route(qa, "responded", formatter)
            .route(general, "responded", formatter)
            .end(formatter, "complete")  # Single termination with end()
        )

        # Test technical query path
        tech_input: ChatState = {"query": "How do I fix this bug in my code?"}
        technical_result = await chat_flow(tech_input)
        assert technical_result.state.get("intent") == "technical"
        assert technical_result.state.get("agent") == "technical"
        assert technical_result.state.get("response_type") == "code_example"
        assert technical_result.state.get("formatted") is True
        assert technical_result.outcome == "complete"

        # Test question path
        question_input: ChatState = {"query": "What is RAG?"}
        question_result = await chat_flow(question_input)
        assert question_result.state.get("intent") == "question"
        assert question_result.state.get("agent") == "qa"
        assert question_result.state.get("response_type") == "retrieved_answer"
        assert question_result.state.get("formatted") is True
        assert question_result.outcome == "complete"

        # Test general conversation path
        general_input: ChatState = {"query": "Tell me about the weather"}
        general_result = await chat_flow(general_input)
        assert general_result.state.get("intent") == "general"
        assert general_result.state.get("agent") == "general"
        assert general_result.state.get("response_type") == "chat"
        assert general_result.state.get("formatted") is True
        assert general_result.outcome == "complete"

    @staticmethod
    async def test_single_termination_enforcement() -> None:
        """Test that flows must have exactly one termination point."""

        @dc(frozen=True)
        class DataValidator(Node[ValidationState]):
            """Validates incoming data for processing."""

            name: str = "validator"

            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="valid")

        @dc(frozen=True)
        class DataProcessor(Node[ValidationState]):
            """Processes validated data."""

            name: str = "processor"

            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="processed")

        validator = DataValidator()
        processor = DataProcessor()

        # This works - single termination point
        valid_flow = (
            flow("ValidationPipeline", validator)
            .route(validator, "valid", processor)
            .end(processor, "processed")
        )

        # Test that it runs successfully
        result = await valid_flow(ValidationState(input_text="test data"))
        assert result.outcome == "processed"

    @staticmethod
    async def test_nested_flows() -> None:
        """Test that flows can be composed as nodes in AI pipelines."""

        @dc(frozen=True)
        class DocumentLoader(Node[DocState]):
            """Loads documents for processing."""

            name: str = "loader"

            @override
            async def exec(self, state: DocState) -> NodeResult[DocState]:
                new_state: DocState = {**state, "loaded": "true", "doc_count": "5"}
                return NodeResult(new_state, outcome="loaded")

        @dc(frozen=True)
        class Embedder(Node[DocState]):
            """Creates embeddings from loaded documents."""

            name: str = "embedder"

            @override
            async def exec(self, state: DocState) -> NodeResult[DocState]:
                new_state: DocState = {
                    **state,
                    "embedded": "true",
                    "embedding_dim": "768",
                }
                return NodeResult(new_state, outcome="embedded")

        @dc(frozen=True)
        class VectorStore(Node[DocState]):
            """Stores embeddings in vector database."""

            name: str = "vector_store"

            @override
            async def exec(self, state: DocState) -> NodeResult[DocState]:
                new_state: DocState = {**state, "stored": "true"}
                return NodeResult(new_state, outcome="indexed")

        # Create inner flow for document processing
        loader = DocumentLoader()
        embedder = Embedder()

        doc_processing_flow = (
            flow("DocumentProcessor", loader)
            .route(loader, "loaded", embedder)
            .end(embedder, "embedded")
        )

        # Use inner flow as a node in larger indexing pipeline
        vector_store = VectorStore()

        indexing_pipeline = (
            flow("IndexingPipeline", doc_processing_flow)
            .route(doc_processing_flow, "embedded", vector_store)
            .end(vector_store, "indexed")
        )

        doc_input: DocState = {
            "source": "knowledge_base",
            "loaded": "",
            "doc_count": "",
            "embedded": "",
            "embedding_dim": "",
            "stored": "",
        }
        result = await indexing_pipeline(doc_input)

        assert result.state["loaded"] == "true"
        assert result.state["embedded"] == "true"
        assert result.state["stored"] == "true"
        assert result.state["doc_count"] == "5"
        assert result.state["embedding_dim"] == "768"
        assert result.outcome == "indexed"
