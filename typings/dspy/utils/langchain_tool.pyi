from dspy.adapters.types.tool import Tool as Tool
from dspy.adapters.types.tool import (
    convert_input_schema_to_tool_args as convert_input_schema_to_tool_args,
)
from langchain.tools import BaseTool as BaseTool

def convert_langchain_tool(tool: BaseTool) -> Tool: ...
