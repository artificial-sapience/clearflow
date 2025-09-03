from collections.abc import Callable
from typing import Any

import dspy
import pandas as pd
from _typeshed import Incomplete
from dspy.primitives.prediction import Prediction as Prediction
from dspy.utils.callback import with_callbacks as with_callbacks
from dspy.utils.parallelizer import ParallelExecutor as ParallelExecutor

logger: Incomplete

class EvaluationResult(Prediction):
    def __init__(self, score: float, results: list[tuple[dspy.Example, dspy.Example, Any]]) -> None: ...

class Evaluate:
    devset: Incomplete
    metric: Incomplete
    num_threads: Incomplete
    display_progress: Incomplete
    display_table: Incomplete
    max_errors: Incomplete
    provide_traceback: Incomplete
    failure_score: Incomplete
    def __init__(self, *, devset: list[dspy.Example], metric: Callable | None = None, num_threads: int | None = None, display_progress: bool = False, display_table: bool | int = False, max_errors: int | None = None, provide_traceback: bool | None = None, failure_score: float = 0.0, **kwargs) -> None: ...
    @with_callbacks
    def __call__(self, program: dspy.Module, metric: Callable | None = None, devset: list[dspy.Example] | None = None, num_threads: int | None = None, display_progress: bool | None = None, display_table: bool | int | None = None, callback_metadata: dict[str, Any] | None = None) -> EvaluationResult: ...

def prediction_is_dictlike(prediction): ...
def merge_dicts(d1, d2) -> dict: ...
def truncate_cell(content) -> str: ...
def stylize_metric_name(df: pd.DataFrame, metric_name: str) -> pd.DataFrame: ...
def display_dataframe(df: pd.DataFrame): ...
def configure_dataframe_for_ipython_notebook_display(df: pd.DataFrame) -> pd.DataFrame: ...
def is_in_ipython_notebook_environment(): ...
