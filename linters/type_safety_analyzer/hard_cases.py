"""Test cases for type safety analyzer benchmarking.

This module contains various Python patterns found in production code
that may benefit from type safety improvements.
"""

import json
from collections.abc import Mapping


class WorkflowEngine:
    """Workflow engine with state transitions."""

    def __init__(self) -> None:
        """Initialize workflow engine with initial state."""
        self.current_state = "initialized"
        self.allowed_transitions = {
            "initialized": ["starting", "cancelled"],
            "starting": ["running", "failed"],
            "running": ["paused", "completed", "failed"],
            "paused": ["running", "cancelled"],
            "completed": ["archived"],
            "failed": ["retrying", "cancelled"],
            "retrying": ["running", "failed"],
            "cancelled": ["archived"],
            "archived": [],
        }

    def transition_to(self, new_state: str) -> bool:
        """Transition to new state with validation.

        Args:
            new_state: The state to transition to.

        Returns:
            True if transition was successful, False otherwise.

        """
        if new_state in self.allowed_transitions.get(self.current_state, []):
            old_state = self.current_state
            self.current_state = new_state
            WorkflowEngine.log_transition(old_state, new_state)
            return True
        return False

    @staticmethod
    def log_transition(from_state: str, to_state: str) -> None:
        """Log state transition with appropriate severity level."""
        if to_state == "failed":
            level = "error"
        elif to_state == "completed":
            level = "info"
        elif to_state in {"paused", "cancelled"}:
            level = "warning"
        else:
            level = "debug"

        print(f"[{level}] State transition: {from_state} -> {to_state}")


def data_validation_pipeline(
    data: Mapping[str, str | int], validation_type: str
) -> Mapping[str, str | int | tuple[str, ...] | Mapping[str, str | int]]:
    """Validate data using specified validation strategy.

    Args:
        data: Data dictionary to validate.
        validation_type: Type of validation to apply.

    Returns:
        Validation result dictionary.

    """
    # Get validation fields based on type
    validation_configs = {
        "strict": (("id", "name", "email", "created_at"), ("phone", "address")),
        "lenient": (("id", "name"), ("email", "phone", "address", "created_at")),
        "minimal": (("id",), ("name", "email", "phone", "address", "created_at")),
    }

    fields = validation_configs.get(validation_type)
    if not fields:
        return {"status": "error", "message": "unknown_validation_type"}

    required_fields, optional_fields = fields

    # Field validation with result types
    missing_fields = tuple(field for field in required_fields if field not in data)
    if missing_fields:
        return {"status": "validation_failed", "error_type": "missing_required_fields", "details": missing_fields}

    # Email validation (if present)
    email_value = data.get("email")
    if isinstance(email_value, str) and "@" not in email_value:
        return {
            "status": "validation_failed",
            "error_type": "invalid_email_format",
            "details": {"field": "email", "value": email_value},
        }

    return {
        "status": "validation_passed",
        "validated_fields": len(tuple(f for f in data if f in required_fields + optional_fields)),
        "validation_level": validation_type,
    }


def _process_format(content: str, format_type: str) -> tuple[str, str]:
    """Process input format and return processed content with type.

    Returns:
        Tuple of (processed_content, content_type).

    """
    if format_type == "markdown":
        return content.replace("# ", "<h1>").replace("## ", "<h2>"), "text/html"
    if format_type == "json":
        try:
            parsed = json.loads(content)
            return str(parsed), "application/json"
        except json.JSONDecodeError:
            return "", "error"
    if format_type == "plain":
        return content.strip(), "text/plain"
    if format_type == "xml":
        return f"<root>{content}</root>", "application/xml"
    return "", "unsupported"


def _process_output(processed: str, content_type: str, output_mode: str, format_type: str) -> Mapping[str, str | int]:
    """Process output mode and return result dictionary.

    Returns:
        Dictionary with status and content based on output mode.

    """
    if output_mode == "inline":
        return {"status": "success", "content": processed, "type": content_type}
    if output_mode == "reference":
        ref_id = f"ref_{hash(processed) % 10000}"
        return {"status": "success", "reference": ref_id, "type": content_type}
    if output_mode == "summary":
        max_len = 100
        summary = processed[:max_len] + "..." if len(processed) > max_len else processed
        return {"status": "success", "summary": summary, "type": content_type}
    if output_mode == "metadata_only":
        return {"status": "success", "length": len(processed), "type": content_type, "format": format_type}
    return {"status": "invalid_output_mode", "mode": output_mode}


def content_processor(content: str, format_type: str, output_mode: str) -> Mapping[str, str | int]:
    """Process content with specified format and output mode.

    Args:
        content: Content to process.
        format_type: Input format type.
        output_mode: Output mode.

    Returns:
        Processed content dictionary.

    """
    # Process input format
    processed, content_type = _process_format(content, format_type)

    # Check for errors
    if content_type in {"error", "unsupported"}:
        return {"status": content_type, "format": format_type}

    # Process output mode
    return _process_output(processed, content_type, output_mode, format_type)


def deployment_orchestrator(
    action: str, environment: str, service_type: str, rollback_strategy: str = "immediate"
) -> Mapping[str, str | int | bool | Mapping[str, str | int | bool]]:
    """Orchestrate deployment based on action and environment.

    Args:
        action: Deployment action to perform.
        environment: Target environment.
        service_type: Type of service to deploy.
        rollback_strategy: Rollback strategy to use.

    Returns:
        Deployment configuration dictionary.

    """
    # Deployment actions
    valid_actions = ("deploy", "rollback", "scale", "restart", "health_check")
    if action not in valid_actions:
        return {"status": "invalid_action", "action": action}

    # Environment validation
    if environment not in {"development", "staging", "production"}:
        return {"status": "invalid_environment", "environment": environment}

    # Service configurations
    service_configs = {
        "web_server": {"port": 80, "health": "/health", "scaling": 2},
        "api_gateway": {"port": 443, "health": "/api/health", "scaling": 1},
        "database": {"port": 5432, "health": "/db/status", "scaling": 0},
        "cache_layer": {"port": 6379, "health": "/cache/ping", "scaling": 3},
    }

    service_config = service_configs.get(service_type)
    if not service_config:
        return {"status": "unknown_service_type", "service": service_type}

    # Rollback strategies (conditional on action)
    if action == "deploy" and rollback_strategy not in {"immediate", "gradual", "manual"}:
        return {"status": "invalid_rollback_strategy", "strategy": rollback_strategy}

    # Complex conditional logic for environment
    if environment == "production" and action == "deploy" and rollback_strategy == "immediate":
        approval_required = True
        notification_level = "critical"
    elif environment == "production":
        approval_required = False
        notification_level = "normal"
    else:
        approval_required = False
        notification_level = "debug"

    return {
        "status": "deployment_configured",
        "config": {
            "action": action,
            "environment": environment,
            "service": service_type,
            "port": service_config["port"],
            "health_check": service_config["health"],
            "scaling": service_config["scaling"],
            "rollback": rollback_strategy,
            "approval_required": approval_required,
            "notification_level": notification_level,
        },
    }


def cache_eviction_strategy(strategy: str, item_count: int) -> str:
    """Determine cache eviction behavior based on strategy.

    Args:
        strategy: The eviction strategy to use.
        item_count: Number of items to consider.

    Returns:
        Description of eviction behavior.

    """
    strategies = {
        "lru": f"evict_{item_count}_least_recently_used",
        "lfu": f"evict_{item_count}_least_frequently_used",
        "ttl": f"evict_{item_count}_expired_items",
        "random": f"evict_{item_count}_random_selection",
        "fifo": f"evict_{item_count}_first_in_first_out",
    }

    return strategies.get(strategy, "unknown_strategy")
