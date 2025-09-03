from _typeshed import Incomplete
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

class LabeledFewShot(Teleprompter):
    k: Incomplete
    def __init__(self, k: int = 16) -> None: ...
    student: Incomplete
    trainset: Incomplete
    def compile(self, student, *, trainset, sample: bool = True): ...
