import dspy
from _typeshed import Incomplete
from dspy.propose.utils import strip_prefix as strip_prefix

class ObservationSummarizer(dspy.Signature):
    observations: Incomplete
    summary: Incomplete

class DatasetDescriptor(dspy.Signature):
    examples: Incomplete
    observations: Incomplete

class DatasetDescriptorWithPriorObservations(dspy.Signature):
    examples: Incomplete
    prior_observations: Incomplete
    observations: Incomplete

def order_input_keys_in_string(unordered_repr): ...
def create_dataset_summary(trainset, view_data_batch_size, prompt_model, log_file=None, verbose: bool = False): ...
