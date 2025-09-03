from collections.abc import Callable
from typing import Any

import mcp
from dspy.adapters.types.base_type import Type as Type
from dspy.dsp.utils.settings import settings as settings
from dspy.utils.callback import with_callbacks as with_callbacks
from langchain.tools import BaseTool as BaseTool

class Tool(Type):
    func: Callable
    name: str | None
    desc: str | None
    args: dict[str, Any] | None
    arg_types: dict[str, Any] | None
    arg_desc: dict[str, str] | None
    has_kwargs: bool
    def __init__(self, func: Callable, name: str | None = None, desc: str | None = None, args: dict[str, Any] | None = None, arg_types: dict[str, Any] | None = None, arg_desc: dict[str, str] | None = None) -> None: ...
    def format(self): ...
    def format_as_litellm_function_call(self): ...
    @with_callbacks
    def __call__(self, **kwargs): ...
    @with_callbacks
    async def acall(self, **kwargs): ...
    @classmethod
    def from_mcp_tool(cls, session: mcp.client.session.ClientSession, tool: mcp.types.Tool) -> Tool: ...
    @classmethod
    def from_langchain(cls, tool: BaseTool) -> Tool: ...

class ToolCalls(Type):
    class ToolCall(Type):
        name: str
        args: dict[str, Any]
        def format(self): ...
    tool_calls: list[ToolCall]
    @classmethod
    def from_dict_list(cls, tool_calls_dicts: list[dict[str, Any]]) -> ToolCalls: ...
    @classmethod
    def description(cls) -> str: ...
    def format(self) -> list[dict[str, Any]]: ...
    @classmethod
    def validate_input(cls, data: Any): ...

def convert_input_schema_to_tool_args(schema: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Type], dict[str, str]]: ...
