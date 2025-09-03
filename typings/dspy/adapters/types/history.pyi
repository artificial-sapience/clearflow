from typing import Any

import pydantic
from _typeshed import Incomplete

class History(pydantic.BaseModel):
    messages: list[dict[str, Any]]
    model_config: Incomplete
