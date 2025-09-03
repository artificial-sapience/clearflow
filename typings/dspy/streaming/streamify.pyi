from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from typing import Any

from _typeshed import Incomplete
from anyio.streams.memory import MemoryObjectSendStream as MemoryObjectSendStream
from dspy.dsp.utils.settings import settings as settings
from dspy.primitives.module import Module as Module
from dspy.primitives.prediction import Prediction as Prediction
from dspy.streaming.messages import StatusMessage as StatusMessage
from dspy.streaming.messages import StatusMessageProvider as StatusMessageProvider
from dspy.streaming.messages import StatusStreamingCallback as StatusStreamingCallback
from dspy.streaming.streaming_listener import StreamListener as StreamListener
from dspy.streaming.streaming_listener import (
    find_predictor_for_stream_listeners as find_predictor_for_stream_listeners,
)
from dspy.utils.asyncify import asyncify as asyncify

logger: Incomplete

def streamify(program: Module, status_message_provider: StatusMessageProvider | None = None, stream_listeners: list[StreamListener] | None = None, include_final_prediction_in_output_stream: bool = True, is_async_program: bool = False, async_streaming: bool = True) -> Callable[[Any, Any], Awaitable[Any]]: ...
def apply_sync_streaming(async_generator: AsyncGenerator) -> Generator: ...
async def streaming_response(streamer: AsyncGenerator) -> AsyncGenerator: ...
