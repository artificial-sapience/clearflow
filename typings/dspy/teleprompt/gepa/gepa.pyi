from dataclasses import dataclass
from typing import Any, Literal, Protocol

from _typeshed import Incomplete
from dspy.clients.lm import LM as LM
from dspy.primitives import Example as Example
from dspy.primitives import Module as Module
from dspy.primitives import Prediction as Prediction
from dspy.teleprompt.gepa.gepa_utils import DspyAdapter as DspyAdapter
from dspy.teleprompt.gepa.gepa_utils import DSPyTrace as DSPyTrace
from dspy.teleprompt.gepa.gepa_utils import PredictorFeedbackFn as PredictorFeedbackFn
from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback as ScoreWithFeedback
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter
from gepa import GEPAResult as GEPAResult

logger: Incomplete
AUTO_RUN_SETTINGS: Incomplete

class GEPAFeedbackMetric(Protocol):
    def __call__(gold: Example, pred: Prediction, trace: DSPyTrace | None, pred_name: str | None, pred_trace: DSPyTrace | None) -> float | ScoreWithFeedback: ...

@dataclass(frozen=True)
class DspyGEPAResult:
    candidates: list[Module]
    parents: list[list[int | None]]
    val_aggregate_scores: list[float]
    val_subscores: list[list[float]]
    per_val_instance_best_candidates: list[set[int]]
    discovery_eval_counts: list[int]
    best_outputs_valset: list[list[tuple[int, list[Prediction]]]] | None = ...
    total_metric_calls: int | None = ...
    num_full_val_evals: int | None = ...
    log_dir: str | None = ...
    seed: int | None = ...
    @property
    def best_idx(self) -> int: ...
    @property
    def best_candidate(self) -> dict[str, str]: ...
    @property
    def highest_score_achieved_per_val_task(self) -> list[float]: ...
    def to_dict(self) -> dict[str, Any]: ...
    @staticmethod
    def from_gepa_result(gepa_result: GEPAResult, adapter: DspyAdapter) -> DspyGEPAResult: ...

class GEPA(Teleprompter):
    metric_fn: Incomplete
    auto: Incomplete
    max_full_evals: Incomplete
    max_metric_calls: Incomplete
    reflection_minibatch_size: Incomplete
    candidate_selection_strategy: Incomplete
    reflection_lm: Incomplete
    skip_perfect_score: Incomplete
    add_format_failure_as_feedback: Incomplete
    use_merge: Incomplete
    max_merge_invocations: Incomplete
    num_threads: Incomplete
    failure_score: Incomplete
    perfect_score: Incomplete
    log_dir: Incomplete
    track_stats: Incomplete
    use_wandb: Incomplete
    wandb_api_key: Incomplete
    wandb_init_kwargs: Incomplete
    track_best_outputs: Incomplete
    seed: Incomplete
    def __init__(self, metric: GEPAFeedbackMetric, *, auto: Literal["light", "medium", "heavy"] | None = None, max_full_evals: int | None = None, max_metric_calls: int | None = None, reflection_minibatch_size: int = 3, candidate_selection_strategy: Literal["pareto", "current_best"] = "pareto", reflection_lm: LM | None = None, skip_perfect_score: bool = True, add_format_failure_as_feedback: bool = False, use_merge: bool = True, max_merge_invocations: int | None = 5, num_threads: int | None = None, failure_score: float = 0.0, perfect_score: float = 1.0, log_dir: str = None, track_stats: bool = False, use_wandb: bool = False, wandb_api_key: str | None = None, wandb_init_kwargs: dict[str, Any] | None = None, track_best_outputs: bool = False, seed: int | None = 0) -> None: ...
    def auto_budget(self, num_preds, num_candidates, valset_size: int, minibatch_size: int = 35, full_eval_steps: int = 5) -> int: ...
    def compile(self, student: Module, *, trainset: list[Example], teacher: Module | None = None, valset: list[Example] | None = None) -> Module: ...
