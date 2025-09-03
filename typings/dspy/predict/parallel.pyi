from typing import Any

from _typeshed import Incomplete
from dspy.dsp.utils.settings import settings as settings
from dspy.primitives.example import Example as Example
from dspy.utils.parallelizer import ParallelExecutor as ParallelExecutor

class Parallel:
    num_threads: Incomplete
    max_errors: Incomplete
    access_examples: Incomplete
    return_failed_examples: Incomplete
    provide_traceback: Incomplete
    disable_progress_bar: Incomplete
    error_count: int
    error_lock: Incomplete
    cancel_jobs: Incomplete
    failed_examples: Incomplete
    exceptions: Incomplete
    def __init__(self, num_threads: int | None = None, max_errors: int | None = None, access_examples: bool = True, return_failed_examples: bool = False, provide_traceback: bool | None = None, disable_progress_bar: bool = False) -> None: ...
    def forward(self, exec_pairs: list[tuple[Any, Example]], num_threads: int | None = None) -> list[Any]: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
