import dspy
from _typeshed import Incomplete
from dspy.evaluate.evaluate import Evaluate as Evaluate
from dspy.signatures import Signature as Signature
from dspy.teleprompt.teleprompt import Teleprompter as Teleprompter

logger: Incomplete

class BasicGenerateInstruction(Signature):
    basic_instruction: Incomplete
    proposed_instruction: Incomplete
    proposed_prefix_for_output_field: Incomplete

class GenerateInstructionGivenAttempts(dspy.Signature):
    attempted_instructions: Incomplete
    proposed_instruction: Incomplete
    proposed_prefix_for_output_field: Incomplete

class COPRO(Teleprompter):
    metric: Incomplete
    breadth: Incomplete
    depth: Incomplete
    init_temperature: Incomplete
    prompt_model: Incomplete
    track_stats: Incomplete
    def __init__(self, prompt_model=None, metric=None, breadth: int = 10, depth: int = 3, init_temperature: float = 1.4, track_stats: bool = False, **_kwargs) -> None: ...
    def compile(self, student, *, trainset, eval_kwargs): ...
