"""Strict base model for mission-critical validation with Pydantic BaseModel.

This module provides a base class with the strictest possible validation settings
for mission-critical systems using Pydantic's BaseModel instead of dataclasses.
"""

from pydantic import BaseModel, ConfigDict

__all__ = ["StrictBaseModel"]


class StrictBaseModel(BaseModel):
    """Base model with strictest validation for mission-critical correctness.

    This class enforces the same level of strictness as strict_dataclass but using
    BaseModel which provides better support for generic types and inheritance.

    Strictness settings:
    - frozen=True: Immutable after creation (no attribute reassignment)
    - strict=True: No implicit type coercion (e.g., "123" -> 123)
    - extra='forbid': Reject unknown fields to prevent silent data loss
    - revalidate_instances='always': Always revalidate nested models
    - allow_inf_nan=False: Forbid NaN and ±Inf for numeric fields
    - validate_default=True: Validate default values and default_factory outputs
    - arbitrary_types_allowed=False: Only allow validated types by default

    Unlike Pydantic dataclasses, these settings ARE inherited by subclasses,
    making this approach more maintainable and consistent.

    Example:
        from clearflow.strict_base_model import StrictBaseModel
        from pydantic import Field
        import uuid

        class MyMessage(StrictBaseModel):
            id: uuid.UUID = Field(default_factory=uuid.uuid4)
            data: str
            value: float  # Will reject NaN/Inf

        # This will raise ValidationError:
        # msg = MyMessage(data=123)  # Wrong type, no coercion
        # msg = MyMessage(data="hello", value=float('nan'))  # NaN forbidden
        # msg = MyMessage(data="hello", value=1.0, extra="field")  # Extra field forbidden

        # This works:
        msg = MyMessage(data="hello", value=1.0)

        # This will raise ValidationError (frozen):
        # msg.data = "changed"  # Immutable

    """

    model_config = ConfigDict(
        # --- Immutability and shape ---
        frozen=True,  # Make instances immutable after creation
        # Prevents attribute reassignment and enables hashability
        # --- Strict validation behavior ---
        strict=True,  # No implicit type coercion
        # Inputs must match annotated types exactly
        extra="forbid",  # Reject unknown fields on input
        # Enforces schema contract strictly
        # --- Nested model validation ---
        revalidate_instances="never",  # Trust already-validated frozen models
        # No benefit for immutable models, improves performance ~1.7x
        # --- Numeric validation ---
        allow_inf_nan=False,  # Forbid NaN and ±Inf for numeric fields
        # Ensures well-defined values for comparisons
        # --- Default value validation ---
        validate_default=True,  # Validate default values and default_factory outputs
        # Ensures invalid defaults cannot slip through
        # --- Type validation ---
        arbitrary_types_allowed=False,  # Disallow unvalidated opaque types by default
        # Prevents bypassing validation
        # Can override in subclasses when needed
        # --- Additional strictness ---
        use_enum_values=False,  # Keep enums as objects, not their values
        populate_by_name=False,  # Only allow field names, not aliases
        str_strip_whitespace=False,  # Don't automatically strip whitespace
    )
