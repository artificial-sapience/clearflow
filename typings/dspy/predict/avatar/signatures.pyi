import dspy
from dspy.predict.avatar.models import Action as Action

class Actor(dspy.Signature):
    goal: str
    tools: list[str]
    action_1: Action
