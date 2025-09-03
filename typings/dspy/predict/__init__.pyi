from dspy.predict.aggregation import majority as majority
from dspy.predict.best_of_n import BestOfN as BestOfN
from dspy.predict.chain_of_thought import ChainOfThought as ChainOfThought
from dspy.predict.code_act import CodeAct as CodeAct
from dspy.predict.knn import KNN as KNN
from dspy.predict.multi_chain_comparison import (
    MultiChainComparison as MultiChainComparison,
)
from dspy.predict.parallel import Parallel as Parallel
from dspy.predict.predict import Predict as Predict
from dspy.predict.program_of_thought import ProgramOfThought as ProgramOfThought
from dspy.predict.react import ReAct as ReAct
from dspy.predict.react import Tool as Tool
from dspy.predict.refine import Refine as Refine

__all__ = ["KNN", "BestOfN", "ChainOfThought", "CodeAct", "MultiChainComparison", "Parallel", "Predict", "ProgramOfThought", "ReAct", "Refine", "Tool", "majority"]
