from typing import Any

from _typeshed import Incomplete
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.adapters.json_adapter import JSONAdapter as JSONAdapter
from dspy.adapters.xml_adapter import XMLAdapter as XMLAdapter
from dspy.dsp.utils.settings import settings as settings
from dspy.primitives.module import Module as Module
from dspy.streaming.messages import StreamResponse as StreamResponse
from litellm import ModelResponseStream as ModelResponseStream

ADAPTER_SUPPORT_STREAMING: Incomplete

class StreamListener:
    signature_field_name: Incomplete
    predict: Incomplete
    predict_name: Incomplete
    field_start_queue: Incomplete
    field_end_queue: Incomplete
    stream_start: bool
    stream_end: bool
    cache_hit: bool
    allow_reuse: Incomplete
    adapter_identifiers: Incomplete
    def __init__(self, signature_field_name: str, predict: Any = None, predict_name: str | None = None, allow_reuse: bool = False) -> None: ...
    def receive(self, chunk: ModelResponseStream): ...
    def flush(self) -> str: ...

def find_predictor_for_stream_listeners(program: Module, stream_listeners: list[StreamListener]): ...
