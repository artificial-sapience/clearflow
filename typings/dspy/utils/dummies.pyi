import numpy as np
from _typeshed import Incomplete
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.adapters.chat_adapter import FieldInfoWithName as FieldInfoWithName
from dspy.adapters.chat_adapter import field_header_pattern as field_header_pattern
from dspy.clients.lm import LM as LM
from dspy.dsp.utils.utils import dotdict as dotdict
from dspy.signatures.field import OutputField as OutputField
from dspy.utils.callback import with_callbacks as with_callbacks

class DummyLM(LM):
    answers: Incomplete
    follow_examples: Incomplete
    def __init__(self, answers: list[dict[str, str]] | dict[str, dict[str, str]], follow_examples: bool = False) -> None: ...
    @with_callbacks
    def __call__(self, prompt=None, messages=None, **kwargs): ...
    async def acall(self, prompt=None, messages=None, **kwargs): ...
    def get_convo(self, index): ...

def dummy_rm(passages=()) -> callable: ...

class DummyVectorizer:
    max_length: Incomplete
    n_gram: Incomplete
    P: Incomplete
    coeffs: Incomplete
    def __init__(self, max_length: int = 100, n_gram: int = 2) -> None: ...
    def __call__(self, texts: list[str]) -> np.ndarray: ...
