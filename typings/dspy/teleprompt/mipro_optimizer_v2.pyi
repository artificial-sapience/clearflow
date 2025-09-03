from collections.abc import Callable
from typing import Any, Literal

from _typeshed import Incomplete
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.propose import GroundedProposer as GroundedProposer
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter
from dspy.teleprompt.utils import create_minibatch as create_minibatch
from dspy.teleprompt.utils import (
    create_n_fewshot_demo_sets as create_n_fewshot_demo_sets,
)
from dspy.teleprompt.utils import eval_candidate_program as eval_candidate_program
from dspy.teleprompt.utils import (
    get_program_with_highest_avg_score as get_program_with_highest_avg_score,
)
from dspy.teleprompt.utils import get_signature as get_signature
from dspy.teleprompt.utils import print_full_program as print_full_program
from dspy.teleprompt.utils import save_candidate_program as save_candidate_program
from dspy.teleprompt.utils import set_signature as set_signature

logger: Incomplete
BOOTSTRAPPED_FEWSHOT_EXAMPLES_IN_CONTEXT: int
LABELED_FEWSHOT_EXAMPLES_IN_CONTEXT: int
MIN_MINIBATCH_SIZE: int
AUTO_RUN_SETTINGS: Incomplete
YELLOW: str
GREEN: str
BLUE: str
BOLD: str
ENDC: str

class MIPROv2(Teleprompter):
    auto: Incomplete
    num_fewshot_candidates: Incomplete
    num_instruct_candidates: Incomplete
    num_candidates: Incomplete
    metric: Incomplete
    init_temperature: Incomplete
    task_model: Incomplete
    prompt_model: Incomplete
    max_bootstrapped_demos: Incomplete
    max_labeled_demos: Incomplete
    verbose: Incomplete
    track_stats: Incomplete
    log_dir: Incomplete
    teacher_settings: Incomplete
    prompt_model_total_calls: int
    total_calls: int
    num_threads: Incomplete
    max_errors: Incomplete
    metric_threshold: Incomplete
    seed: Incomplete
    rng: Incomplete
    def __init__(self, metric: Callable, prompt_model: Any | None = None, task_model: Any | None = None, teacher_settings: dict | None = None, max_bootstrapped_demos: int = 4, max_labeled_demos: int = 4, auto: Literal["light", "medium", "heavy"] | None = "light", num_candidates: int | None = None, num_threads: int | None = None, max_errors: int | None = None, seed: int = 9, init_temperature: float = 0.5, verbose: bool = False, track_stats: bool = True, log_dir: str | None = None, metric_threshold: float | None = None) -> None: ...
    def compile(self, student: Any, *, trainset: list, teacher: Any = None, valset: list | None = None, num_trials: int | None = None, max_bootstrapped_demos: int | None = None, max_labeled_demos: int | None = None, seed: int | None = None, minibatch: bool = True, minibatch_size: int = 35, minibatch_full_eval_steps: int = 5, program_aware_proposer: bool = True, data_aware_proposer: bool = True, view_data_batch_size: int = 10, tip_aware_proposer: bool = True, fewshot_aware_proposer: bool = True, requires_permission_to_run: bool = True, provide_traceback: bool | None = None) -> Any: ...
