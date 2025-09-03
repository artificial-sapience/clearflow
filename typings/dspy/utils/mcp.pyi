import mcp
from dspy.adapters.types.tool import Tool as Tool
from dspy.adapters.types.tool import (
    convert_input_schema_to_tool_args as convert_input_schema_to_tool_args,
)

def convert_mcp_tool(session: mcp.client.session.ClientSession, tool: mcp.types.Tool) -> Tool: ...
