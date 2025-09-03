import dspy
from _typeshed import Incomplete
from dspy.predict.avatar.models import Action as Action
from dspy.predict.avatar.models import ActionOutput as ActionOutput
from dspy.predict.avatar.models import Tool as Tool
from dspy.predict.avatar.signatures import Actor as Actor
from dspy.signatures.signature import ensure_signature as ensure_signature
from pydantic.fields import FieldInfo as FieldInfo

def get_number_with_suffix(number: int) -> str: ...

class Avatar(dspy.Module):
    signature: Incomplete
    input_fields: Incomplete
    output_fields: Incomplete
    finish_tool: Incomplete
    tools: Incomplete
    actor_signature: Incomplete
    verbose: Incomplete
    max_iters: Incomplete
    actor: Incomplete
    actor_clone: Incomplete
    def __init__(self, signature, tools, max_iters: int = 3, verbose: bool = False) -> None: ...
    def forward(self, **kwargs): ...
