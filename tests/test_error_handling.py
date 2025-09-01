"""Test error handling and edge cases for ClearFlow.

This module tests error conditions, edge cases, and validation logic
to ensure robust behavior in mission-critical scenarios.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import override

import pytest

from clearflow import Flow, Node, NodeResult
from tests.conftest import ValidationState


class TestErrorHandling:
    """Test error handling and edge cases."""

    @staticmethod
    async def test_missing_route() -> None:
        """Test behavior when a route is not defined."""

        @dc(frozen=True)
        class UnpredictableNode(Node[dict[str, str]]):
            """Node with variable outcomes."""

            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                # Return an outcome that might not be routed
                outcome = state.get("force_outcome", "unexpected")
                return NodeResult(state, outcome=outcome)

        node = UnpredictableNode()

        # Flow with incomplete routing
        flow = (
            Flow[dict[str, str]]("IncompleteFlow")
            .start_with(node)
            .route(node, "expected", None)
            # "unexpected" outcome not routed
            .build()
        )

        # Should bubble up the unhandled outcome
        result = await flow({"force_outcome": "unexpected"})
        assert result.outcome == "unexpected"

    @staticmethod
    async def test_empty_flow_name() -> None:
        """Test that flow names must be non-empty."""
        with pytest.raises(ValueError, match="non-empty string"):
            Flow[dict[str, object]]("")

        with pytest.raises(ValueError, match="non-empty string"):
            Flow[dict[str, object]]("   ")

    @staticmethod
    async def test_node_name_inference() -> None:
        """Test that nodes get names from their class if not provided."""

        @dc(frozen=True)
        class MyCustomNode(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                return NodeResult(state, outcome="done")

        # No name provided
        node = MyCustomNode()
        assert node.name == "MyCustomNode"

        # Explicit name provided
        named_node = MyCustomNode(name="custom_name")
        assert named_node.name == "custom_name"

    @staticmethod
    async def test_single_node_flow_no_routes() -> None:
        """Test a flow with a single node and no routes (line 94 coverage)."""

        @dc(frozen=True)
        class StandaloneNode(Node[dict[str, object]]):
            @override
            async def exec(self, state: dict[str, object]) -> NodeResult[dict[str, object]]:
                return NodeResult(state, outcome="standalone")

        node = StandaloneNode()

        # Create flow with single node but no routes
        flow = Flow[dict[str, object]]("SingleNodeFlow").start_with(node).build()

        # Execute - should return result as-is since no routes exist
        result = await flow({"test": "value"})
        assert result.outcome == "standalone"
        assert result.state["test"] == "value"

    @staticmethod
    async def test_node_without_name_validation() -> None:
        """Test routing fails when from_node lacks name (lines 122-123 coverage)."""

        @dc(frozen=True)
        class UnnamedNode(Node[ValidationState]):
            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="done")

        # Manually create node with empty name to trigger validation
        unnamed_node = UnnamedNode()
        object.__setattr__(unnamed_node, "name", "")  # noqa: PLC2801

        @dc(frozen=True)
        class TargetNode(Node[ValidationState]):
            """Target node for routing."""
            
            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="done")
        
        target_node = TargetNode()

        # Should raise ValueError when trying to route from unnamed node
        with pytest.raises(ValueError, match="from_node must have a name"):
            (
                Flow[ValidationState]("TestFlow")
                .start_with(target_node)
                .route(unnamed_node, "done", None)
            )