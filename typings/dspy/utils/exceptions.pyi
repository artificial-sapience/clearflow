from _typeshed import Incomplete
from dspy.signatures.signature import Signature as Signature

class AdapterParseError(Exception):
    adapter_name: Incomplete
    signature: Incomplete
    lm_response: Incomplete
    parsed_result: Incomplete
    def __init__(self, adapter_name: str, signature: Signature, lm_response: str, message: str | None = None, parsed_result: str | None = None) -> None: ...
