from dataclasses import dataclass
from typing import Any

import dspy
from _typeshed import Incomplete
from dspy.primitives.prediction import Prediction as Prediction

@dataclass
class Document:
    page_content: str
    metadata: dict[str, Any]
    type: str
    def to_dict(self) -> dict[str, Any]: ...

class DatabricksRM(dspy.Retrieve):
    databricks_token: Incomplete
    databricks_endpoint: Incomplete
    databricks_client_id: Incomplete
    databricks_client_secret: Incomplete
    databricks_index_name: Incomplete
    columns: Incomplete
    filters_json: Incomplete
    k: Incomplete
    docs_id_column_name: Incomplete
    docs_uri_column_name: Incomplete
    text_column_name: Incomplete
    use_with_databricks_agent_framework: Incomplete
    def __init__(self, databricks_index_name: str, databricks_endpoint: str | None = None, databricks_token: str | None = None, databricks_client_id: str | None = None, databricks_client_secret: str | None = None, columns: list[str] | None = None, filters_json: str | None = None, k: int = 3, docs_id_column_name: str = "id", docs_uri_column_name: str | None = None, text_column_name: str = "text", use_with_databricks_agent_framework: bool = False) -> None: ...
    def forward(self, query: str | list[float], query_type: str = "ANN", filters_json: str | None = None) -> dspy.Prediction | list[dict[str, Any]]: ...
