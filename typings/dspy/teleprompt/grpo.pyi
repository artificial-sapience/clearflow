from collections.abc import Callable
from typing import Any, Literal

from _typeshed import Incomplete
from dspy.adapters.base import Adapter as Adapter
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.clients.lm import LM as LM
from dspy.clients.utils_finetune import GRPOGroup as GRPOGroup
from dspy.clients.utils_finetune import TrainDataFormat as TrainDataFormat
from dspy.dsp.utils.settings import settings as settings
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.primitives.example import Example as Example
from dspy.primitives.module import Module as Module
from dspy.teleprompt.bootstrap_finetune import FailedPrediction as FailedPrediction
from dspy.teleprompt.bootstrap_finetune import (
    FinetuneTeleprompter as FinetuneTeleprompter,
)
from dspy.teleprompt.bootstrap_finetune import (
    all_predictors_have_lms as all_predictors_have_lms,
)
from dspy.teleprompt.bootstrap_finetune import (
    assert_structural_equivalency as assert_structural_equivalency,
)
from dspy.teleprompt.bootstrap_finetune import (
    bootstrap_trace_data as bootstrap_trace_data,
)

logger: Incomplete

class GRPO(FinetuneTeleprompter):
    metric: Incomplete
    multitask: Incomplete
    adapter: dict[LM, Adapter]
    exclude_demos: Incomplete
    num_threads: Incomplete
    num_train_steps: Incomplete
    rng: Incomplete
    num_dspy_examples_per_grpo_step: Incomplete
    num_rollouts_per_grpo_step: Incomplete
    use_train_as_val: Incomplete
    num_steps_for_val: Incomplete
    report_train_scores: Incomplete
    failure_score: Incomplete
    format_failure_score: Incomplete
    variably_invoked_predictor_grouping_mode: Incomplete
    variably_invoked_predictor_fill_strategy: Incomplete
    shuffled_trainset_ids: Incomplete
    epoch: int
    id_freqs: Incomplete
    def __init__(self, metric: Callable | None = None, multitask: bool = True, train_kwargs: dict[str, Any] | dict[LM, dict[str, Any]] | None = None, adapter: Adapter | dict[LM, Adapter] | None = None, exclude_demos: bool = False, num_threads: int = 6, num_train_steps: int = 100, seed: int = 0, num_dspy_examples_per_grpo_step: int = 1, num_rollouts_per_grpo_step: int = 1, use_train_as_val: bool = False, num_steps_for_val: int = 5, report_train_scores: bool = False, failure_score: float = 0, format_failure_score: float = -1, variably_invoked_predictor_grouping_mode: Literal["truncate", "fill", "ragged"] = "truncate", variably_invoked_predictor_fill_strategy: Literal["randint", "max"] | None = None) -> None: ...
    def validate_trace_data_and_log_issues(self, trace_data: list[list[list[dict[str, Any]]]], subsample_training_dataset: list[Example], num_teachers: int, num_samples_per_input: int, pred_signature_hash_to_ind: dict[int, int]): ...
    def report_validation_metrics(self, student, trainset, valset, logger, step_idx: int = -1) -> None: ...
    def update_shuffled_trainset(self, original_trainset) -> None: ...
    def select_training_sample_and_update_shuffled_trainset(self, original_trainset: list[Example], train_step_idx: int) -> list[Example]: ...
    def compile(self, student: Module, trainset: list[Example], teacher: Module | list[Module] | None = None, valset: list[Example] | None = None, **kwargs) -> Module: ...

def disable_lm_cache(program: Module, lm_cache_dict: dict): ...
def recover_lm_cache(program: Module, lm_cache_dict: dict): ...
