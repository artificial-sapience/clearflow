"""Test Suite for ClearFlow - The Purely Functional LLM Framework.

This test suite validates the core principles of ClearFlow:
- Immutability of state
- Pure functions (no side effects)
- Deterministic behavior
- Composability of flows

Testing approach:
- Property-based testing: verify invariants like immutability
- Example-based testing: verify specific behaviors
- Edge case testing: handle errors gracefully
- Composition testing: verify that functions compose correctly

Each test documents the functional programming principle it validates.

Copyright (c) 2025 ClearFlow Contributors
"""

import random
from dataclasses import dataclass as dc
from typing import Any, cast, override

import pytest

from clearflow import (
    Flow,
    Node,
    NodeResult,
    State,
)

# Type aliases for domain-specific test scenarios

ChatState = dict[str, Any]  # For chat agent tests
DocumentState = dict[str, Any]  # For document processing tests
ToolState = dict[str, Any]  # For tool execution tests

# More specific types for certain test cases
DocumentListState = dict[str, list[str] | str]
MessageListState = dict[str, list[str] | int]


# Simple test node for cases where we need a concrete Node
class SimpleNode[T](Node[T]):
    """A simple node that just passes through state with a configurable outcome."""

    outcome: str = "done"

    @override
    async def exec(self, state: State[T]) -> NodeResult[T]:
        return NodeResult(state, outcome=self.outcome)


# ===== STATE TESTS =====


class TestState:
    """Test the immutable state container."""

    @staticmethod
    async def test_immutability() -> None:
        """Core principle: State modifications create new instances."""
        original_data: ChatState = {"messages": [], "context": "initial"}
        state1 = State(original_data)

        # Modification creates new state using transform
        state2 = state1.transform(
            lambda d: {**d, "messages": ["Hello"], "context": "greeting"}
        )

        # Original state unchanged
        assert state1.data["messages"] == []
        assert state2.data["messages"] == ["Hello"]
        assert state1.data["context"] == "initial"
        assert state2.data["context"] == "greeting"
        assert state1 is not state2

        # Original data dict also unchanged (shallow copy)
        assert original_data["messages"] == []

    @staticmethod
    async def test_transform() -> None:
        """Test functional transformation of state data."""
        state1 = State[DocumentState]({
            "documents": ["doc1.txt", "doc2.txt", "doc3.txt"],
            "processed": [],
        })

        # Transform with pure function
        def process_documents(data: DocumentState) -> DocumentState:
            docs = data.get("documents", [])
            if isinstance(docs, list):
                # Process only string documents
                processed: list[str] = []
                for doc in docs:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(doc, str):
                        processed.append(f"processed_{doc}")
                return {**data, "processed": processed, "status": "completed"}
            return data

        state2 = state1.transform(process_documents)

        # Verify transformation
        assert state1.data["documents"] == ["doc1.txt", "doc2.txt", "doc3.txt"]
        assert state2.data["processed"] == [
            "processed_doc1.txt",
            "processed_doc2.txt",
            "processed_doc3.txt",
        ]
        assert "status" in state2.data
        assert cast("str", state2.data["status"]) == "completed"

    @staticmethod
    async def test_generic_types() -> None:
        """Test State works with various generic types."""
        # Prompt state
        prompt_state: State[str] = State("Summarize this document")
        enhanced_state = prompt_state.transform(
            lambda p: f"System: You are a helpful assistant.\nUser: {p}"
        )
        assert "System:" in enhanced_state.data

        # Token list state
        tokens_state: State[list[str]] = State(["Hello", "world", "!"])
        encoded_state = tokens_state.transform(
            lambda tokens: [f"<{t}>" for t in tokens]
        )
        assert encoded_state.data == ["<Hello>", "<world>", "<!>"]

        # Custom agent type state
        @dc
        class Agent:
            name: str
            capabilities: list[str]
            model: str

        agent_state: State[Agent] = State(
            Agent("Assistant", ["chat", "search"], "gpt-4")
        )
        upgraded_state = agent_state.transform(
            lambda a: Agent(a.name, [*a.capabilities, "code"], "gpt-4-turbo")
        )
        assert "code" in upgraded_state.data.capabilities
        assert upgraded_state.data.model == "gpt-4-turbo"


# ===== NODE TESTS =====


class TestNode:
    """Test basic node functionality."""

    @staticmethod
    async def test_node_with_function() -> None:
        """Test creating a node with a function."""

        class PromptAnalyzer(Node[ChatState]):
            """Analyzes user prompts for intent."""

            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                prompt = state.data.get("prompt", "")
                intent = "question" if "?" in str(prompt) else "statement"
                new_state = state.transform(
                    lambda d: {**d, "intent": intent, "analyzed": True}
                )
                return NodeResult(new_state, outcome="analyzed")

        node = PromptAnalyzer(name="prompt_analyzer")
        initial = State({"prompt": "What is the weather today?"})
        result = await node(initial)

        assert result.state.data["intent"] == "question"
        assert result.state.data["analyzed"] is True
        assert result.outcome == "analyzed"
        assert node.name == "prompt_analyzer"

    @staticmethod
    async def test_node_subclass() -> None:
        """Test creating a node by subclassing."""

        class DocumentSummarizer(Node[DocumentState]):
            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                content = state.data.get("content", "")
                # Simulate summarization
                summary = (
                    f"Summary of {len(str(content))} characters: {str(content)[:50]}..."
                )
                new_state = state.transform(
                    lambda d: {**d, "summary": summary, "summarized": True}
                )
                return NodeResult(new_state, outcome="summarized")

        node = DocumentSummarizer()  # Name auto-set from class
        content = (
            "This is a long document about artificial intelligence "
            "and machine learning..."
        )
        initial = State({"content": content})
        result = await node(initial)

        assert "Summary of" in result.state.data["summary"]
        assert result.state.data["summarized"] is True
        assert result.outcome == "summarized"
        assert node.name == "DocumentSummarizer"

    @staticmethod
    async def test_node_lifecycle() -> None:
        """Test node lifecycle phases (prep, exec, post)."""

        class LLMAPICall(Node[ChatState]):
            @override
            async def prep(self, state: State[ChatState]) -> State[ChatState]:
                # Prepare: Add system prompt
                return state.transform(
                    lambda d: {**d, "system_prompt": "You are a helpful assistant"}
                )

            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                # Execute: Simulate API call
                state = state.transform(
                    lambda d: {
                        **d,
                        "response": "I can help with that!",
                        "tokens_used": 15,
                    }
                )
                return NodeResult(state, outcome="generated")

            @override
            async def post(
                self, result: NodeResult[ChatState]
            ) -> NodeResult[ChatState]:
                # Post: Log usage
                tokens = result.state.data.get("tokens_used", 0)
                new_state = result.state.transform(
                    lambda d: {**d, "logged": True, "total_cost": tokens * 0.0001}
                )
                return NodeResult(new_state, result.outcome)

        node = LLMAPICall()  # Name auto-set from class
        result = await node(State({"user_prompt": "Help me write code"}))

        assert result.state.data.get("system_prompt") == "You are a helpful assistant"
        assert result.state.data.get("response") == "I can help with that!"
        assert result.state.data.get("logged") is True
        assert result.state.data.get("total_cost") == 0.0015

    @staticmethod
    async def test_node_name_from_class() -> None:
        """Test node gets name from class when no name provided."""

        class ExtractEntities(Node[DocumentState]):
            """Extract entities from document."""

            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                # Extract entities from document
                entities = ["OpenAI", "GPT-4", "machine learning"]
                new_state = state.transform(lambda d: {**d, "entities": entities})
                return NodeResult(new_state, outcome="extracted")

        # Create node without explicit name - should use class name
        node = ExtractEntities()
        assert node.name == "ExtractEntities"

        # With explicit name, use that instead
        class EntityExtractor(Node[DocumentState]):
            """Extract entities with custom name."""

            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                entities = ["OpenAI", "GPT-4", "machine learning"]
                new_state = state.transform(lambda d: {**d, "entities": entities})
                return NodeResult(new_state, outcome="extracted")

        node_with_name = EntityExtractor(name="entity_extractor")
        assert node_with_name.name == "entity_extractor"

        # Test empty name gets class name
        empty_name_node = ExtractEntities(name="")
        assert empty_name_node.name == "ExtractEntities"

        # Test flow name validation still works
        class NodeWithEmptyNameAfterInit(Node[DocumentState]):
            def __post_init__(self) -> None:
                """Override to force empty name."""
                object.__setattr__(self, "name", "")

            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                return NodeResult(state, outcome="done")

        # This node will have empty name even after __post_init__
        tricky_node = NodeWithEmptyNameAfterInit()
        assert not tricky_node.name  # Empty string

        # Test that route validation catches truly empty names
        class StartNode(Node[DocumentState]):
            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                return NodeResult(state, outcome="done")

        start = StartNode(name="start")
        with pytest.raises(ValueError, match="from_node must have a name"):
            (
                Flow[DocumentState]("TestFlow")
                .start_with(start)
                .route(tricky_node, "outcome", start)
                .build()
            )


# ===== FLOW BUILDER TESTS =====


class TestFlow:
    """Test the immutable flow builder."""

    @staticmethod
    async def test_builder_immutability() -> None:
        """Test that builder methods return new instances."""
        builder1 = Flow[ChatState]("ChatAssistant")
        greeting = SimpleNode[ChatState](name="greeting")
        end = SimpleNode[ChatState](name="end")
        builder2 = builder1.start_with(greeting)
        builder3 = builder2.route(greeting, "next", end)

        # Each method returns a new object (immutability)
        # builder1 and builder2 are different types, so check they're distinct
        assert id(builder1) != id(builder2)
        assert builder2 is not builder3  # route returns new instance

        # Each stage has appropriate methods
        assert hasattr(builder1, "start_with")
        assert hasattr(builder2, "route")
        assert hasattr(builder3, "build")

    @staticmethod
    async def test_simple_flow() -> None:
        """Test building a simple agent flow."""

        async def analyze_query(state: State[ChatState]) -> NodeResult[ChatState]:
            query = state.data.get("query", "")
            # Determine if we need to search or can answer directly
            needs_search = (
                "latest" in str(query).lower() or "current" in str(query).lower()
            )
            new_state = state.transform(
                lambda d: {**d, "needs_search": needs_search, "query_type": "factual"}
            )
            return NodeResult(
                new_state, outcome="search" if needs_search else "generate"
            )

        async def search_knowledge(state: State[ChatState]) -> NodeResult[ChatState]:
            # Simulate knowledge search
            new_state = state.transform(
                lambda d: {
                    **d,
                    "search_results": [
                        "Result 1: Latest AI developments...",
                        "Result 2: Current trends...",
                    ],
                }
            )
            return NodeResult(new_state, outcome="generate")

        async def generate_response(state: State[ChatState]) -> NodeResult[ChatState]:
            search_results = state.data.get("search_results", [])
            response = (
                "Based on current information..."
                if search_results
                else "Based on my knowledge..."
            )
            new_state = state.transform(
                lambda d: {**d, "response": response, "tokens_used": 150}
            )
            return NodeResult(new_state, outcome="completed")

        class Analyzer(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await analyze_query(state)

        class Searcher(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await search_knowledge(state)

        class Generator(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await generate_response(state)

        analyze = Analyzer(name="analyzer")
        search = Searcher(name="searcher")
        generate = Generator(name="generator")

        rag_assistant = (
            Flow[ChatState]("RAG_Assistant")
            .start_with(analyze)
            .route(analyze, "search", search)
            .route(analyze, "generate", generate)
            .route(search, "generate", generate)
            .route(generate, "completed", None)  # Explicit termination
            .build()
        )

        # Test direct answer path
        result1 = await rag_assistant(State({"query": "What is machine learning?"}))
        assert result1.state.data.get("needs_search") is False
        assert "Based on my knowledge" in result1.state.data.get("response", "")

        # Test search path
        result2 = await rag_assistant(
            State({"query": "What are the latest AI developments?"})
        )
        assert result2.state.data.get("needs_search") is True
        assert "search_results" in result2.state.data
        assert "Based on current information" in result2.state.data.get("response", "")

    @staticmethod
    async def test_branching_flow() -> None:
        """Test agent flow with intent-based orchestration."""

        class IntentClassifier(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                message = state.data.get("message", "")
                message_lower = str(message).lower()

                # Classify intent based on keywords
                if any(
                    word in message_lower
                    for word in ["code", "program", "function", "debug"]
                ):
                    intent = "coding"
                elif any(
                    word in message_lower for word in ["summarize", "tldr", "summary"]
                ):
                    intent = "summarization"
                elif any(
                    word in message_lower
                    for word in ["translate", "translation", "language"]
                ):
                    intent = "translation"
                else:
                    intent = "general_chat"

                new_state = state.transform(lambda d: {**d, "intent": intent})
                return NodeResult(new_state, outcome=intent)

        class CodingAssistant(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                new_state = state.transform(
                    lambda d: {
                        **d,
                        "response": (
                            "I'll help you with coding. "
                            "Let me analyze your requirements..."
                        ),
                        "mode": "code_generation",
                        "capabilities": [
                            "syntax_highlighting",
                            "error_detection",
                            "refactoring",
                        ],
                    }
                )
                return NodeResult(new_state, outcome="response_ready")

        class SummarizationAgent(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                new_state = state.transform(
                    lambda d: {
                        **d,
                        "response": "I'll create a concise summary for you...",
                        "mode": "summarization",
                        "max_summary_length": 200,
                    }
                )
                return NodeResult(new_state, outcome="response_ready")

        class TranslationAgent(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                new_state = state.transform(
                    lambda d: {
                        **d,
                        "response": "I can translate between multiple languages...",
                        "mode": "translation",
                        "supported_languages": ["en", "es", "fr", "de", "ja", "zh"],
                    }
                )
                return NodeResult(new_state, outcome="response_ready")

        class GeneralChatAgent(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                new_state = state.transform(
                    lambda d: {
                        **d,
                        "response": (
                            "I'm here to help with general questions "
                            "and conversations..."
                        ),
                        "mode": "chat",
                    }
                )
                return NodeResult(new_state, outcome="response_ready")

        class ResponseDelivery(Node[ChatState]):
            """Delivers response and checks if user needs more help."""

            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                # In a real system, this would format and deliver the response
                # For testing, we just mark it as delivered
                new_state = state.transform(
                    lambda d: {**d, "delivered": True, "session_complete": True}
                )
                return NodeResult(new_state, outcome="session_ended")

        classifier = IntentClassifier(name="IntentClassifier")
        coding = CodingAssistant(name="CodingAssistant")
        summarize = SummarizationAgent(name="SummarizationAgent")
        translate = TranslationAgent(name="TranslationAgent")
        general = GeneralChatAgent(name="GeneralChatAgent")
        delivery = ResponseDelivery(name="ResponseDelivery")

        multi_agent_system = (
            Flow[ChatState]("MultiAgentAssistant")
            .start_with(classifier)
            .route(classifier, "coding", coding)
            .route(classifier, "summarization", summarize)
            .route(classifier, "translation", translate)
            .route(classifier, "general_chat", general)
            # All agents converge to response delivery
            .route(coding, "response_ready", delivery)
            .route(summarize, "response_ready", delivery)
            .route(translate, "response_ready", delivery)
            .route(general, "response_ready", delivery)
            # Single termination point
            .route(delivery, "session_ended", None)
            .build()
        )

        # Test coding intent
        coding_result = await multi_agent_system(
            State({"message": "Help me debug this Python function"})
        )
        assert coding_result.state.data.get("intent") == "coding"
        assert coding_result.state.data.get("mode") == "code_generation"
        assert "syntax_highlighting" in coding_result.state.data.get("capabilities", [])
        assert coding_result.state.data.get("delivered") is True
        assert coding_result.outcome == "session_ended"

        # Test summarization intent
        summary_result = await multi_agent_system(
            State({"message": "Can you summarize this article?"})
        )
        assert summary_result.state.data.get("intent") == "summarization"
        assert summary_result.state.data.get("max_summary_length") == 200
        assert summary_result.state.data.get("delivered") is True

        # Test translation intent
        translate_result = await multi_agent_system(
            State({"message": "Translate this to Spanish"})
        )
        assert translate_result.state.data.get("intent") == "translation"
        assert "es" in translate_result.state.data.get("supported_languages", [])
        assert translate_result.state.data.get("delivered") is True

        # Test general intent
        general_result = await multi_agent_system(
            State({"message": "What's your opinion on AI?"})
        )
        assert general_result.state.data.get("intent") == "general_chat"
        assert general_result.state.data.get("mode") == "chat"
        assert general_result.state.data.get("delivered") is True

    @staticmethod
    async def test_builder_validation() -> None:
        """Test builder validation."""
        # Cannot create builder with empty name
        with pytest.raises(ValueError, match="Flow name must be a non-empty string"):
            Flow[ChatState]("")

        # Cannot create builder with whitespace-only name
        with pytest.raises(ValueError, match="Flow name must be a non-empty string"):
            Flow[ChatState]("   ")

        # Cannot build without start node
        with pytest.raises(AttributeError):
            Flow[ChatState]("TestFlow").build()  # type: ignore[attr-defined]

    @staticmethod
    async def test_routing_exhaustiveness() -> None:
        """Test orchestration exhaustiveness validation and single termination."""

        # Test 1: Multiple termination points should fail
        class ChoiceNode(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                choice = state.data.get("choice", "A")
                return NodeResult(state, outcome=str(choice))

        choice = ChoiceNode(name="choice")

        # Should fail with multiple None routes
        with pytest.raises(ValueError, match="multiple termination points"):
            (
                Flow[ChatState]("MultiTerminal")
                .start_with(choice)
                .route(choice, "A", None)
                .route(choice, "B", None)
                .build()
            )

        # Test 2: Single termination should work
        cleanup = ChoiceNode(name="cleanup")
        single_terminal = (
            Flow[ChatState]("SingleTerminal")
            .start_with(choice)
            .route(choice, "A", cleanup)
            .route(choice, "B", cleanup)
            .route(cleanup, "A", None)  # Single termination
            .build()
        )
        result = await single_terminal(State({"choice": "A"}))
        assert result.outcome == "A"

        # Test 3: Nested flow without termination (returns outcomes to parent)
        nested_flow = (
            Flow[ChatState]("NestedFlow")
            .start_with(choice)
            # No routes - outcomes bubble up
            .build()
        )

        # Use nested flow in parent
        parent_flow = (
            Flow[ChatState]("ParentFlow")
            .start_with(nested_flow)
            .route(nested_flow, "A", None)  # Parent handles termination
            .build()
        )

        result = await parent_flow(State({"choice": "A"}))
        assert result.outcome == "A"


# ===== FLOW COMPOSITION TESTS =====


class TestFlowComposition:
    """Test composing flows as nodes."""

    @staticmethod
    async def test_flow_is_node() -> None:
        """Test that Flow is a Node and can be used as such."""

        # Build inner flow for document processing
        async def validate_document(
            state: State[DocumentState],
        ) -> NodeResult[DocumentState]:
            doc = state.data.get("document", "")
            valid = len(str(doc)) > 0
            new_state = state.transform(lambda d: {**d, "validated": valid})
            return NodeResult(new_state, outcome="validated")

        class Validator(Node[DocumentState]):
            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                return await validate_document(state)

        validator_node = Validator(name="Validator")
        validation_flow = (
            Flow[DocumentState]("DocumentValidator").start_with(validator_node).build()
        )

        # Verify flow is a Node (Flow returns Node)
        assert isinstance(validation_flow, Node)
        # The name might not be "_Flow" since it's private
        assert validation_flow.name is not None

    @staticmethod
    async def test_nested_flows() -> None:
        """Test flows composed of other flows."""

        # Sub-flow 1: Authentication for API access
        class APIKeyValidator(Node[ToolState]):
            @override
            async def exec(self, state: State[ToolState]) -> NodeResult[ToolState]:
                api_key = state.data.get("api_key", "")
                valid = len(str(api_key)) > 10  # Simple validation
                new_state = state.transform(lambda d: {**d, "auth_valid": valid})
                return NodeResult(new_state, outcome="validated")

        class RateLimitChecker(Node[ToolState]):
            @override
            async def exec(self, state: State[ToolState]) -> NodeResult[ToolState]:
                if state.data.get("auth_valid"):
                    # Check rate limits
                    new_state = state.transform(
                        lambda d: {
                            **d,
                            "rate_limit_ok": True,
                            "requests_remaining": 100,
                        }
                    )
                    return NodeResult(new_state, outcome="authorized")
                new_state = state.transform(
                    lambda d: {**d, "rate_limit_ok": False, "error": "Invalid API key"}
                )
                return NodeResult(new_state, outcome="unauthorized")

        validator = APIKeyValidator(name="APIKeyValidator")
        rate_limiter = RateLimitChecker(name="RateLimitChecker")
        auth_flow = (
            Flow[ToolState]("AuthenticationFlow")
            .start_with(validator)
            .route(validator, "validated", rate_limiter)
            # No terminal routes - this is a sub-flow that returns outcomes to parent
            .build()
        )

        # Sub-flow 2: Tool execution
        class ToolExecutor(Node[ToolState]):
            @override
            async def exec(self, state: State[ToolState]) -> NodeResult[ToolState]:
                if state.data.get("rate_limit_ok"):
                    tool_name = state.data.get("tool_name", "calculator")
                    # Simulate tool execution
                    new_state = state.transform(
                        lambda d: {
                            **d,
                            "tool_result": f"Executed {tool_name} successfully",
                            "execution_time_ms": 150,
                        }
                    )
                    return NodeResult(new_state, outcome="executed")
                new_state = state.transform(
                    lambda d: {**d, "tool_result": "Execution blocked: unauthorized"}
                )
                return NodeResult(new_state, outcome="blocked")

        executor = ToolExecutor(name="ToolExecutor")
        execution_flow = (
            Flow[ToolState]("ExecutionFlow")
            .start_with(executor)
            # No terminal routes - returns outcomes to parent
            .build()
        )

        # Cleanup node for single termination
        class CleanupHandler(Node[ToolState]):
            @override
            async def exec(self, state: State[ToolState]) -> NodeResult[ToolState]:
                # Log the final state for auditing
                new_state = state.transform(
                    lambda d: {**d, "completed_at": "2024-01-01T00:00:00Z"}
                )
                return NodeResult(new_state, outcome="done")

        cleanup = CleanupHandler(name="CleanupHandler")

        # Main flow composing sub-flows
        tool_orchestrator = (
            Flow[ToolState]("ToolOrchestrator")
            .start_with(auth_flow)
            .route(auth_flow, "authorized", execution_flow)
            .route(
                auth_flow, "unauthorized", execution_flow
            )  # Still route to execution for error handling
            .route(execution_flow, "executed", cleanup)
            .route(execution_flow, "blocked", cleanup)
            .route(cleanup, "done", None)  # Single termination
            .build()
        )

        # Run composed flow with valid API key
        result = await tool_orchestrator(
            State({"api_key": "sk-valid-key-12345", "tool_name": "web_search"})
        )
        assert result.state.data.get("auth_valid") is True
        assert result.state.data.get("rate_limit_ok") is True
        assert "web_search" in str(result.state.data.get("tool_result", ""))

    @staticmethod
    async def test_complex_composition() -> None:
        """Test complex multi-level agent composition."""

        # Level 1: Intent extraction for customer support
        async def analyze_customer_query(
            state: State[ChatState],
        ) -> NodeResult[ChatState]:
            query = state.data.get("customer_message", "")
            # Determine intent: refund, technical_support, or general_inquiry
            intent = "refund" if "refund" in str(query).lower() else "technical_support"
            new_state = state.transform(
                lambda d: {
                    **d,
                    "intent": intent,
                    "priority": "high" if intent == "refund" else "normal",
                }
            )
            return NodeResult(new_state, outcome="classified")

        async def generate_support_response(
            state: State[ChatState],
        ) -> NodeResult[ChatState]:
            intent = state.data.get("intent", "")
            responses = {
                "refund": (
                    "I'll help you process your refund request. "
                    "Let me gather some information..."
                ),
                "technical_support": (
                    "I'll assist you with your technical issue. "
                    "Can you describe the problem?"
                ),
                "general_inquiry": "I'm here to help! What would you like to know?",
            }
            new_state = state.transform(
                lambda d: {
                    **d,
                    "response": responses.get(
                        str(intent), responses["general_inquiry"]
                    ),
                }
            )
            return NodeResult(new_state, outcome="responded")

        # Level 2: Specialized sub-agents
        class IntentAnalyzer(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await analyze_customer_query(state)

        class ResponseGenerator(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await generate_support_response(state)

        intent_analyzer = IntentAnalyzer(name="intent_analyzer")
        response_generator = ResponseGenerator(name="response_generator")

        support_classifier = (
            Flow[ChatState]("SupportClassifier")
            .start_with(intent_analyzer)
            .route(intent_analyzer, "classified", response_generator)
            .route(response_generator, "responded", None)  # Terminal
            .build()
        )

        # Level 3: Sentiment analysis layer
        async def analyze_sentiment(state: State[ChatState]) -> NodeResult[ChatState]:
            message = state.data.get("customer_message", "")
            # Simple sentiment detection
            negative_words = ["angry", "frustrated", "terrible", "awful", "hate"]
            sentiment = (
                "negative"
                if any(word in str(message).lower() for word in negative_words)
                else "neutral"
            )
            new_state = state.transform(
                lambda d: {
                    **d,
                    "sentiment": sentiment,
                    "escalate": sentiment == "negative",
                }
            )
            return NodeResult(new_state, outcome="analyzed")

        class SentimentAnalyzer(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await analyze_sentiment(state)

        sentiment_analyzer = SentimentAnalyzer(name="sentiment_analyzer")
        customer_analyzer = (
            Flow[ChatState]("CustomerAnalyzer")
            .start_with(sentiment_analyzer)
            .route(sentiment_analyzer, "analyzed", support_classifier)
            .route(support_classifier, "responded", None)  # Terminal
            .build()
        )

        # Level 4: Main customer service orchestrator
        async def initial_greeting(state: State[ChatState]) -> NodeResult[ChatState]:
            new_state = state.transform(
                lambda d: {
                    **d,
                    "greeted": True,
                    "session_id": "CS-2024-001",
                    "agent_name": "Support Bot",
                }
            )
            return NodeResult(new_state, outcome="ready")

        class Greeter(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await initial_greeting(state)

        greeter = Greeter(name="greeter")
        customer_service_bot = (
            Flow[ChatState]("CustomerServiceBot")
            .start_with(greeter)
            .route(greeter, "ready", customer_analyzer)
            .route(customer_analyzer, "responded", None)  # Terminal
            .build()
        )

        # Run nested agent flows
        result = await customer_service_bot(
            State({"customer_message": "I'm frustrated and want a refund for my order"})
        )
        assert result.state.data.get("greeted") is True
        assert result.state.data.get("sentiment") == "negative"
        assert result.state.data.get("escalate") is True
        assert result.state.data.get("intent") == "refund"
        assert "refund request" in str(result.state.data.get("response", ""))


# ===== FUNCTIONAL UTILITIES TESTS =====


class TestFunctionalPatterns:
    """Test functional patterns using only public API."""

    @staticmethod
    async def test_sequence_pattern() -> None:
        """Test sequential composition using Flow."""

        class TokenizeText(Node[DocumentState]):
            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                text = state.data.get("text", "")
                # Simple tokenization
                tokens = str(text).split()
                new_state = state.transform(
                    lambda d: {**d, "tokens": tokens, "token_count": len(tokens)}
                )
                return NodeResult(new_state, outcome="tokenized")

        class EmbedTokens(Node[DocumentState]):
            @override
            async def exec(
                self, state: State[DocumentState]
            ) -> NodeResult[DocumentState]:
                tokens = state.data.get("tokens", [])
                # Simulate embedding generation
                embeddings = [
                    {"token": t, "vector": [0.1, 0.2, 0.3]}
                    for t in tokens
                    if isinstance(t, str)
                ]
                new_state = state.transform(
                    lambda d: {**d, "embeddings": embeddings, "embedded": True}
                )
                return NodeResult(new_state, outcome="embedded")

        # Compose: tokenize, then embed
        tokenizer = TokenizeText(name="TokenizeText")
        embedder = EmbedTokens(name="EmbedTokens")

        text_processing_pipeline = (
            Flow[DocumentState]("TextProcessingPipeline")
            .start_with(tokenizer)
            .route(tokenizer, "tokenized", embedder)
            .route(embedder, "embedded", None)  # Terminal
            .build()
        )

        initial = State({"text": "Natural language processing with embeddings"})
        result = await text_processing_pipeline(initial)

        assert result.state.data.get("token_count") == 5
        assert len(result.state.data.get("embeddings", [])) == 5
        assert result.state.data.get("embedded") is True

    @staticmethod
    async def test_conditional_pattern() -> None:
        """Test conditional branching using Flow."""

        class ContentModerator(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                content = state.data.get("user_content", "")
                # Simple content moderation check
                sensitive_words = ["spam", "inappropriate", "blocked"]
                is_safe = not any(
                    word in str(content).lower() for word in sensitive_words
                )

                new_state = state.transform(
                    lambda d: {
                        **d,
                        "content_safe": is_safe,
                        "moderation_score": 0.1 if is_safe else 0.9,
                    }
                )
                return NodeResult(new_state, outcome="safe" if is_safe else "flagged")

        class GenerateResponse(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                content = state.data.get("user_content", "")
                response = f"I'll help you with: {content}"
                new_state = state.transform(
                    lambda d: {**d, "ai_response": response, "status": "completed"}
                )
                return NodeResult(new_state, outcome="generated")

        class BlockContent(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                new_state = state.transform(
                    lambda d: {
                        **d,
                        "ai_response": (
                            "I cannot process this content due to policy violations."
                        ),
                        "status": "blocked",
                        "action_taken": "content_filtered",
                    }
                )
                return NodeResult(new_state, outcome="blocked")

        # Build conditional flow for content moderation
        moderator = ContentModerator(name="ContentModerator")
        responder = GenerateResponse(name="GenerateResponse")
        blocker = BlockContent(name="BlockContent")

        moderation_pipeline = (
            Flow[ChatState]("ContentModerationPipeline")
            .start_with(moderator)
            .route(moderator, "safe", responder)
            .route(moderator, "flagged", blocker)
            .build()
        )

        # Test safe content path
        safe_state = State({"user_content": "Help me learn Python programming"})
        safe_result = await moderation_pipeline(safe_state)
        assert safe_result.state.data.get("content_safe") is True
        assert "I'll help you with" in str(
            safe_result.state.data.get("ai_response", "")
        )
        assert safe_result.state.data.get("status") == "completed"

        # Test flagged content path
        flagged_state = State({"user_content": "This is spam content"})
        flagged_result = await moderation_pipeline(flagged_state)
        assert flagged_result.state.data.get("content_safe") is False
        assert "cannot process" in str(flagged_result.state.data.get("ai_response", ""))
        assert flagged_result.state.data.get("status") == "blocked"

    @staticmethod
    async def test_loop_pattern() -> None:
        """Test looping flow using Flow."""

        class RetryableAPICall(Node[ToolState]):
            @override
            async def exec(self, state: State[ToolState]) -> NodeResult[ToolState]:
                attempts = state.data.get("retry_attempts", 0)
                max_retries = state.data.get("max_retries", 3)

                if isinstance(attempts, int) and isinstance(max_retries, int):
                    # Simulate API call with 60% success rate
                    success = (
                        random.random() > 0.4 or attempts >= 2  # noqa: S311 - Simulating API success rate for testing
                    )  # Always succeed on 3rd attempt

                    new_attempts = attempts + 1
                    new_state = state.transform(
                        lambda d: {
                            **d,
                            "retry_attempts": new_attempts,
                            "last_attempt_status": "success" if success else "failed",
                            "api_response": "Data retrieved successfully"
                            if success
                            else None,
                        }
                    )

                    # Determine outcome
                    if success:
                        return NodeResult(new_state, outcome="success")
                    if new_attempts < max_retries:
                        return NodeResult(new_state, outcome="retry")
                    return NodeResult(new_state, outcome="max_retries_exceeded")

                return NodeResult(state, outcome="error")

        api_caller = RetryableAPICall(name="RetryableAPICall")

        retry_flow = (
            Flow[ToolState]("RetryableAPIFlow")
            .start_with(api_caller)
            .route(api_caller, "retry", api_caller)  # Loop back for retry
            .build()
        )

        initial = State({
            "retry_attempts": 0,
            "max_retries": 3,
            "api_endpoint": "https://api.example.com/data",
        })
        result = await retry_flow(initial)

        # Should have made at least one attempt
        assert result.state.data.get("retry_attempts", 0) >= 1
        assert result.state.data.get("retry_attempts", 0) <= 3
        # Should eventually succeed or hit max retries
        assert result.outcome in {"success", "max_retries_exceeded"}

    @staticmethod
    async def test_batch_pattern() -> None:
        """Test batch processing pattern using Flow."""

        @dc
        class DocumentBatch:
            documents: list[dict[str, Any]]
            batch_id: str

        class BatchDocumentProcessor(Node[DocumentBatch]):
            @override
            async def exec(
                self, state: State[DocumentBatch]
            ) -> NodeResult[DocumentBatch]:
                batch = state.data
                processed_docs: list[dict[str, Any]] = []

                # Process each document in the batch
                for doc in batch.documents:
                    # Simulate document processing
                    processed = {
                        "id": doc.get("id", "unknown"),
                        "title": doc.get("title", ""),
                        "word_count": len(str(doc.get("content", "")).split()),
                        "summary": f"Summary of {doc.get('title', 'document')}",
                        "entities_extracted": ["Entity1", "Entity2"],
                        "processed_at": "2024-01-01T10:00:00Z",
                    }
                    processed_docs.append(processed)

                new_batch = DocumentBatch(
                    documents=processed_docs, batch_id=batch.batch_id
                )

                return NodeResult(State(new_batch), outcome="batch_processed")

        batch_processor = BatchDocumentProcessor(name="BatchDocumentProcessor")
        batch_flow = (
            Flow[DocumentBatch]("BatchProcessor").start_with(batch_processor).build()
        )

        # Create batch of documents
        initial_batch = DocumentBatch(
            documents=[
                {
                    "id": "doc1",
                    "title": "AI Research Paper",
                    "content": (
                        "This is a paper about artificial intelligence "
                        "and machine learning"
                    ),
                },
                {
                    "id": "doc2",
                    "title": "Climate Report",
                    "content": "Global climate change impacts and solutions",
                },
                {
                    "id": "doc3",
                    "title": "Tech News",
                    "content": "Latest developments in quantum computing",
                },
            ],
            batch_id="batch-2024-001",
        )

        result = await batch_flow(State(initial_batch))
        processed_docs = result.state.data.documents

        assert len(processed_docs) == 3
        assert all("summary" in doc for doc in processed_docs)
        assert all("entities_extracted" in doc for doc in processed_docs)
        assert processed_docs[0]["word_count"] > 0


# ===== EDGE CASE TESTS =====


class TestEdgeCases:
    """Test edge cases and error handling."""

    @staticmethod
    async def test_flow_without_routes() -> None:
        """Test flow with just a start node."""

        async def single_llm_call(state: State[ChatState]) -> NodeResult[ChatState]:
            new_state = state.transform(
                lambda d: {**d, "response": "Generated response", "completed": True}
            )
            return NodeResult(new_state, outcome="done")

        class LLMCall(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await single_llm_call(state)

        llm_node = LLMCall(name="LLMCall")
        simple_flow = Flow[ChatState]("SimpleLLMFlow").start_with(llm_node).build()

        result = await simple_flow(State({"prompt": "Hello AI"}))
        assert result.state.data.get("completed") is True
        assert result.state.data.get("response") == "Generated response"

    @staticmethod
    async def test_missing_route() -> None:
        """Test flow handles missing routes gracefully."""

        async def intent_router(state: State[ChatState]) -> NodeResult[ChatState]:
            # Return an outcome that has no defined route
            new_state = state.transform(lambda d: {**d, "intent": "unknown_intent"})
            return NodeResult(new_state, outcome="unhandled_intent")

        async def fallback_handler(state: State[ChatState]) -> NodeResult[ChatState]:
            new_state = state.transform(
                lambda d: {**d, "response": "I can help with that!", "handled": True}
            )
            return NodeResult(new_state, outcome="handled")

        class IntentRouter(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await intent_router(state)

        class FallbackHandler(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await fallback_handler(state)

        router = IntentRouter(name="intent_router")
        fallback = FallbackHandler(name="fallback")

        # Build flow without route for "unhandled_intent" outcome
        intent_flow = (
            Flow[ChatState]("IntentRouting")
            .start_with(router)
            .route(router, "known_intent", fallback)  # Only route for known intents
            .build()
        )

        result = await intent_flow(State({"user_query": "Something unexpected"}))

        # Flow should end when route not found
        assert result.outcome == "unhandled_intent"
        assert result.state.data.get("intent") == "unknown_intent"
        assert result.state.data.get("handled") is None

    @staticmethod
    async def test_optional_processing() -> None:
        """Test optional processing pattern."""

        class ConditionalEnhancer(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                should_enhance = state.data.get("enable_enhancement", False)
                prompt = state.data.get("prompt", "")

                if should_enhance:
                    # Enhance the prompt
                    enhanced = f"Enhanced: {prompt} [Added context and examples]"
                    new_state = state.transform(
                        lambda d: {**d, "prompt": enhanced, "enhanced": True}
                    )
                else:
                    # Pass through unchanged
                    new_state = state.transform(lambda d: {**d, "enhanced": False})

                return NodeResult(new_state, outcome="processed")

        enhancer = ConditionalEnhancer(name="ConditionalEnhancer")
        enhancement_flow = (
            Flow[ChatState]("ConditionalEnhancement").start_with(enhancer).build()
        )

        # Test with enhancement disabled
        no_enhance_state = State({
            "prompt": "Tell me about AI",
            "enable_enhancement": False,
        })
        result1 = await enhancement_flow(no_enhance_state)
        assert result1.state.data.get("prompt") == "Tell me about AI"  # Unchanged
        assert result1.state.data.get("enhanced") is False

        # Test with enhancement enabled
        enhance_state = State({
            "prompt": "Tell me about AI",
            "enable_enhancement": True,
        })
        result2 = await enhancement_flow(enhance_state)
        assert "Enhanced:" in result2.state.data.get("prompt", "")
        assert result2.state.data.get("enhanced") is True

    @staticmethod
    async def test_empty_state_handling() -> None:
        """Test handling of empty state."""

        class SafeProcessor(Node[dict[str, Any]]):
            @override
            async def exec(
                self, state: State[dict[str, Any]]
            ) -> NodeResult[dict[str, Any]]:
                # Handle potentially empty state
                data = state.data or {}

                # Add default values if missing
                new_data = {
                    "initialized": True,
                    "timestamp": "2024-01-01T00:00:00Z",
                    **data,  # Preserve any existing data
                }

                return NodeResult(State(new_data), outcome="initialized")

        processor = SafeProcessor(name="SafeProcessor")
        init_flow = Flow[dict[str, Any]]("SafeInit").start_with(processor).build()

        # Test with empty dict
        result = await init_flow(State({}))
        assert result.state.data.get("initialized") is True
        assert "timestamp" in result.state.data


# ===== PROPERTY-BASED TESTS =====


class TestProperties:
    """Property-based tests to verify invariants."""

    @staticmethod
    async def test_state_immutability_property() -> None:
        """Property: State modifications never affect original."""
        for _ in range(100):
            # Generate random agent state
            original_data: ChatState = {
                "session_id": f"session_{random.randint(0, 1000)}",  # noqa: S311 - Test data generation, not cryptographic
                "message_count": random.randint(0, 100),  # noqa: S311 - Test data generation, not cryptographic
                "is_authenticated": random.choice([True, False]),  # noqa: S311 - Test data generation, not cryptographic
                "model": random.choice(["gpt-4", "claude-3", "llama-2"]),  # noqa: S311 - Test data generation, not cryptographic
                "tokens_used": random.randint(0, 10000),  # noqa: S311 - Test data generation, not cryptographic
            }

            state1 = State(dict(original_data))

            # Apply random modifications simulating chat flow
            state2 = state1.transform(
                lambda d: {**d, "message_count": d.get("message_count", 0) + 1}
            )
            state3 = state2.transform(
                lambda d: {
                    **d,
                    "tokens_used": (
                        d.get("tokens_used", 0) + random.randint(10, 200)  # noqa: S311 - Simulating token usage for testing
                    ),
                }
            )
            state4 = state3.transform(
                lambda d: {**d, "last_response": "AI response", "status": "active"}
            )

            # Original must remain unchanged
            assert state1.data == original_data
            assert state1 is not state2
            assert state2 is not state3
            assert state3 is not state4

    @staticmethod
    async def test_flow_determinism_property() -> None:
        """Property: Same input always produces same output."""

        async def deterministic_classifier(
            state: State[ChatState],
        ) -> NodeResult[ChatState]:
            prompt = state.data.get("prompt", "")

            # Deterministic classification based on prompt content
            prompt_lower = str(prompt).lower()
            score = sum(ord(c) for c in prompt_lower)  # Deterministic scoring

            # Classify based on score
            if score < 500:
                category = "simple_query"
            elif score < 1000:
                category = "moderate_query"
            else:
                category = "complex_query"

            confidence = (score % 100) / 100.0  # Deterministic confidence

            new_state = state.transform(
                lambda d: {
                    **d,
                    "category": category,
                    "confidence": confidence,
                    "analysis_score": score,
                }
            )
            return NodeResult(new_state, outcome="classified")

        # Create a simple classification flow
        class Classifier(Node[ChatState]):
            @override
            async def exec(self, state: State[ChatState]) -> NodeResult[ChatState]:
                return await deterministic_classifier(state)

        classifier = Classifier(name="Classifier")
        classification_flow = (
            Flow[ChatState]("DeterministicClassifier").start_with(classifier).build()
        )

        # Test multiple times with same input
        test_prompt = "Explain quantum computing to me"
        test_state = State({"prompt": test_prompt})
        results: list[dict[str, Any]] = []

        for _ in range(10):
            result = await classification_flow(test_state)
            results.append({
                "category": result.state.data.get("category"),
                "confidence": result.state.data.get("confidence"),
                "score": result.state.data.get("analysis_score"),
            })

        # All results must be identical
        if results:
            first_result = results[0]
            assert all(r == first_result for r in results)
            assert (
                first_result["category"] == "complex_query"
            )  # Known result for this prompt

    @staticmethod
    async def test_builder_immutability_property() -> None:
        """Property: Builder operations never modify original builder."""
        for i in range(50):
            # Create agent nodes with realistic names
            agent_names = [
                "PromptAnalyzer",
                "ContentGenerator",
                "ResponseFormatter",
                "QualityChecker",
            ]

            # Create nodes with agent-appropriate names
            analyzer = SimpleNode[ChatState](name=f"{agent_names[0]}_{i}")
            generator = SimpleNode[ChatState](name=f"{agent_names[1]}_{i}")

            # Apply operations simulating agent flow construction
            builder1 = Flow[ChatState](f"ChatAgent_{i}")
            builder2 = builder1.start_with(analyzer)
            builder3 = builder2.route(analyzer, "analyzed", generator)
            builder4 = builder3.route(
                generator, "generated", analyzer
            )  # Allow feedback loop

            # Each operation returns a new instance (immutability)
            assert id(builder1) != id(builder2)  # Different types
            assert builder2 is not builder3
            assert builder3 is not builder4

            # Each builder stage has appropriate methods
            assert hasattr(builder1, "start_with")
            assert hasattr(builder2, "route")
            assert hasattr(builder2, "build")
            assert hasattr(builder3, "route")
            assert hasattr(builder3, "build")
            assert hasattr(builder4, "route")
            assert hasattr(builder4, "build")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
