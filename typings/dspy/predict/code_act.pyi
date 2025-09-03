from collections.abc import Callable

from _typeshed import Incomplete
from dspy.adapters.types.tool import Tool as Tool
from dspy.predict.program_of_thought import ProgramOfThought as ProgramOfThought
from dspy.predict.react import ReAct as ReAct
from dspy.primitives.python_interpreter import PythonInterpreter as PythonInterpreter
from dspy.signatures.signature import Signature as Signature
from dspy.signatures.signature import ensure_signature as ensure_signature

logger: Incomplete

class CodeAct(ReAct, ProgramOfThought):
    signature: Incomplete
    max_iters: Incomplete
    history: Incomplete
    tools: dict[str, Tool]
    codeact: Incomplete
    extractor: Incomplete
    interpreter: Incomplete
    def __init__(self, signature: str | type[Signature], tools: list[Callable], max_iters: int = 5, interpreter: PythonInterpreter | None = None) -> None: ...
    def forward(self, **kwargs): ...
