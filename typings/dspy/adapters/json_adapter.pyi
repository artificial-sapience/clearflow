from typing import Any

from _typeshed import Incomplete
from dspy.adapters.chat_adapter import ChatAdapter as ChatAdapter
from dspy.adapters.chat_adapter import FieldInfoWithName as FieldInfoWithName
from dspy.adapters.types.tool import ToolCalls as ToolCalls
from dspy.adapters.utils import format_field_value as format_field_value
from dspy.adapters.utils import get_annotation_name as get_annotation_name
from dspy.adapters.utils import parse_value as parse_value
from dspy.adapters.utils import serialize_for_json as serialize_for_json
from dspy.adapters.utils import translate_field_type as translate_field_type
from dspy.clients.lm import LM as LM
from dspy.signatures.signature import Signature as Signature
from dspy.signatures.signature import SignatureMeta as SignatureMeta
from dspy.utils.callback import BaseCallback as BaseCallback
from dspy.utils.exceptions import AdapterParseError as AdapterParseError
from pydantic.fields import FieldInfo as FieldInfo

logger: Incomplete

class JSONAdapter(ChatAdapter):
    def __init__(self, callbacks: list[BaseCallback] | None = None, use_native_function_calling: bool = True) -> None: ...
    def __call__(self, lm: LM, lm_kwargs: dict[str, Any], signature: type[Signature], demos: list[dict[str, Any]], inputs: dict[str, Any]) -> list[dict[str, Any]]: ...
    async def acall(self, lm: LM, lm_kwargs: dict[str, Any], signature: type[Signature], demos: list[dict[str, Any]], inputs: dict[str, Any]) -> list[dict[str, Any]]: ...
    def format_field_structure(self, signature: type[Signature]) -> str: ...
    def user_message_output_requirements(self, signature: type[Signature]) -> str: ...
    def format_assistant_message_content(self, signature: type[Signature], outputs: dict[str, Any], missing_field_message=None) -> str: ...
    def parse(self, signature: type[Signature], completion: str) -> dict[str, Any]: ...
    def format_field_with_value(self, fields_with_values: dict[FieldInfoWithName, Any], role: str = "user") -> str: ...
    def format_finetune_data(self, signature: type[Signature], demos: list[dict[str, Any]], inputs: dict[str, Any], outputs: dict[str, Any]) -> dict[str, list[Any]]: ...
