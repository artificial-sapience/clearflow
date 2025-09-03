from _typeshed import Incomplete
from dspy import Example as Example
from dspy.dsp.utils import dotdict as dotdict

class Dataset:
    train_size: Incomplete
    train_seed: Incomplete
    dev_size: Incomplete
    dev_seed: Incomplete
    test_size: Incomplete
    test_seed: Incomplete
    input_keys: Incomplete
    do_shuffle: bool
    name: Incomplete
    def __init__(self, train_seed: int = 0, train_size=None, eval_seed: int = 0, dev_size=None, test_size=None, input_keys=None) -> None: ...
    def reset_seeds(self, train_seed=None, train_size=None, eval_seed=None, dev_size=None, test_size=None) -> None: ...
    @property
    def train(self): ...
    @property
    def dev(self): ...
    @property
    def test(self): ...
    @classmethod
    def prepare_by_seed(cls, train_seeds=None, train_size: int = 16, dev_size: int = 1000, divide_eval_per_seed: bool = True, eval_seed: int = 2023, **kwargs): ...
