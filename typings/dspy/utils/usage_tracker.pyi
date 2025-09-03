from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from _typeshed import Incomplete
from dspy.dsp.utils.settings import settings as settings

class UsageTracker:
    usage_data: Incomplete
    def __init__(self) -> None: ...
    def add_usage(self, lm: str, usage_entry: dict[str, Any]) -> None: ...
    def get_total_tokens(self) -> dict[str, dict[str, Any]]: ...

@contextmanager
def track_usage() -> Generator[UsageTracker]: ...
