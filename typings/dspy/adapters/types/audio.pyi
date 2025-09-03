from typing import Any

from _typeshed import Incomplete
from dspy.adapters.types.base_type import Type as Type

SF_AVAILABLE: bool

class Audio(Type):
    data: str
    audio_format: str
    model_config: Incomplete
    def format(self) -> list[dict[str, Any]]: ...
    @classmethod
    def validate_input(cls, values: Any) -> Any: ...
    @classmethod
    def from_url(cls, url: str) -> Audio: ...
    @classmethod
    def from_file(cls, file_path: str) -> Audio: ...
    @classmethod
    def from_array(cls, array: Any, sampling_rate: int, format: str = "wav") -> Audio: ...

def encode_audio(audio: str | bytes | dict | Audio | Any, sampling_rate: int = 16000, format: str = "wav") -> dict: ...
