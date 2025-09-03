from _typeshed import Incomplete
from dspy.predict.chain_of_thought import ChainOfThought as ChainOfThought
from dspy.primitives import Module as Module
from dspy.signatures import InputField as InputField
from dspy.signatures import OutputField as OutputField
from dspy.signatures import Signature as Signature

class SemanticRecallPrecision(Signature):
    question: str
    ground_truth: str
    system_response: str
    recall: float
    precision: float

class DecompositionalSemanticRecallPrecision(Signature):
    question: str
    ground_truth: str
    system_response: str
    ground_truth_key_ideas: str
    system_response_key_ideas: str
    discussion: str
    recall: float
    precision: float

def f1_score(precision, recall): ...

class SemanticF1(Module):
    threshold: Incomplete
    module: Incomplete
    def __init__(self, threshold: float = 0.66, decompositional: bool = False) -> None: ...
    def forward(self, example, pred, trace=None): ...

class AnswerCompleteness(Signature):
    question: str
    ground_truth: str
    system_response: str
    ground_truth_key_ideas: str
    system_response_key_ideas: str
    discussion: str
    completeness: float

class AnswerGroundedness(Signature):
    question: str
    retrieved_context: str
    system_response: str
    system_response_claims: str
    discussion: str
    groundedness: float

class CompleteAndGrounded(Module):
    threshold: Incomplete
    completeness_module: Incomplete
    groundedness_module: Incomplete
    def __init__(self, threshold: float = 0.66) -> None: ...
    def forward(self, example, pred, trace=None): ...
