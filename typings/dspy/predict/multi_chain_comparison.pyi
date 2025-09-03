from _typeshed import Incomplete
from dspy.predict.predict import Predict as Predict
from dspy.primitives.module import Module as Module
from dspy.signatures import InputField as InputField
from dspy.signatures import OutputField as OutputField
from dspy.signatures.signature import ensure_signature as ensure_signature

class MultiChainComparison(Module):
    M: Incomplete
    predict: Incomplete
    def __init__(self, signature, M: int = 3, temperature: float = 0.7, **config) -> None: ...
    def forward(self, completions, **kwargs): ...
