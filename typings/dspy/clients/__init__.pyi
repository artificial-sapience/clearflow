from dspy.clients.base_lm import BaseLM as BaseLM
from dspy.clients.base_lm import inspect_history as inspect_history
from dspy.clients.embedding import Embedder as Embedder
from dspy.clients.lm import LM as LM
from dspy.clients.provider import Provider as Provider
from dspy.clients.provider import TrainingJob as TrainingJob

__all__ = ["LM", "BaseLM", "Embedder", "Provider", "TrainingJob", "configure_cache", "disable_litellm_logging", "enable_litellm_logging", "inspect_history"]

def configure_cache(enable_disk_cache: bool | None = True, enable_memory_cache: bool | None = True, disk_cache_dir: str | None = ..., disk_size_limit_bytes: int | None = ..., memory_max_entries: int | None = 1000000, enable_litellm_cache: bool = False): ...
def enable_litellm_logging() -> None: ...
def disable_litellm_logging() -> None: ...
