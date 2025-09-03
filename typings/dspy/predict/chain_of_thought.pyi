from typing import Any

from _typeshed import Incomplete
from dspy.primitives.module import Module as Module
from dspy.primitives.prediction import Prediction as Prediction
from dspy.signatures.signature import Signature as Signature
from dspy.signatures.signature import ensure_signature as ensure_signature
from pydantic.fields import FieldInfo as FieldInfo

class ChainOfThought(Module):
    predict: Incomplete
    def __init__(self, signature: str | type[Signature], rationale_field: FieldInfo | None = None, rationale_field_type: type = ..., **config: dict[str, Any]) -> None: ...
    def forward(self, **kwargs: Any) -> Prediction: ...
    async def aforward(self, **kwargs: Any) -> Prediction: ...
