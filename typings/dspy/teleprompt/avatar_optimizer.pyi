from collections.abc import Callable

import dspy
from _typeshed import Incomplete
from dspy.predict.avatar import ActionOutput as ActionOutput
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter
from pydantic import BaseModel

DEFAULT_MAX_EXAMPLES: int

class EvalResult(BaseModel):
    example: dict
    score: float
    actions: list[ActionOutput] | None

class Comparator(dspy.Signature):
    instruction: str
    actions: list[str]
    pos_input_with_metrics: list[EvalResult]
    neg_input_with_metrics: list[EvalResult]
    feedback: str

class FeedbackBasedInstruction(dspy.Signature):
    previous_instruction: str
    feedback: str
    new_instruction: str

class AvatarOptimizer(Teleprompter):
    metric: Incomplete
    optimize_for: Incomplete
    max_iters: Incomplete
    lower_bound: Incomplete
    upper_bound: Incomplete
    max_positive_inputs: Incomplete
    max_negative_inputs: Incomplete
    comparator: Incomplete
    feedback_instruction: Incomplete
    def __init__(self, metric: Callable, max_iters: int = 10, lower_bound: int = 0, upper_bound: int = 1, max_positive_inputs: int | None = None, max_negative_inputs: int | None = None, optimize_for: str = "max") -> None: ...
    def process_example(self, actor, example, return_outputs): ...
    def thread_safe_evaluator(self, devset, actor, return_outputs: bool = False, num_threads=None): ...
    def compile(self, student, *, trainset): ...
