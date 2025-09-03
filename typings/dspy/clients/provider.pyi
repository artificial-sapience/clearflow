import abc
from abc import abstractmethod
from concurrent.futures import Future
from threading import Thread
from typing import Any

from _typeshed import Incomplete
from dspy.clients.lm import LM as LM
from dspy.clients.utils_finetune import TrainDataFormat as TrainDataFormat

class TrainingJob(Future, metaclass=abc.ABCMeta):
    thread: Incomplete
    model: Incomplete
    train_data: Incomplete
    train_data_format: Incomplete
    train_kwargs: Incomplete
    def __init__(self, thread: Thread | None = None, model: str | None = None, train_data: list[dict[str, Any]] | None = None, train_data_format: TrainDataFormat | None = None, train_kwargs: dict[str, Any] | None = None) -> None: ...
    def cancel(self) -> None: ...
    @abstractmethod
    def status(self): ...

class ReinforceJob(abc.ABC):
    lm: Incomplete
    train_kwargs: Incomplete
    checkpoints: Incomplete
    last_checkpoint: Incomplete
    def __init__(self, lm: LM, train_kwargs: dict[str, Any] | None = None) -> None: ...
    @abstractmethod
    def initialize(self): ...
    @abstractmethod
    def step(self, train_data: list[dict[str, Any]], train_data_format: TrainDataFormat | str | None = None): ...
    @abstractmethod
    def terminate(self): ...
    @abstractmethod
    def update_model(self): ...
    @abstractmethod
    def save_checkpoint(self, checkpoint_name: str): ...
    def cancel(self) -> None: ...
    def status(self) -> None: ...

class Provider:
    finetunable: bool
    reinforceable: bool
    TrainingJob: Incomplete
    ReinforceJob: Incomplete
    def __init__(self) -> None: ...
    @staticmethod
    def is_provider_model(model: str) -> bool: ...
    @staticmethod
    def launch(lm: LM, launch_kwargs: dict[str, Any] | None = None): ...
    @staticmethod
    def kill(lm: LM, launch_kwargs: dict[str, Any] | None = None): ...
    @staticmethod
    def finetune(job: TrainingJob, model: str, train_data: list[dict[str, Any]], train_data_format: TrainDataFormat | str | None, train_kwargs: dict[str, Any] | None = None) -> str: ...
