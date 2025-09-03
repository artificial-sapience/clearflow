import dspy
from _typeshed import Incomplete
from dspy.propose.dataset_summary_generator import (
    create_dataset_summary as create_dataset_summary,
)
from dspy.propose.propose_base import Proposer as Proposer
from dspy.propose.utils import create_example_string as create_example_string
from dspy.propose.utils import (
    create_predictor_level_history_string as create_predictor_level_history_string,
)
from dspy.propose.utils import get_dspy_source_code as get_dspy_source_code
from dspy.propose.utils import strip_prefix as strip_prefix
from dspy.teleprompt.utils import get_prompt_model as get_prompt_model
from dspy.teleprompt.utils import get_signature as get_signature

MAX_INSTRUCT_IN_HISTORY: int
TIPS: Incomplete

class DescribeProgram(dspy.Signature):
    program_code: Incomplete
    program_example: Incomplete
    program_description: Incomplete

class DescribeModule(dspy.Signature):
    program_code: Incomplete
    program_example: Incomplete
    program_description: Incomplete
    module: Incomplete
    module_description: Incomplete

def generate_instruction_class(use_dataset_summary: bool = True, program_aware: bool = True, use_task_demos: bool = True, use_instruct_history: bool = True, use_tip: bool = True): ...

class GenerateModuleInstruction(dspy.Module):
    use_dataset_summary: Incomplete
    program_aware: Incomplete
    use_task_demos: Incomplete
    use_instruct_history: Incomplete
    use_tip: Incomplete
    verbose: Incomplete
    program_code_string: Incomplete
    describe_program: Incomplete
    describe_module: Incomplete
    generate_module_instruction: Incomplete
    def __init__(self, program_code_string=None, use_dataset_summary: bool = True, program_aware: bool = False, use_task_demos: bool = True, use_instruct_history: bool = True, use_tip: bool = True, verbose: bool = False) -> None: ...
    def forward(self, demo_candidates, pred_i, demo_set_i, program, previous_instructions, data_summary, num_demos_in_context: int = 3, tip=None): ...

class GroundedProposer(Proposer):
    program_aware: Incomplete
    use_dataset_summary: Incomplete
    use_task_demos: Incomplete
    num_demos_in_context: Incomplete
    use_instruct_history: Incomplete
    use_tip: Incomplete
    set_tip_randomly: Incomplete
    set_history_randomly: Incomplete
    verbose: Incomplete
    rng: Incomplete
    prompt_model: Incomplete
    program_code_string: Incomplete
    data_summary: Incomplete
    def __init__(self, prompt_model, program, trainset, view_data_batch_size: int = 10, use_dataset_summary: bool = True, program_aware: bool = True, use_task_demos: bool = True, num_demos_in_context: int = 3, use_instruct_history: bool = True, use_tip: bool = True, set_tip_randomly: bool = True, set_history_randomly: bool = True, verbose: bool = False, rng=None) -> None: ...
    def propose_instructions_for_program(self, trainset, program, demo_candidates, trial_logs, N, T) -> list[str]: ...
    def propose_instruction_for_predictor(self, program, predictor, pred_i, T, demo_candidates, demo_set_i, trial_logs, tip=None) -> str: ...
