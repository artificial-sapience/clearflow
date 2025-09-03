from collections.abc import Callable

from _typeshed import Incomplete
from dspy.primitives.example import Example as Example
from dspy.primitives.module import Module as Module
from dspy.teleprompt.bootstrap_finetune import BootstrapFinetune as BootstrapFinetune
from dspy.teleprompt.bootstrap_finetune import (
    all_predictors_have_lms as all_predictors_have_lms,
)
from dspy.teleprompt.bootstrap_finetune import kill_lms as kill_lms
from dspy.teleprompt.bootstrap_finetune import launch_lms as launch_lms
from dspy.teleprompt.bootstrap_finetune import prepare_student as prepare_student
from dspy.teleprompt.random_search import (
    BootstrapFewShotWithRandomSearch as BootstrapFewShotWithRandomSearch,
)
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

logger: Incomplete

class BetterTogether(Teleprompter):
    STRAT_SEP: str
    prompt_optimizer: Incomplete
    weight_optimizer: Incomplete
    rng: Incomplete
    def __init__(self, metric: Callable, prompt_optimizer: Teleprompter | None = None, weight_optimizer: Teleprompter | None = None, seed: int | None = None) -> None: ...
    def compile(self, student: Module, trainset: list[Example], strategy: str = "p -> w -> p", valset_ratio: float = 0.1) -> Module: ...
