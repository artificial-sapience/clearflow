# Pydantic Migration Plan for ClearFlow Messages

## Overview

Migrate Message API from vanilla frozen dataclasses to Pydantic dataclasses with strict validation for mission-critical correctness.

**Goal**: Maximum type safety and runtime validation while maintaining API compatibility.

## Migration Phases

### Phase 1: Core Infrastructure Setup

#### 1.1 Add Pydantic Dependency

- [ ] Update `pyproject.toml` to add `pydantic>=2.11.0` as dependency
- [ ] Run `uv sync` to install
- [ ] Run `./quality-check.sh` to ensure no breakage

#### 1.2 Create Migration Branch

- [ ] Create feature branch `feat/pydantic-messages`
- [ ] Document breaking changes if any

### Phase 2: Message Base Class Migration

#### 2.1 Update Message Base Class

- [ ] Import from `pydantic.dataclasses` instead of `dataclasses`
- [ ] Add strict config: `config={'strict': True, 'extra': 'forbid', 'validate_assignment': True}`
- [ ] Change `datetime` to `AwareDatetime` type
- [ ] Update UUID handling for Pydantic compatibility
- [ ] Run `./quality-check.sh clearflow/message.py`

#### 2.2 Update Event Class

- [ ] Migrate Event to Pydantic dataclass
- [ ] Ensure `__post_init__` validation works with Pydantic
- [ ] Test triggered_by_id validation
- [ ] Run `./quality-check.sh clearflow/message.py`

#### 2.3 Update Command Class

- [ ] Migrate Command to Pydantic dataclass
- [ ] Ensure `__post_init__` validation works
- [ ] Test abstract class instantiation prevention
- [ ] Run `./quality-check.sh clearflow/message.py`

### Phase 3: Message Node Migration

#### 3.1 Update MessageNode

- [ ] Migrate MessageNode to Pydantic dataclass
- [ ] Ensure name validation works
- [ ] Test frozen behavior maintained
- [ ] Run `./quality-check.sh clearflow/message_node.py`

### Phase 4: Message Flow Migration

#### 4.1 Update MessageFlow Components

- [ ] Check if MessageFlow needs Pydantic migration
- [ ] Update any internal dataclasses
- [ ] Run `./quality-check.sh clearflow/message_flow.py`

### Phase 5: Callback System Migration

#### 5.1 Update CallbackHandler if needed

- [ ] Check if callbacks use dataclasses
- [ ] Migrate if necessary
- [ ] Run `./quality-check.sh clearflow/callbacks.py`

### Phase 6: Test Suite Verification

#### 6.1 Run Existing Tests

- [ ] Run `./quality-check.sh tests` - should pass 100%
- [ ] Fix any test failures due to stricter validation
- [ ] Document any behavior changes

#### 6.2 Add Pydantic-Specific Tests

- [ ] Test strict mode validation
- [ ] Test extra='forbid' behavior
- [ ] Test validate_assignment=True
- [ ] Test AwareDatetime validation
- [ ] Run `./quality-check.sh tests`

### Phase 7: Example Updates

#### 7.1 Portfolio Example

- [ ] Test portfolio example still works
- [ ] Update any message creation that fails validation
- [ ] Run `./quality-check.sh examples/portfolio_analysis_message_driven`

#### 7.2 Chat Example

- [ ] Test chat example still works
- [ ] Update if needed
- [ ] Run `./quality-check.sh examples/chat_message_driven`

#### 7.3 RAG Example

- [ ] Test RAG example still works
- [ ] Update if needed
- [ ] Run `./quality-check.sh examples/rag_message_driven`

### Phase 8: ConsoleHandler JSON Serialization

#### 8.1 Update ConsoleHandler

- [ ] Use Pydantic's `.model_dump_json()` for serialization
- [ ] Configure exclusion of internal fields
- [ ] Add JSON syntax colorization
- [ ] Test with portfolio example
- [ ] Run `./quality-check.sh examples/shared`

### Phase 9: Documentation Updates

#### 9.1 Update Documentation

- [ ] Update README.md if API changes
- [ ] Update CLAUDE.md with Pydantic patterns
- [ ] Document validation benefits
- [ ] Add migration guide if breaking changes

### Phase 10: Final Verification

#### 10.1 Full Quality Check

- [ ] Run `./quality-check.sh` (entire codebase)
- [ ] Ensure 100% test coverage maintained
- [ ] Verify all examples work
- [ ] Check performance impact

## Technical Decisions

### Pydantic Config Settings

```python
# Strictest Pydantic-dataclass configuration with explanations for each setting.
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

@dataclass(
    # --- Python dataclass semantics (shape & mutability of the object itself) ---
    frozen=True,  # Make instances immutable after __init__; forbids attribute reassignment.
                  # This eliminates whole classes of state bugs and (with eq=True by default)
                  # allows hashing/use as dict keys.
    slots=True,   # Use __slots__ to block dynamic attribute creation and reduce memory.
                  # Prevents typo-based attribute injection and speeds attribute access.
    kw_only=True, # Force keyword-only construction so arguments cannot be mis-ordered.
                  # Safer when fields are added/reordered over time.

    # --- Pydantic runtime validation/serialization behavior ---
    config=ConfigDict(
        strict=True,                   # No implicit type coercion (e.g., "123" -> 123).
                                       # Inputs must already match annotated types exactly.
        extra='forbid',                # Reject unknown fields on input; avoids silent data loss
                                       # and enforces your schema/contract strictly.
        arbitrary_types_allowed=False, # Disallow un-validated opaque types unless Pydantic
                                       # knows how to handle them; prevents bypassing validation.
        revalidate_instances='always', # If nested Pydantic models/dataclasses are provided as values,
                                       # re-validate them every time; catches mutations made after
                                       # their initial construction.
        allow_inf_nan=False,           # Forbid NaN and ±Inf for numeric fields; ensures values are
                                       # well-defined for comparisons, hashing, and serialization.
        validate_default=True,         # Validate default values (including default_factory outputs)
                                       # so invalid defaults cannot slip through.
        # validate_assignment=True,    # Not needed when frozen: reassignment isn't possible.
    ),
)
class Message:
    ...
```

### Type Migrations

| Current Type | Pydantic Type | Reason |
|-------------|---------------|--------|
| `datetime` | `AwareDatetime` | Ensures timezone-aware timestamps |
| `UUID` | `UUID` | Pydantic handles UUID validation |
| `str` | `str` with constraints | Can add `Field(min_length=1)` etc |
| `float` | `float` with constraints | Can add `Field(ge=0, le=100)` for percentages |

### Breaking Changes Risk Assessment

**Low Risk** - Pydantic dataclasses are mostly compatible:

- Same initialization syntax
- Same attribute access
- Frozen behavior maintained

**Potential Issues**:

- Stricter validation may reject previously valid data
- `__post_init__` behavior might need adjustment
- Import changes needed in message.py only

## Success Criteria

1.  All tests pass with 100% coverage
2.  All examples run without modification (or minimal updates)
3.  Strict validation catches type errors at runtime
4.  JSON serialization works natively
5.  No performance regression
6.  Quality check passes 100%

## Rollback Plan

If issues arise:

1. Keep vanilla dataclasses in core (`clearflow/__init__.py`)
2. Only use Pydantic for Message API
3. Can revert by changing imports back to `dataclasses`
