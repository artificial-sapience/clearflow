from _typeshed import Incomplete
from dspy.datasets.dataset import Dataset as Dataset

all_colors: Incomplete

class Colors(Dataset):
    sort_by_suffix: Incomplete
    def __init__(self, sort_by_suffix: bool = True, *args, **kwargs) -> None: ...
    def sorted_by_suffix(self, colors): ...
