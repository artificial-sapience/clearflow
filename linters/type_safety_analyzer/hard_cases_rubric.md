# Type Safety Analyzer Test Rubric

This document defines the expected detections and fixes for `hard_cases.py`. Each case represents a real-world pattern that should be improved with Literal types for better type safety.

## Score Calculation

- Each correctly identified issue: 1 point
- Each correct fix suggestion: 2 points
- Total possible: 45 points (15 issues × 3 points each)

---

## Case 1: WorkflowEngine State Machine

### Issues to Detect

1. **Line 16: Initial state magic string**
   - Issue: `self.current_state = "initialized"`
   - Should suggest: Define `WorkflowState` Literal type
   - Fix: `WorkflowState = Literal["initialized", "starting", "running", "paused", "completed", "failed", "retrying", "cancelled", "archived"]`

2. **Line 17-26: State transition dictionary keys**
   - Issue: Dictionary keys are magic strings representing states
   - Should suggest: Use WorkflowState as dictionary key type
   - Fix: `allowed_transitions: dict[WorkflowState, list[WorkflowState]]`

3. **Line 29: Parameter type**
   - Issue: `new_state: str` is too broad
   - Should suggest: `new_state: WorkflowState`

4. **Line 50-56: Log level magic strings**
   - Issue: `level = "error"`, `level = "info"`, etc.
   - Should suggest: Define `LogLevel` Literal type
   - Fix: `LogLevel = Literal["debug", "info", "warning", "error"]`

### Expected Fix

```python
from typing import Literal

WorkflowState = Literal["initialized", "starting", "running", "paused",
                        "completed", "failed", "retrying", "cancelled", "archived"]
LogLevel = Literal["debug", "info", "warning", "error"]

class WorkflowEngine:
    current_state: WorkflowState = "initialized"
    allowed_transitions: dict[WorkflowState, list[WorkflowState]]

    def transition_to(self, new_state: WorkflowState) -> bool: ...

    @staticmethod
    def log_transition(from_state: WorkflowState, to_state: WorkflowState) -> None:
        level: LogLevel
        if to_state == "failed":
            level = "error"
        # ...
```

---

## Case 2: Data Validation Pipeline

### Issues to Detect

5. **Line 62: Parameter type**
   - Issue: `validation_type: str` is too broad
   - Should suggest: `ValidationType = Literal["strict", "lenient", "minimal"]`

6. **Line 76-78: Dictionary keys**
   - Issue: Validation config keys are magic strings
   - Should suggest: Use ValidationType for dictionary keys
   - Fix: `validation_configs: dict[ValidationType, tuple[...]]`

7. **Line 83, 90, 97: Status strings**
   - Issue: Return status values like `"error"`, `"validation_failed"`, `"validation_passed"`
   - Should suggest: `ValidationStatus = Literal["error", "validation_failed", "validation_passed"]`

8. **Line 90, 97: Error type strings**
   - Issue: `"missing_required_fields"`, `"invalid_email_format"`
   - Should suggest: `ErrorType = Literal["missing_required_fields", "invalid_email_format", "unknown_validation_type"]`

### Expected Fix

```python
ValidationType = Literal["strict", "lenient", "minimal"]
ValidationStatus = Literal["error", "validation_failed", "validation_passed"]
ErrorType = Literal["missing_required_fields", "invalid_email_format", "unknown_validation_type"]

def data_validation_pipeline(
    data: Mapping[str, str | int],
    validation_type: ValidationType
) -> Mapping[str, ValidationStatus | ErrorType | ...]:
    validation_configs: dict[ValidationType, tuple[...]] = {...}
```

---

## Case 3: Content Processing Functions

### Issues to Detect

9. **Line 108: Format type parameter**
   - Issue: `format_type: str` is too broad
   - Should suggest: `FormatType = Literal["markdown", "json", "plain", "xml"]`

10. **Line 116-127: Content type returns**
    - Issue: Return values like `"text/html"`, `"application/json"`, `"error"`, `"unsupported"`
    - Should suggest: `ContentType = Literal["text/html", "application/json", "text/plain", "application/xml", "error", "unsupported"]`

11. **Line 130: Output mode parameter**
    - Issue: `output_mode: str` is too broad
    - Should suggest: `OutputMode = Literal["inline", "reference", "summary", "metadata_only"]`

12. **Line 137-148: Status returns**
    - Issue: All return dicts have `"status": "success"` or `"status": "invalid_output_mode"`
    - Should suggest: `ProcessStatus = Literal["success", "invalid_output_mode", "error", "unsupported"]`

### Expected Fix

```python
FormatType = Literal["markdown", "json", "plain", "xml"]
ContentType = Literal["text/html", "application/json", "text/plain",
                     "application/xml", "error", "unsupported"]
OutputMode = Literal["inline", "reference", "summary", "metadata_only"]
ProcessStatus = Literal["success", "invalid_output_mode", "error", "unsupported"]

def _process_format(content: str, format_type: FormatType) -> tuple[str, ContentType]: ...
def _process_output(..., output_mode: OutputMode, ...) -> Mapping[str, ...]: ...
def content_processor(content: str, format_type: FormatType, output_mode: OutputMode) -> ...: ...
```

---

## Case 4: Deployment Orchestrator

### Issues to Detect

13. **Line 175: Action parameter**
    - Issue: `action: str` with validation against tuple
    - Should suggest: `DeployAction = Literal["deploy", "rollback", "scale", "restart", "health_check"]`

14. **Line 175: Environment parameter**
    - Issue: `environment: str` with set validation
    - Should suggest: `Environment = Literal["development", "staging", "production"]`

15. **Line 175: Rollback strategy**
    - Issue: `rollback_strategy: str = "immediate"` with set validation
    - Should suggest: `RollbackStrategy = Literal["immediate", "gradual", "manual"]`

### Expected Fix

```python
DeployAction = Literal["deploy", "rollback", "scale", "restart", "health_check"]
Environment = Literal["development", "staging", "production"]
ServiceType = Literal["web_server", "api_gateway", "database", "cache_layer"]
RollbackStrategy = Literal["immediate", "gradual", "manual"]
NotificationLevel = Literal["critical", "normal", "debug"]

def deployment_orchestrator(
    action: DeployAction,
    environment: Environment,
    service_type: ServiceType,
    rollback_strategy: RollbackStrategy = "immediate"
) -> ...: ...
```

---

## Case 5: Cache Eviction Strategy

### Issues to Detect

16. **Line 241: Strategy parameter**
    - Issue: `strategy: str` validated against dictionary keys
    - Should suggest: `CacheStrategy = Literal["lru", "lfu", "ttl", "random", "fifo"]`

### Expected Fix

```python
CacheStrategy = Literal["lru", "lfu", "ttl", "random", "fifo"]

def cache_eviction_strategy(strategy: CacheStrategy, item_count: int) -> str: ...
```

---

## Scoring Guidelines

### Full Credit (3 points per issue)

- Correctly identifies the line number (±2 lines)
- Correctly identifies the type safety issue
- Suggests appropriate Literal type with correct values

### Partial Credit

- 2 points: Identifies issue and suggests Literal but misses some values
- 1 point: Identifies issue but suggests wrong solution (e.g., Enum instead of Literal)
- 0 points: Misses the issue entirely

### Bonus Points

- +1 for suggesting grouping related Literals (e.g., all status types together)
- +1 for suggesting type aliases for complex return types
- +1 for identifying the service_type issue (not explicitly listed but follows pattern)

### Common Mistakes (Deductions)

- -1: Suggesting constants instead of Literal types
- -1: Over-engineering with unnecessary abstractions
- -1: Missing values in Literal definitions
- -1: Suggesting runtime validation instead of type-time safety

---

## Model Performance Benchmarks

### Excellent (40-45 points)

- Identifies all or nearly all issues
- Provides correct Literal type definitions
- Understands the pattern and applies consistently

### Good (30-39 points)

- Identifies most major issues
- Some minor mistakes in Literal definitions
- Generally understands the pattern

### Fair (20-29 points)

- Identifies about half the issues
- May confuse Literal with Enum or constants
- Partial understanding of type safety benefits

### Poor (Below 20 points)

- Misses most issues
- Suggests incorrect solutions
- Doesn't understand Literal type benefits

---

## Notes for Evaluators

1. **Context Matters**: The LLM should recognize these patterns without hints
2. **Consistency**: Solutions should be consistent across similar patterns
3. **Practicality**: Fixes should improve type safety without over-complicating
4. **ClearFlow Alignment**: Solutions should match ClearFlow's philosophy of explicit, type-safe code

This rubric tests whether the LLM can:

- Recognize magic strings that represent finite sets
- Understand when Literal types provide value
- Generate correct Literal type definitions
- Apply patterns consistently across similar code structures
