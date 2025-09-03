from collections.abc import Callable

import dspy
from _typeshed import Incomplete
from dspy.teleprompt.simba_utils import append_a_demo as append_a_demo
from dspy.teleprompt.simba_utils import append_a_rule as append_a_rule
from dspy.teleprompt.simba_utils import (
    prepare_models_for_resampling as prepare_models_for_resampling,
)
from dspy.teleprompt.simba_utils import wrap_program as wrap_program
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

logger: Incomplete

class SIMBA(Teleprompter):
    metric: Incomplete
    bsize: Incomplete
    num_candidates: Incomplete
    max_steps: Incomplete
    max_demos: Incomplete
    demo_input_field_maxlen: Incomplete
    num_threads: Incomplete
    temperature_for_sampling: Incomplete
    temperature_for_candidates: Incomplete
    strategies: Incomplete
    def __init__(self, *, metric: Callable, bsize: int = 32, num_candidates: int = 6, max_steps: int = 8, max_demos: int = 4, demo_input_field_maxlen: int = 100000, num_threads=None, temperature_for_sampling: float = 0.2, temperature_for_candidates: float = 0.2) -> None: ...
    def compile(self, student: dspy.Module, *, trainset: list[dspy.Example], seed: int = 0): ...
