from collections.abc import Callable
from typing import Any

import numpy as np
from _typeshed import Incomplete
from dspy.clients.cache import request_cache as request_cache

class Embedder:
    model: Incomplete
    batch_size: Incomplete
    caching: Incomplete
    default_kwargs: Incomplete
    def __init__(self, model: str | Callable, batch_size: int = 200, caching: bool = True, **kwargs: dict[str, Any]) -> None: ...
    def __call__(self, inputs: str | list[str], batch_size: int | None = None, caching: bool | None = None, **kwargs: dict[str, Any]) -> np.ndarray: ...
    async def acall(self, inputs, batch_size=None, caching=None, **kwargs): ...
