from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypedDict

from _typeshed import Incomplete
from dspy.adapters.base import Adapter as Adapter
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.clients.lm import LM as LM
from dspy.clients.utils_finetune import infer_data_format as infer_data_format
from dspy.dsp.utils.settings import settings as settings
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.predict.predict import Predict as Predict
from dspy.primitives.example import Example as Example
from dspy.primitives.module import Module as Module
from dspy.primitives.prediction import Prediction as Prediction
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter
from dspy.utils.exceptions import AdapterParseError as AdapterParseError

logger: Incomplete

class FinetuneTeleprompter(Teleprompter):
    train_kwargs: dict[LM, Any]
    def __init__(self, train_kwargs: dict[str, Any] | dict[LM, dict[str, Any]] | None = None) -> None: ...
    @staticmethod
    def convert_to_lm_dict(arg) -> dict[LM, Any]: ...

class BootstrapFinetune(FinetuneTeleprompter):
    metric: Incomplete
    multitask: Incomplete
    adapter: dict[LM, Adapter]
    exclude_demos: Incomplete
    num_threads: Incomplete
    def __init__(self, metric: Callable | None = None, multitask: bool = True, train_kwargs: dict[str, Any] | dict[LM, dict[str, Any]] | None = None, adapter: Adapter | dict[LM, Adapter] | None = None, exclude_demos: bool = False, num_threads: int | None = None) -> None: ...
    def compile(self, student: Module, trainset: list[Example], teacher: Module | list[Module] | None = None) -> Module: ...
    @staticmethod
    def finetune_lms(finetune_dict) -> dict[Any, LM]: ...

def build_call_data_from_trace(trace: list[dict], pred_ind: int, adapter: Adapter, exclude_demos: bool = False) -> dict[str, list[dict[str, Any]]]: ...

@dataclass
class FailedPrediction:
    completion_text: str
    format_reward: float | None = ...

class TraceData(TypedDict):
    example_ind: int
    example: Example
    prediction: Prediction
    trace: list[tuple[Any, dict[str, Any], Prediction]]
    score: float | None

def bootstrap_trace_data(program: Module, dataset: list[Example], metric: Callable | None = None, num_threads: int | None = None, raise_on_error: bool = True, capture_failed_parses: bool = False, failure_score: float = 0, format_failure_score: float = -1, log_format_failures: bool = False) -> list[TraceData]: ...
def all_predictors_have_lms(program: Module) -> bool: ...
def copy_program_with_lms(program: Module) -> Module: ...
def prepare_student(student: Module) -> Module: ...
def prepare_teacher(student: Module, teacher: Module | None = None) -> Module: ...
def assert_structural_equivalency(program1: object, program2: object): ...
def assert_no_shared_predictor(program1: Module, program2: Module): ...
def get_unique_lms(program: Module) -> list[LM]: ...
def launch_lms(program: Module): ...
def kill_lms(program: Module): ...
