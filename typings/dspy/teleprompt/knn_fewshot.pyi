from typing import Any

from _typeshed import Incomplete
from dspy.clients import Embedder as Embedder
from dspy.predict.knn import KNN as KNN
from dspy.primitives import Example as Example
from dspy.teleprompt import BootstrapFewShot as BootstrapFewShot
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

class KNNFewShot(Teleprompter):
    KNN: Incomplete
    few_shot_bootstrap_args: Incomplete
    def __init__(self, k: int, trainset: list[Example], vectorizer: Embedder, **few_shot_bootstrap_args: dict[str, Any]) -> None: ...
    def compile(self, student, *, teacher=None): ...
