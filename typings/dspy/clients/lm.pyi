from typing import Any, Literal, Unpack

from _typeshed import Incomplete
from dspy.clients.cache import request_cache as request_cache
from dspy.clients.openai import OpenAIProvider as OpenAIProvider
from dspy.clients.provider import Provider as Provider
from dspy.clients.provider import ReinforceJob as ReinforceJob
from dspy.clients.provider import TrainingJob as TrainingJob
from dspy.clients.utils_finetune import TrainDataFormat as TrainDataFormat
from dspy.dsp.utils.settings import settings as settings
from dspy.utils.callback import BaseCallback as BaseCallback
from litellm.types.utils import ModelResponse  # Use litellm's ModelResponse

from .base_lm import BaseLM as BaseLM
from .base_lm import LMParams, Message

logger: Incomplete

class LM(BaseLM):
    model: Incomplete
    model_type: Incomplete
    cache: Incomplete
    cache_in_memory: Incomplete
    provider: Incomplete
    callbacks: Incomplete
    history: Incomplete
    num_retries: Incomplete
    finetuning_model: Incomplete
    launch_kwargs: Incomplete
    train_kwargs: Incomplete
    kwargs: Incomplete
    def __init__(self, model: str, model_type: Literal["chat", "text"] = "chat", temperature: float = 0.0, max_tokens: int = 4000, cache: bool = True, cache_in_memory: bool = True, callbacks: list[BaseCallback] | None = None, num_retries: int = 3, provider: Provider | None = None, finetuning_model: str | None = None, launch_kwargs: dict[str, Any] | None = None, train_kwargs: dict[str, Any] | None = None, **kwargs: Any) -> None: ...
    def forward(
        self,
        prompt: str | None = None,
        messages: tuple[Message, ...] | None = None,
        **kwargs: Unpack[LMParams],
    ) -> ModelResponse: ...
    async def aforward(
        self,
        prompt: str | None = None,
        messages: tuple[Message, ...] | None = None,
        **kwargs: Unpack[LMParams],
    ) -> ModelResponse: ...
    def launch(self, launch_kwargs: dict[str, Any] | None = None): ...
    def kill(self, launch_kwargs: dict[str, Any] | None = None): ...
    def finetune(self, train_data: list[dict[str, Any]], train_data_format: TrainDataFormat | None, train_kwargs: dict[str, Any] | None = None) -> TrainingJob: ...
    def reinforce(self, train_kwargs) -> ReinforceJob: ...
    def infer_provider(self) -> Provider: ...
    def dump_state(self): ...

def litellm_completion(request: dict[str, Any], num_retries: int, cache: dict[str, Any] | None = None): ...
def litellm_text_completion(request: dict[str, Any], num_retries: int, cache: dict[str, Any] | None = None): ...
async def alitellm_completion(request: dict[str, Any], num_retries: int, cache: dict[str, Any] | None = None): ...
async def alitellm_text_completion(request: dict[str, Any], num_retries: int, cache: dict[str, Any] | None = None): ...
