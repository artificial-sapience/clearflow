"""Test Node abstraction features of ClearFlow.

This module tests the Node class functionality including pure functions,
lifecycle hooks, and routing patterns for mission-critical AI orchestration.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc, replace
from typing import override

import pytest

from clearflow import Node, NodeResult
from tests.conftest import AgentState, Message, ValidationState


class TestNode:
    """Test the Node abstraction."""

    @staticmethod
    async def test_pure_exec_function() -> None:
        """Core principle: exec functions are pure - same input, same output."""

        @dc(frozen=True)
        class TokenCountNode(Node[ValidationState]):
            """Pure function for token counting in LLM validation."""

            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                # Pure transformation: count tokens (simplified)
                token_count = len(state.input_text.split())
                
                if token_count > 100:
                    errors = state.errors + (f"Token count {token_count} exceeds limit",)
                    new_state = replace(state, errors=errors, validated=False)
                    outcome = "too_long"
                else:
                    new_state = replace(state, validated=True)
                    outcome = "valid_length"
                
                return NodeResult(new_state, outcome=outcome)

        node = TokenCountNode()
        initial = ValidationState(input_text="Short prompt for testing")

        # Multiple calls with same input produce same output (functional purity)
        result1 = await node(initial)
        result2 = await node(initial)

        assert result1.state == result2.state
        assert result1.outcome == result2.outcome
        assert result1.state.validated is True
        assert result1.outcome == "valid_length"
        
        # Verify immutability
        assert initial.validated is False

    @staticmethod
    async def test_lifecycle_hooks() -> None:
        """Test that prep and post hooks work correctly."""

        @dc(frozen=True)
        class PromptState:
            """Immutable state for prompt engineering pipeline."""
            raw_prompt: str
            sanitized: bool = False
            validated: bool = False
            enhanced: bool = False

        @dc(frozen=True)
        class PromptEngineeringNode(Node[PromptState]):
            """Node demonstrating lifecycle hooks for prompt engineering."""

            @override
            async def prep(self, state: PromptState) -> PromptState:
                # Sanitize prompt in prep phase
                return replace(state, sanitized=True)

            @override
            async def exec(self, state: PromptState) -> NodeResult[PromptState]:
                # Validate prompt in main execution
                new_state = replace(state, validated=True)
                return NodeResult(new_state, outcome="validated")

            @override
            async def post(self, result: NodeResult[PromptState]) -> NodeResult[PromptState]:
                # Enhance prompt in post phase
                new_state = replace(result.state, enhanced=True)
                return NodeResult(new_state, outcome=result.outcome)

        node = PromptEngineeringNode()
        initial = PromptState(raw_prompt="Explain quantum computing")
        result = await node(initial)

        assert result.state.sanitized is True
        assert result.state.validated is True
        assert result.state.enhanced is True
        assert initial.sanitized is False  # Original unchanged

    @staticmethod
    async def test_llm_router_node() -> None:
        """Test LLM response routing for multi-path orchestration."""

        @dc(frozen=True)
        class LLMRouterNode(Node[AgentState]):
            """Routes to different paths based on LLM analysis."""

            @override
            async def exec(self, state: AgentState) -> NodeResult[AgentState]:
                # Analyze last user message for intent (simulating LLM classification)
                last_msg = state.messages[-1] if state.messages else None
                
                if not last_msg or last_msg.role != "user":
                    outcome = "no_input"
                    response = Message(role="assistant", content="Please provide input.")
                elif "weather" in last_msg.content.lower():
                    outcome = "tool_required"  # Route to tool use flow
                    response = Message(role="assistant", content="I'll check the weather for you.")
                elif "code" in last_msg.content.lower():
                    outcome = "code_generation"  # Route to code gen flow
                    response = Message(role="assistant", content="I'll help you write code.")
                else:
                    outcome = "direct_response"  # Simple Q&A path
                    response = Message(role="assistant", content="I understand your request.")
                
                # Immutable state update
                new_state = AgentState(
                    messages=state.messages + (response,),
                    context=state.context,
                    temperature=0.3 if outcome == "code_generation" else state.temperature
                )
                return NodeResult(new_state, outcome=outcome)

        node = LLMRouterNode()

        # Test tool-required path
        weather_state = AgentState(
            messages=(Message(role="user", content="What's the weather in NYC?"),),
            context="weather_assistant"
        )
        result = await node(weather_state)
        assert result.outcome == "tool_required"
        assert len(result.state.messages) == 2
        assert "check the weather" in result.state.messages[-1].content

        # Test code generation path with temperature adjustment
        code_state = AgentState(
            messages=(Message(role="user", content="Help me write Python code"),),
            context="coding_assistant",
            temperature=0.7
        )
        result = await node(code_state)
        assert result.outcome == "code_generation"
        assert result.state.temperature == 0.3  # Lowered for code generation
        assert "write code" in result.state.messages[-1].content