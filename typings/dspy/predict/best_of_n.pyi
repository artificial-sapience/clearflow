from collections.abc import Callable

from _typeshed import Incomplete
from dspy.predict.predict import Module as Module
from dspy.predict.predict import Prediction as Prediction

class BestOfN(Module):
    module: Incomplete
    reward_fn: Incomplete
    threshold: Incomplete
    N: Incomplete
    fail_count: Incomplete
    def __init__(self, module: Module, N: int, reward_fn: Callable[[dict, Prediction], float], threshold: float, fail_count: int | None = None) -> None: ...
    def forward(self, **kwargs): ...
