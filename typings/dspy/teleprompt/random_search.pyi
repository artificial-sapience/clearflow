from _typeshed import Incomplete
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

from .bootstrap import BootstrapFewShot as BootstrapFewShot
from .vanilla import LabeledFewShot as LabeledFewShot

class BootstrapFewShotWithRandomSearch(Teleprompter):
    metric: Incomplete
    teacher_settings: Incomplete
    max_rounds: Incomplete
    num_threads: Incomplete
    stop_at_score: Incomplete
    metric_threshold: Incomplete
    min_num_samples: int
    max_num_samples: Incomplete
    max_errors: Incomplete
    num_candidate_sets: Incomplete
    max_labeled_demos: Incomplete
    def __init__(self, metric, teacher_settings=None, max_bootstrapped_demos: int = 4, max_labeled_demos: int = 16, max_rounds: int = 1, num_candidate_programs: int = 16, num_threads=None, max_errors=None, stop_at_score=None, metric_threshold=None) -> None: ...
    trainset: Incomplete
    valset: Incomplete
    def compile(self, student, *, teacher=None, trainset, valset=None, restrict=None, labeled_sample: bool = True): ...
