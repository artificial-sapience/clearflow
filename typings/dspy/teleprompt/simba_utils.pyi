from collections.abc import Callable

import dspy
from _typeshed import Incomplete
from dspy.adapters.utils import (
    get_field_description_string as get_field_description_string,
)
from dspy.signatures import InputField as InputField
from dspy.signatures import OutputField as OutputField

logger: Incomplete

def prepare_models_for_resampling(program: dspy.Module, n: int): ...
def wrap_program(program: dspy.Module, metric: Callable): ...
def append_a_demo(demo_input_field_maxlen): ...
def append_a_rule(bucket, system, **kwargs): ...

class OfferFeedback(dspy.Signature):
    program_code: str
    modules_defn: str
    program_inputs: str
    oracle_metadata: str
    worse_program_trajectory: str
    worse_program_outputs: str
    worse_reward_value: float
    better_program_trajectory: str
    better_program_outputs: str
    better_reward_value: float
    module_names: list[str]
    discussion: str
    module_advice: dict[str, str]

def inspect_modules(program): ...
def recursive_mask(o): ...
