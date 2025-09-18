"""Comprehensive stress test file for type safety analyzer.

This file contains various patterns of magic strings and type safety issues
that should be detected by the analyzer, ranging from simple to complex cases.
It serves as both a test case and evaluation benchmark for different LLM models.
"""

import os
from collections.abc import Mapping
from pathlib import Path

# ==============================================================================
# SIMPLE CASES - Basic magic strings that should be easy to detect
# ==============================================================================


def simple_status_check(status: str) -> str:
    """Process status and return corresponding state.

    Args:
        status: The status to check.

    Returns:
        The corresponding state string.

    """
    if status == "pending":
        return "waiting"
    if status == "approved":
        return "ready"
    if status == "rejected":
        return "failed"
    return "unknown"


def simple_mode_config() -> Mapping[str, bool | str]:
    """Generate configuration based on environment mode.

    Returns:
        Configuration dictionary with debug and log_level settings.

    """
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return {"debug": False, "log_level": "error"}
    if env == "staging":
        return {"debug": True, "log_level": "warning"}
    return {"debug": True, "log_level": "debug"}


# ==============================================================================
# INTERMEDIATE CASES - Patterns requiring some analysis
# ==============================================================================


class ApiClient:
    """API client with various string-based configurations."""

    def __init__(self, endpoint: str = "https://api.example.com") -> None:
        """Initialize API client with endpoint."""
        self.endpoint = endpoint
        self.timeout = 30
        self.retry_strategy = "exponential"  # Should be Literal

    @staticmethod
    def request(method: str, **kwargs: str | int) -> Mapping[str, str | Mapping[str, str]]:
        """Make HTTP request with method validation.

        Args:
            method: HTTP method to use.
            **kwargs: Additional parameters.

        Returns:
            Response dictionary with status and data/error.

        Raises:
            ValueError: If method is not supported.

        """
        # HTTP methods - clear pattern for Literal
        if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
            msg = f"Unsupported method: {method}"
            raise ValueError(msg)

        # Status code handling
        http_ok = 200
        http_not_found = 404
        http_server_error = 500
        response_status = kwargs.get("mock_status", http_ok)
        if response_status == http_ok:
            return {"status": "success", "data": {}}
        if response_status == http_not_found:
            return {"status": "not_found", "error": "Resource not found"}
        if response_status == http_server_error:
            return {"status": "server_error", "error": "Internal server error"}
        return {"status": "unknown_error", "error": "Unexpected status"}


def file_operations(operation: str, file_path: str) -> Mapping[str, str]:
    """Perform file operations based on operation type.

    Args:
        operation: The operation to perform.
        file_path: Path to the file.

    Returns:
        Result dictionary with status and action.

    """
    path = Path(file_path)

    operations = {
        "read": lambda: {"result": "success", "action": "file_read"}
        if path.exists()
        else {"result": "error", "action": "file_not_found"},
        "write": lambda: _write_file(path),
        "delete": lambda: _delete_file(path),
    }

    if operation not in operations:
        return {"result": "error", "action": "invalid_operation"}

    return operations[operation]()


def _write_file(path: Path) -> Mapping[str, str]:
    """Write test content to file.

    Returns:
        Result dictionary.

    """
    try:
        path.write_text("test content", encoding="utf-8")
    except OSError:
        return {"result": "error", "action": "write_failed"}
    else:
        return {"result": "success", "action": "file_written"}


def _delete_file(path: Path) -> Mapping[str, str]:
    """Delete file if it exists.

    Returns:
        Result dictionary.

    """
    if path.exists():
        path.unlink()
        return {"result": "success", "action": "file_deleted"}
    return {"result": "error", "action": "file_not_found"}


# ==============================================================================
# ADVANCED CASES - Now simplified (complex cases moved to hard_cases.py)
# ==============================================================================


def validate_user_role(role: str) -> bool:
    """Check if user role is valid.

    Args:
        role: The user role to validate.

    Returns:
        True if role is valid, False otherwise.

    """
    # User roles that should be Literal types
    valid_roles = {"admin", "moderator", "user", "guest"}
    return role in valid_roles


def get_permission_level(role: str) -> int:
    """Get permission level for role.

    Args:
        role: The user role.

    Returns:
        Permission level integer.

    """
    # Permission mapping
    if role == "admin":
        return 100
    if role == "moderator":
        return 50
    if role == "user":
        return 10
    if role == "guest":
        return 1
    return 0


# ==============================================================================
# EDGE CASES - Now simplified (complex cases moved to hard_cases.py)
# ==============================================================================


def get_log_level(severity: str) -> int:
    """Get numeric log level from severity string.

    Args:
        severity: The severity level.

    Returns:
        Numeric log level.

    """
    # Log levels that should be Literal types
    levels = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40,
        "critical": 50,
    }
    return levels.get(severity, 0)


def format_message(msg_type: str, content: str) -> str:
    """Format message based on type.

    Args:
        msg_type: The message type.
        content: The message content.

    Returns:
        Formatted message.

    """
    # Message types that could be Literal
    if msg_type == "alert":
        return f"⚠️  {content}"
    if msg_type == "success":
        return f"✅ {content}"
    if msg_type == "error":
        return f"❌ {content}"
    if msg_type == "info":
        return f"i  {content}"
    return content


# ==============================================================================
# MIXED PATTERNS - Now simplified (complex cases moved to hard_cases.py)
# ==============================================================================


def get_database_driver(db_type: str) -> str:
    """Get database driver based on type.

    Args:
        db_type: The database type.

    Returns:
        Driver name string.

    """
    # Database types that should be Literal
    drivers = {
        "postgresql": "psycopg2",
        "mysql": "pymysql",
        "sqlite": "sqlite3",
        "mongodb": "pymongo",
    }
    return drivers.get(db_type, "unknown")


def get_request_timeout(request_type: str) -> int:
    """Get timeout value based on request type.

    Args:
        request_type: The type of request.

    Returns:
        Timeout in seconds.

    """
    # Request types needing Literal
    if request_type == "quick":
        return 5
    if request_type == "normal":
        return 30
    if request_type == "long_running":
        return 300
    if request_type == "batch":
        return 3600
    return 60  # default timeout


# ==============================================================================
# PERFORMANCE TEST - Split into smaller functions to pass complexity checks
# ==============================================================================


def validate_order(
    order_data: Mapping[str, str | int | float],
) -> bool:
    """Validate order has required fields.

    Returns:
        True if valid, False otherwise.

    """
    if "order_id" not in order_data:
        return False
    return "customer_id" in order_data


def get_processing_config(processing_mode: str) -> Mapping[str, int | str] | None:
    """Get processing configuration for mode.

    Returns:
        Config dict or None if invalid mode.

    """
    configs = {
        "express": {"time": 1, "quality": "basic", "shipping": "overnight"},
        "standard": {"time": 24, "quality": "standard", "shipping": "ground"},
        "economy": {"time": 72, "quality": "minimal", "shipping": "ground_economy"},
        "bulk": {"time": 168, "quality": "batch", "shipping": "freight"},
    }
    if processing_mode not in configs:
        return None
    return configs[processing_mode]


def get_priority_config(priority_level: str, base_time: int) -> Mapping[str, str | int] | None:
    """Get priority configuration.

    Returns:
        Priority config or None if invalid.

    """
    if priority_level == "urgent":
        return {"time": max(1, base_time // 4), "notify": "real_time", "escalate": "manager"}
    if priority_level == "high":
        return {"time": max(2, base_time // 2), "notify": "hourly", "escalate": "supervisor"}
    if priority_level == "normal":
        return {"time": base_time, "notify": "daily", "escalate": "none"}
    if priority_level == "low":
        return {"time": base_time * 2, "notify": "weekly", "escalate": "none"}
    return None


def get_payment_config(payment_method: str) -> Mapping[str, float | bool] | None:
    """Get payment configuration.

    Returns:
        Payment config or None if invalid.

    """
    configs = {
        "credit_card": {"fee": 2.9, "settle": 2, "verify": True},
        "debit_card": {"fee": 1.5, "settle": 1, "verify": True},
        "bank_transfer": {"fee": 0.5, "settle": 5, "verify": False},
        "digital_wallet": {"fee": 1.0, "settle": 1, "verify": False},
        "cryptocurrency": {"fee": 0.1, "settle": 60, "verify": True},
    }
    return configs.get(payment_method)


def comprehensive_order_processor(
    order_data: Mapping[str, str | int | float],
    processing_mode: str = "standard",
    priority_level: str = "normal",
    payment_method: str = "credit_card",
) -> Mapping[str, str | int | float | Mapping[str, str | float]]:
    """Process order with complex validation and business logic.

    Args:
        order_data: Order data dictionary.
        processing_mode: Processing mode.
        priority_level: Priority level.
        payment_method: Payment method.

    Returns:
        Order processing result dictionary.

    """
    # Validate order
    if not validate_order(order_data):
        return {"status": "validation_error", "error": "missing_fields"}

    # Get processing config
    process_config = get_processing_config(processing_mode)
    if not process_config:
        return {"status": "invalid_processing_mode", "mode": processing_mode}

    # Get priority config
    base_time = int(process_config["time"])  # Configs always have int time
    priority_config = get_priority_config(priority_level, base_time)
    if not priority_config:
        return {"status": "invalid_priority", "priority": priority_level}

    # Get payment config
    payment_config = get_payment_config(payment_method)
    if not payment_config:
        return {"status": "unsupported_payment_method", "method": payment_method}

    # Determine final status
    if payment_config["verify"] and priority_level in {"urgent", "high"}:
        final_status = "pending_verification"
    elif processing_mode == "bulk" and payment_method == "cryptocurrency":
        final_status = "pending_approval"
    else:
        final_status = "processing"

    return {
        "status": final_status,
        "order_id": order_data["order_id"],
        "estimated_completion": f"{priority_config['time']} hours",
        "shipping": process_config["shipping"],
        "quality_level": process_config["quality"],
        "notifications": priority_config["notify"],
        "escalation": priority_config["escalate"],
        "payment": {
            "method": payment_method,
            "fee_percent": payment_config["fee"],
            "settlement_hours": payment_config["settle"],
        },
    }


# ==============================================================================
# CONFIGURATION CONSTANTS - Should trigger consolidation suggestions
# ==============================================================================

# These scattered constants should be suggested for consolidation
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"
CACHE_DURATION = 3600
LOG_FORMAT = "json"
RETRY_COUNT = 3
BATCH_SIZE = 100

# Database configurations - another pattern
DB_ENGINE = "postgresql"
DB_POOL_SIZE = 10
DB_TIMEOUT = 15
DB_RETRY_STRATEGY = "exponential"

# Feature flags - yet another pattern
ENABLE_CACHING = True
ENABLE_METRICS = True
ENABLE_TRACING = False
FEATURE_FLAG_MODE = "runtime"
