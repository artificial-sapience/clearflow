from _typeshed import Incomplete
from dspy.clients import Embedder as Embedder
from dspy.primitives import Example as Example

class KNN:
    k: Incomplete
    trainset: Incomplete
    embedding: Incomplete
    trainset_vectors: Incomplete
    def __init__(self, k: int, trainset: list[Example], vectorizer: Embedder) -> None: ...
    def __call__(self, **kwargs) -> list: ...
