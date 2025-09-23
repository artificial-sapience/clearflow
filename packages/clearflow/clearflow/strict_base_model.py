"""Strict validation base for mission-critical AI systems.

Provides StrictBaseModel - a Pydantic BaseModel configured with maximum strictness
for systems where correctness matters more than convenience. Every setting is
chosen to catch errors early rather than allow ambiguous behavior.

Key guarantees:
- Immutable after creation (frozen=True)
- No type coercion (strict=True)
- No silent data loss (extra='forbid')
- No NaN/Inf in numerics (allow_inf_nan=False)

Use this for messages, events, and configuration where data integrity is critical.
"""

from pydantic import BaseModel, ConfigDict

__all__ = ["StrictBaseModel"]


class StrictBaseModel(BaseModel):
    """Pydantic base with maximum validation strictness for data integrity.

    Enforces fail-fast validation with zero tolerance for ambiguity. Every input
    is validated strictly, every output is immutable, and every edge case that
    could hide bugs is rejected.

    Why use this over regular BaseModel:
    - Catches type mismatches at system boundaries (no "123" → 123 coercion)
    - Prevents mutation bugs (instances are frozen after creation)
    - Rejects malformed data early (no extra fields, no NaN values)
    - Settings inherit to all subclasses (unlike dataclass configs)

    Example:
        >>> from clearflow.strict_base_model import StrictBaseModel
        >>> from pydantic import Field
        >>> from uuid import UUID, uuid4

        >>> class QueryCommand(StrictBaseModel):
        ...     id: UUID = Field(default_factory=uuid4)
        ...     query: str
        ...     temperature: float  # Rejects NaN/Inf

        >>> # Type safety - these all raise ValidationError:
        >>> QueryCommand(query=123)  # Wrong type
        >>> QueryCommand(query="test", temperature=float('nan'))  # NaN
        >>> QueryCommand(query="test", temperature=0.7, extra="field")  # Unknown field

        >>> # Immutability - this raises ValidationError:
        >>> cmd = QueryCommand(query="test", temperature=0.7)
        >>> cmd.query = "changed"  # Can't mutate frozen instance

    Perfect for:
    - Message types in message-driven systems
    - Configuration that must be validated once
    - API contracts where schema compliance is critical
    - Any data structure where mutation would be a bug

    """

    model_config = ConfigDict(
        # Immutability
        frozen=True,  # Instances cannot be modified after creation
        # Prevents accidental mutation and enables use as dict keys
        # Type strictness
        strict=True,  # No type coercion: "123" won't become 123
        # Forces explicit type conversions at system boundaries
        # Schema enforcement
        extra="forbid",  # Unknown fields raise errors
        # Catches typos and schema drift immediately
        # Performance optimization
        revalidate_instances="never",  # Skip re-validating frozen models
        # Already-validated frozen instances are trusted (1.7x faster)
        # Numeric safety
        allow_inf_nan=False,  # Reject float('inf') and float('nan')
        # Prevents comparison bugs and JSON serialization issues
        # Default validation
        validate_default=True,  # Check default values at class definition
        # Catches invalid defaults before any instance is created
        # Type flexibility
        arbitrary_types_allowed=True,  # Accept any type annotation
        # Enables domain types, dataclasses, and AI library integration
        # Precise behavior
        use_enum_values=False,  # Keep enums as objects (not their values)
        populate_by_name=False,  # Only accept exact field names (no aliases)
        str_strip_whitespace=False,  # Preserve exact string input
    )
