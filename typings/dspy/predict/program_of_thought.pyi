from _typeshed import Incomplete
from dspy.primitives.module import Module as Module
from dspy.primitives.python_interpreter import PythonInterpreter as PythonInterpreter
from dspy.signatures.signature import Signature as Signature
from dspy.signatures.signature import ensure_signature as ensure_signature

logger: Incomplete

class ProgramOfThought(Module):
    signature: Incomplete
    max_iters: Incomplete
    input_fields: Incomplete
    output_fields: Incomplete
    code_generate: Incomplete
    code_regenerate: Incomplete
    generate_answer: Incomplete
    interpreter: Incomplete
    def __init__(self, signature: str | type[Signature], max_iters: int = 3, interpreter: PythonInterpreter | None = None) -> None: ...
    def forward(self, **kwargs): ...
