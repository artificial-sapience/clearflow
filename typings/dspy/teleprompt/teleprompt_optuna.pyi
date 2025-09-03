from _typeshed import Incomplete
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

from .bootstrap import BootstrapFewShot as BootstrapFewShot

class BootstrapFewShotWithOptuna(Teleprompter):
    metric: Incomplete
    teacher_settings: Incomplete
    max_rounds: Incomplete
    num_threads: Incomplete
    min_num_samples: int
    max_num_samples: Incomplete
    num_candidate_sets: Incomplete
    max_labeled_demos: Incomplete
    def __init__(self, metric, teacher_settings=None, max_bootstrapped_demos: int = 4, max_labeled_demos: int = 16, max_rounds: int = 1, num_candidate_programs: int = 16, num_threads=None) -> None: ...
    def objective(self, trial): ...
    trainset: Incomplete
    valset: Incomplete
    student: Incomplete
    teacher: Incomplete
    compiled_teleprompter: Incomplete
    def compile(self, student, *, teacher=None, max_demos, trainset, valset=None): ...
