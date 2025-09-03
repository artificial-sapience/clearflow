from _typeshed import Incomplete
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

from .vanilla import LabeledFewShot as LabeledFewShot

logger: Incomplete

class BootstrapFewShot(Teleprompter):
    metric: Incomplete
    metric_threshold: Incomplete
    teacher_settings: Incomplete
    max_bootstrapped_demos: Incomplete
    max_labeled_demos: Incomplete
    max_rounds: Incomplete
    max_errors: Incomplete
    error_count: int
    error_lock: Incomplete
    def __init__(self, metric=None, metric_threshold=None, teacher_settings: dict | None = None, max_bootstrapped_demos: int = 4, max_labeled_demos: int = 16, max_rounds: int = 1, max_errors=None) -> None: ...
    trainset: Incomplete
    student: Incomplete
    def compile(self, student, *, teacher=None, trainset): ...
