from typing import Any

from _typeshed import Incomplete
from dspy.utils.unbatchify import Unbatchify as Unbatchify

class Embeddings:
    embedder: Incomplete
    k: Incomplete
    corpus: Incomplete
    normalize: Incomplete
    corpus_embeddings: Incomplete
    index: Incomplete
    search_fn: Incomplete
    def __init__(self, corpus: list[str], embedder, k: int = 5, callbacks: list[Any] | None = None, cache: bool = False, brute_force_threshold: int = 20000, normalize: bool = True) -> None: ...
    def __call__(self, query: str): ...
    def forward(self, query: str): ...
