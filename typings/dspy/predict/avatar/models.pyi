from typing import Any

from pydantic import BaseModel

class Tool(BaseModel):
    tool: Any
    name: str
    desc: str | None
    input_type: str | None

class Action(BaseModel):
    tool_name: Any
    tool_input_query: Any

class ActionOutput(BaseModel):
    tool_name: str
    tool_input_query: str
    tool_output: str
