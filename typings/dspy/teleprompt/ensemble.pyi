from _typeshed import Incomplete
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

class Ensemble(Teleprompter):
    reduce_fn: Incomplete
    size: Incomplete
    deterministic: Incomplete
    def __init__(self, *, reduce_fn=None, size=None, deterministic: bool = False) -> None: ...
    programs: Incomplete
    def compile(self, programs): ...
