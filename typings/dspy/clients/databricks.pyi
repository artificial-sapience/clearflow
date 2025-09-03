from typing import Any

from _typeshed import Incomplete
from dspy.clients.provider import Provider as Provider
from dspy.clients.provider import TrainingJob as TrainingJob
from dspy.clients.utils_finetune import TrainDataFormat as TrainDataFormat
from dspy.clients.utils_finetune import get_finetune_directory as get_finetune_directory

logger: Incomplete

class TrainingJobDatabricks(TrainingJob):
    finetuning_run: Incomplete
    launch_started: bool
    launch_completed: bool
    endpoint_name: Incomplete
    def __init__(self, finetuning_run=None, *args, **kwargs) -> None: ...
    def status(self): ...

class DatabricksProvider(Provider):
    finetunable: bool
    TrainingJob = TrainingJobDatabricks
    @staticmethod
    def is_provider_model(model: str) -> bool: ...
    @staticmethod
    def deploy_finetuned_model(model: str, data_format: TrainDataFormat | None = None, databricks_host: str | None = None, databricks_token: str | None = None, deploy_timeout: int = 900): ...
    @staticmethod
    def finetune(job: TrainingJobDatabricks, model: str, train_data: list[dict[str, Any]], train_data_format: TrainDataFormat | str | None = "chat", train_kwargs: dict[str, Any] | None = None) -> str: ...
    @staticmethod
    def upload_data(train_data: list[dict[str, Any]], databricks_unity_catalog_path: str, data_format: TrainDataFormat): ...
