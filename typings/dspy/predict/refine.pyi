from collections.abc import Callable

from _typeshed import Incomplete
from dspy.adapters.utils import (
    get_field_description_string as get_field_description_string,
)
from dspy.predict.predict import Prediction as Prediction
from dspy.signatures import InputField as InputField
from dspy.signatures import OutputField as OutputField
from dspy.signatures import Signature as Signature

from .predict import Module as Module

class OfferFeedback(Signature):
    program_code: str
    modules_defn: str
    program_inputs: str
    program_trajectory: str
    program_outputs: str
    reward_code: str
    target_threshold: float
    reward_value: float
    module_names: list[str]
    discussion: str
    advice: dict[str, str]

class Refine(Module):
    module: Incomplete
    reward_fn: Incomplete
    threshold: Incomplete
    N: Incomplete
    fail_count: Incomplete
    module_code: Incomplete
    reward_fn_code: Incomplete
    def __init__(self, module: Module, N: int, reward_fn: Callable[[dict, Prediction], float], threshold: float, fail_count: int | None = None) -> None: ...
    def forward(self, **kwargs): ...

def inspect_modules(program): ...
def recursive_mask(o): ...
