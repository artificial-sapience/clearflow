from dspy.datasets.dataset import Dataset as Dataset

class HotPotQA(Dataset):
    def __init__(self, *args, only_hard_examples: bool = True, keep_details: str = "dev_titles", unofficial_dev: bool = True, **kwargs) -> None: ...
