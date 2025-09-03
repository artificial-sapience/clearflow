from _typeshed import Incomplete

logger: Incomplete

class ParallelExecutor:
    num_threads: Incomplete
    max_errors: Incomplete
    disable_progress_bar: Incomplete
    provide_traceback: Incomplete
    compare_results: Incomplete
    timeout: Incomplete
    straggler_limit: Incomplete
    error_count: int
    error_lock: Incomplete
    cancel_jobs: Incomplete
    def __init__(self, num_threads=None, max_errors=None, disable_progress_bar: bool = False, provide_traceback=None, compare_results: bool = False, timeout: int = 120, straggler_limit: int = 3) -> None: ...
    def execute(self, function, data): ...
