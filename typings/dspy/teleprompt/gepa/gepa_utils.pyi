import logging
import random
from collections.abc import Callable
from typing import Any, Protocol, TypeAlias

from _typeshed import Incomplete
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.adapters.types import History as History
from dspy.evaluate import Evaluate as Evaluate
from dspy.primitives import Example as Example
from dspy.primitives import Prediction as Prediction
from dspy.teleprompt.bootstrap_finetune import TraceData as TraceData
from gepa import GEPAAdapter

class LoggerAdapter:
    logger: Incomplete
    def __init__(self, logger: logging.Logger) -> None: ...
    def log(self, x: str): ...
type DSPyTrace = list[tuple[Any, dict[str, Any], Prediction]]

class ScoreWithFeedback(Prediction):
    score: float
    feedback: str

class PredictorFeedbackFn(Protocol):
    def __call__(predictor_output: dict[str, Any], predictor_inputs: dict[str, Any], module_inputs: Example, module_outputs: Prediction, captured_trace: DSPyTrace) -> ScoreWithFeedback: ...

class DspyAdapter(GEPAAdapter[Example, TraceData, Prediction]):
    student: Incomplete
    metric_fn: Incomplete
    feedback_map: Incomplete
    failure_score: Incomplete
    num_threads: Incomplete
    add_format_failure_as_feedback: Incomplete
    rng: Incomplete
    named_predictors: Incomplete
    def __init__(self, student_module, metric_fn: Callable, feedback_map: dict[str, Callable], failure_score: float = 0.0, num_threads: int | None = None, add_format_failure_as_feedback: bool = False, rng: random.Random | None = None) -> None: ...
    def build_program(self, candidate: dict[str, str]): ...
    def evaluate(self, batch, candidate, capture_traces: bool = False): ...
    def make_reflective_dataset(self, candidate, eval_batch, components_to_update): ...
