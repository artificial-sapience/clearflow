from enum import Enum
from typing import Any, Literal, TypeAlias, TypedDict

from dspy.adapters.base import Adapter as Adapter
from dspy.utils.caching import DSPY_CACHEDIR as DSPY_CACHEDIR

class TrainingStatus(str, Enum):
    not_started = "not_started"
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"

class TrainDataFormat(str, Enum):
    CHAT = "chat"
    COMPLETION = "completion"
    GRPO_CHAT = "grpo_chat"

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class MessageAssistant(TypedDict):
    role: Literal["assistant"]
    content: str

class GRPOChatData(TypedDict):
    messages: list[Message]
    completion: MessageAssistant
    reward: float
type GRPOGroup = list[GRPOChatData]

def infer_data_format(adapter: Adapter) -> str: ...
def get_finetune_directory() -> str: ...
def write_lines(file_path, data) -> None: ...
def save_data(data: list[dict[str, Any]]) -> str: ...
def validate_data_format(data: list[dict[str, Any]], data_format: TrainDataFormat): ...
def find_data_errors_completion(data_dict: dict[str, str]) -> str | None: ...
def find_data_error_chat(messages: dict[str, Any]) -> str | None: ...
def find_data_error_chat_message(message: dict[str, Any]) -> str | None: ...
