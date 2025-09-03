from typing import Literal

from pydantic.fields import FieldInfo as FieldInfo

def get_dspy_field_type(field: FieldInfo) -> Literal["input", "output"]: ...
