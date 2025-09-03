from typing import Any, Optional

from _typeshed import Incomplete
from pydantic.fields import FieldInfo

DSPY_FIELD_ARG_NAMES: Incomplete
PYDANTIC_CONSTRAINT_MAP: Incomplete

def move_kwargs(**kwargs: Any) -> dict[str, Any]: ...
def InputField(
    *,
    desc: str = "",
    prefix: str = "",
    format: Any | None = None,
    **kwargs: Any
) -> FieldInfo: ...
def OutputField(
    *,
    desc: str = "",
    prefix: str = "",
    format: Any | None = None,
    **kwargs: Any
) -> FieldInfo: ...
def new_to_old_field(field): ...

class OldField:
    prefix: Incomplete
    desc: Incomplete
    format: Incomplete
    def __init__(self, *, prefix=None, desc=None, input, format=None) -> None: ...
    def finalize(self, key, inferred_prefix) -> None: ...
    def __eq__(self, __value: object) -> bool: ...

class OldInputField(OldField):
    def __init__(self, *, prefix=None, desc=None, format=None) -> None: ...

class OldOutputField(OldField):
    def __init__(self, *, prefix=None, desc=None, format=None) -> None: ...
