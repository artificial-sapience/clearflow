from _typeshed import Incomplete

class GSM8K:
    do_shuffle: bool
    train: Incomplete
    dev: Incomplete
    test: Incomplete
    def __init__(self) -> None: ...

def parse_integer_answer(answer, only_first_line: bool = True): ...
def gsm8k_metric(gold, pred, trace=None): ...
