"""Strict dataclass configuration for mission-critical message validation.

This module provides a pre-configured Pydantic dataclass decorator with the
strictest possible validation settings for mission-critical systems.
"""

from functools import partial

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

__all__ = ["strict_dataclass"]

# Strictest possible Pydantic configuration for mission-critical systems
_STRICT_CONFIG = ConfigDict(
    # --- Pydantic runtime validation/serialization behavior ---
    strict=True,  # No implicit type coercion (e.g., "123" -> 123).
    # Inputs must already match annotated types exactly.
    extra="forbid",  # Reject unknown fields on input; avoids silent data loss
    # and enforces your schema/contract strictly.
    arbitrary_types_allowed=False,  # Disallow un-validated opaque types unless Pydantic
    # knows how to handle them; prevents bypassing validation.
    revalidate_instances="always",  # If nested Pydantic models/dataclasses are provided as values,
    # re-validate them every time; catches mutations made after
    # their initial construction.
    allow_inf_nan=False,  # Forbid NaN and ±Inf for numeric fields; ensures values are
    # well-defined for comparisons, hashing, and serialization.
    validate_default=True,  # Validate default values (including default_factory outputs)
    # so invalid defaults cannot slip through.
)

strict_dataclass = partial(
    dataclass,
    # --- Python dataclass semantics (shape & mutability of the object itself) ---
    frozen=True,  # Make instances immutable after __init__; forbids attribute reassignment.
    # This eliminates whole classes of state bugs and (with eq=True by default)
    # allows hashing/use as dict keys.
    slots=True,  # Use __slots__ to block dynamic attribute creation and reduce memory.
    # Prevents typo-based attribute injection and speeds attribute access.
    kw_only=True,  # Force keyword-only construction so arguments cannot be mis-ordered.
    # Safer when fields are added/reordered over time.
    # --- Pydantic validation via config ---
    config=_STRICT_CONFIG,
)
"""Apply strictest Pydantic dataclass validation for mission-critical code.

This decorator must be applied to EVERY message class in the hierarchy.
Pydantic dataclass settings are NOT inherited from parent classes.

Use this decorator for all message classes to ensure:
- Runtime type validation with no coercion
- Immutability and memory efficiency
- Protection against invalid data
- No NaN/Infinity in numeric fields
- Keyword-only construction

Example:
    from clearflow import Command
    from clearflow.strict_dataclass import strict_dataclass

    @strict_dataclass
    class MyCommand(Command):
        data: str
        value: float  # Will reject NaN/Inf

    # This will raise ValidationError:
    # cmd = MyCommand(data=123)  # Wrong type, no coercion
    # cmd = MyCommand(data="hello", value=float('nan'))  # NaN forbidden
    # cmd = MyCommand(data="hello", value=1.0, extra="field")  # Extra field forbidden

    # This works:
    cmd = MyCommand(data="hello", value=1.0, run_id=uuid4())
"""
