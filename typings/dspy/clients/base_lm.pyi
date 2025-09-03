from collections.abc import Coroutine
from typing import Any, Protocol, TypedDict, Unpack

from _typeshed import Incomplete
from dspy.dsp.utils import settings as settings
from dspy.utils.callback import with_callbacks as with_callbacks
from dspy.utils.inspect_history import pretty_print_history as pretty_print_history

MAX_HISTORY_SIZE: int
GLOBAL_HISTORY: Incomplete

# OpenAI-compatible types based on API documentation
class Message(TypedDict):
    """OpenAI message format."""

    role: str
    content: str

class MessageChoice(Protocol):
    """OpenAI choice message."""

    content: str
    tool_calls: None  # Simplified for our use case

class Choice(Protocol):
    """OpenAI completion choice."""

    message: MessageChoice
    finish_reason: str | None

class Usage(TypedDict):
    """OpenAI token usage."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class CompletionResponse(Protocol):
    """OpenAI-compatible completion response format.
    
    As per DSPy documentation, responses should match:
    https://platform.openai.com/docs/api-reference/responses/object
    
    Note: This is a Protocol to allow duck typing with litellm.ModelResponse
    """

    choices: list[Choice]  # DSPy/litellm requires list type
    usage: Usage
    model: str

# Known LM parameters based on OpenAI API
class LMParams(TypedDict, total=False):
    """Known parameters for language model calls."""

    n: int
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop: tuple[str, ...] | None

class BaseLM:
    model: Incomplete
    model_type: Incomplete
    cache: Incomplete
    kwargs: Incomplete
    history: Incomplete
    def __init__(self, model, model_type: str = "chat", temperature: float = 0.0, max_tokens: int = 1000, cache: bool = True, **kwargs) -> None: ...
    @with_callbacks
    def __call__(self, prompt=None, messages=None, **kwargs): ...
    @with_callbacks
    async def acall(self, prompt=None, messages=None, **kwargs): ...
    def forward(
        self,
        prompt: str | None = ...,
        messages: tuple[Message, ...] | None = ...,
        **kwargs: Unpack[LMParams]
    ) -> Any: ...  # Returns Any to allow subclasses to return ModelResponse or CompletionResponse
    async def aforward(
        self,
        prompt: str | None = ...,
        messages: tuple[Message, ...] | None = ...,
        **kwargs: Unpack[LMParams]
    ) -> Any: ...  # Returns Any to allow subclasses to return ModelResponse or CompletionResponse
    def copy(self, **kwargs): ...
    def inspect_history(self, n: int = 1): ...
    def update_history(self, entry) -> None: ...

def inspect_history(n: int = 1): ...
