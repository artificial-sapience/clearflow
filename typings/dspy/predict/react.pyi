from collections.abc import Callable

from _typeshed import Incomplete
from dspy.adapters.types.tool import Tool as Tool
from dspy.primitives.module import Module as Module
from dspy.signatures.signature import Signature as Signature
from dspy.signatures.signature import ensure_signature as ensure_signature

logger: Incomplete

class ReAct(Module):
    signature: Incomplete
    max_iters: Incomplete
    tools: Incomplete
    react: Incomplete
    extract: Incomplete
    def __init__(self, signature: type[Signature], tools: list[Callable], max_iters: int = 10) -> None: ...
    def forward(self, **input_args): ...
    async def aforward(self, **input_args): ...
    def truncate_trajectory(self, trajectory): ...
