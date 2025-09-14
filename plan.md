# Pydantic BaseModel Migration Plan for ClearFlow Messages

## Overview

Complete migration from dataclasses to Pydantic BaseModel for ALL message-driven infrastructure to achieve maximum correctness, type-safety, and immutability.

**Goal**: Redesign message API using BaseModel for verified formal correctness with strict runtime validation.

**Key Decision**: Since message-driven architecture is still in feature branch (not merged to main), we have complete freedom to make breaking changes - no backwards compatibility needed.

## Migration Phases

### Phase 1: Create Base Model Infrastructure

#### 1.1 Create StrictBaseModel

- [ ] Create new file `clearflow/strict_base_model.py`
- [ ] Define `StrictBaseModel` class inheriting from BaseModel
- [ ] Add strictest ConfigDict settings (frozen, strict, extra='forbid', etc.)
- [ ] Add comprehensive docstring explaining strictness settings
- [ ] Export from `clearflow/__init__.py`
- [ ] Run `./quality-check.sh clearflow/strict_base_model.py`

#### 1.2 Convert Message Base Class

- [ ] Change `Message` from `@strict_dataclass` to inherit from StrictBaseModel
- [ ] Remove strict_dataclass import
- [ ] Keep `AwareDatetime` and UUID types with Field defaults
- [ ] Update `message_type` property for BaseModel compatibility
- [ ] Run `./quality-check.sh clearflow/message.py`

#### 1.3 Convert Event Class

- [ ] Change `Event` to inherit from Message (which now inherits from StrictBaseModel)
- [ ] Migrate `model_validator` to BaseModel validator pattern
- [ ] Test triggered_by_id validation logic
- [ ] Verify frozen behavior maintained
- [ ] Run `./quality-check.sh clearflow/message.py`

#### 1.4 Convert Command Class

- [ ] Change `Command` to inherit from Message (which now inherits from StrictBaseModel)
- [ ] Update abstract class validation
- [ ] Test that Command cannot be instantiated directly
- [ ] Verify all validation rules work
- [ ] Run `./quality-check.sh clearflow/message.py`

### Phase 2: Node Infrastructure to BaseModel

#### 2.1 Convert Node Class

- [ ] Change `Node[TMessageIn, TMessageOut]` from `@strict_dataclass` to BaseModel
- [ ] Use PEP 695 generic syntax with BaseModel
- [ ] Add ConfigDict with `frozen=True, strict=True`
- [ ] Migrate name validation to BaseModel validator
- [ ] Run `./quality-check.sh clearflow/message_node.py`

#### 2.2 Test Node Inheritance

- [ ] Verify that Node subclasses work with BaseModel parent
- [ ] Test generic type parameters are preserved
- [ ] Ensure process() method signature is maintained
- [ ] Run `./quality-check.sh clearflow/message_node.py`

### Phase 3: MessageFlow to BaseModel

#### 3.1 Convert MessageFlow Class

- [ ] Change `MessageFlow[TStartMessage, TEndMessage]` from dataclass to BaseModel
- [ ] Add ConfigDict with `frozen=True, arbitrary_types_allowed=True`
- [ ] Remove NodeProtocol class completely (no longer needed with BaseModel)
- [ ] Remove TYPE_CHECKING import and conditional imports
- [ ] Change field types to use `Node[Message, Message]` directly
- [ ] Test flow execution with BaseModel
- [ ] Run `./quality-check.sh clearflow/message_flow.py`

#### 3.2 Convert MessageFlowBuilder

- [ ] Change `_MessageFlowBuilder[TStartMessage, TStartOut]` to BaseModel
- [ ] Update builder methods to work with BaseModel
- [ ] Verify immutability in builder pattern
- [ ] Test route and end methods
- [ ] Run `./quality-check.sh clearflow/message_flow.py`

### Phase 4: Remove strict_dataclass Module

#### 4.1 Delete Obsolete Module

- [ ] Remove `clearflow/strict_dataclass.py`
- [ ] Remove `strict_dataclass` from `clearflow/__init__.py` exports
- [ ] Update all imports throughout codebase
- [ ] Run `./quality-check.sh clearflow/`

### Phase 5: Test Infrastructure Updates

#### 5.1 Update Test Message Classes

- [ ] Convert all Command subclasses in `tests/conftest_message.py` to BaseModel
- [ ] Convert all Event subclasses in `tests/conftest_message.py` to BaseModel
- [ ] Update test utility functions for BaseModel
- [ ] Run `./quality-check.sh tests/conftest_message.py`

#### 5.2 Update Test Node Classes

- [ ] Convert Node subclasses in `tests/test_message_node.py` to BaseModel
- [ ] Convert Node subclasses in `tests/test_message_flow.py` to BaseModel
- [ ] Convert Node subclasses in `tests/test_callbacks.py` to BaseModel
- [ ] Run `./quality-check.sh tests/`

#### 5.3 Fix Test Failures

- [ ] Address any validation errors from stricter BaseModel validation
- [ ] Update test assertions for BaseModel behavior
- [ ] Ensure 100% test coverage maintained
- [ ] Run `./quality-check.sh tests/`

### Phase 6: Example Updates

#### 6.1 Portfolio Example

- [ ] Convert portfolio messages to BaseModel in `examples/portfolio_analysis_message_driven/`
- [ ] Update MarketCommand, AnalysisEvent, etc. to BaseModel
- [ ] Test portfolio example execution
- [ ] Run `./quality-check.sh examples/portfolio_analysis_message_driven/`

#### 6.2 Chat Example

- [ ] Convert chat messages to BaseModel in `examples/chat_message_driven/`
- [ ] Update UserMessage, SystemMessage, etc. to BaseModel
- [ ] Test chat example execution
- [ ] Run `./quality-check.sh examples/chat_message_driven/`

#### 6.3 RAG Example

- [ ] Convert RAG messages to BaseModel in `examples/rag_message_driven/`
- [ ] Update QueryCommand, RetrievalEvent, etc. to BaseModel
- [ ] Test RAG example execution
- [ ] Run `./quality-check.sh examples/rag_message_driven/`

### Phase 7: ConsoleHandler JSON Serialization

#### 7.1 Update ConsoleHandler

- [ ] Use BaseModel's `.model_dump_json()` for serialization
- [ ] Configure field exclusion patterns
- [ ] Add JSON syntax colorization
- [ ] Test with all examples
- [ ] Run `./quality-check.sh examples/shared/`

### Phase 8: Add BaseModel-Specific Tests

#### 8.1 Validation Tests

- [ ] Test strict mode (no type coercion)
- [ ] Test extra='forbid' (reject unknown fields)
- [ ] Test frozen=True (immutability)
- [ ] Test Field constraints (min_length, ge, le, etc.)
- [ ] Run `./quality-check.sh tests/`

#### 8.2 Serialization Tests

- [ ] Test `.model_dump()` method
- [ ] Test `.model_dump_json()` method
- [ ] Test field exclusion in serialization
- [ ] Test deserialization with `.model_validate()`
- [ ] Run `./quality-check.sh tests/`

### Phase 9: Documentation Updates

#### 9.1 Update CLAUDE.md

- [ ] Document BaseModel patterns for message API
- [ ] Add examples of BaseModel usage
- [ ] Update architectural principles section
- [ ] Document validation benefits

#### 9.2 Update README if needed

- [ ] Update any API examples
- [ ] Document BaseModel advantages
- [ ] Add migration notes from dataclass approach

### Phase 10: Final Verification

#### 10.1 Full Quality Check

- [ ] Run `./quality-check.sh` (entire codebase)
- [ ] Ensure 100% test coverage maintained
- [ ] Verify all examples work correctly
- [ ] Check performance metrics

#### 10.2 Architectural Validation

- [ ] Verify all classes use BaseModel consistently
- [ ] Check that immutability is enforced everywhere
- [ ] Validate type safety improvements
- [ ] Confirm strict validation is working

## Technical Specifications

### BaseModel Configuration

```python
from pydantic import BaseModel, ConfigDict, Field

class Message(BaseModel):
    model_config = ConfigDict(
        frozen=True,                    # Immutability
        strict=True,                    # No type coercion
        extra='forbid',                 # No extra fields
        arbitrary_types_allowed=False,  # Only validated types
        revalidate_instances='always',  # Always validate nested models
        allow_inf_nan=False,           # No NaN/Inf for numerics
        validate_default=True,          # Validate defaults
    )

    id: UUID = Field(default_factory=uuid4)
    timestamp: AwareDatetime = Field(default_factory=_utc_now)
    run_id: UUID  # Required field
```

### Generic Classes with BaseModel

```python
# PEP 695 syntax (Python 3.12+)
class Node[TIn: Message, TOut: Message](BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    name: str

class MessageFlow[TStart: Message, TEnd: Message](BaseModel):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        arbitrary_types_allowed=True,  # For Node types
    )
    start_node: Node[TStart, Any]
    routes: dict[str, Node | None]
```

## Benefits of BaseModel Approach

1. **Full Generic Support**: PEP 695 syntax works perfectly with BaseModel
2. **Runtime Validation**: Strict validation with no type coercion
3. **True Immutability**: `frozen=True` prevents all mutations
4. **Native Serialization**: `.model_dump_json()` for efficient JSON serialization
5. **Better Type Safety**: Pyright/mypy understand BaseModel better than dataclasses
6. **Consistent Architecture**: One approach for all message infrastructure

## Success Criteria

1.  All tests pass with 100% coverage
2.  All examples execute without errors
3.  Strict validation catches type errors at runtime
4.  JSON serialization works natively
5.  No performance regression
6.  Quality check passes 100%
7.  Full immutability enforced
8.  Type safety improved with generics

## Migration Notes

- No backwards compatibility needed (feature branch)
- Can make breaking API changes for better design
- Focus on correctness over convenience
- Prioritize type safety and immutability