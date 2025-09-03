from typing import Any

from _typeshed import Incomplete
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.adapters.chat_adapter import FieldInfoWithName as FieldInfoWithName
from dspy.adapters.utils import format_field_value as format_field_value
from dspy.signatures.signature import Signature as Signature
from dspy.utils.callback import BaseCallback as BaseCallback

class XMLAdapter(ChatAdapter):
    field_pattern: Incomplete
    def __init__(self, callbacks: list[BaseCallback] | None = None) -> None: ...
    def format_field_with_value(self, fields_with_values: dict[FieldInfoWithName, Any]) -> str: ...
    def user_message_output_requirements(self, signature: type[Signature]) -> str: ...
    def parse(self, signature: type[Signature], completion: str) -> dict[str, Any]: ...
