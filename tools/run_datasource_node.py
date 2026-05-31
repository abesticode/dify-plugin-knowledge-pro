from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class RunDatasourceNodeTool(Tool):
    """
    Tool for executing a single datasource node within a knowledge pipeline.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Run a datasource node.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        dataset_id = tool_parameters.get("dataset_id", "").strip()
        node_id = tool_parameters.get("node_id", "").strip()
        datasource_type = tool_parameters.get("datasource_type", "").strip()
        inputs_str = tool_parameters.get("inputs", "{}").strip()
        credential_id = tool_parameters.get("credential_id", "")
        
        is_published = tool_parameters.get("is_published")
        if is_published is not None and isinstance(is_published, str):
            is_published = is_published.lower() == "true"
        elif is_published is None:
            is_published = True

        if not dataset_id or not node_id or not datasource_type:
            yield self.create_text_message("Dataset ID, Node ID, and Datasource Type are required.")
            return

        try:
            inputs = json.loads(inputs_str) if inputs_str else {}
        except json.JSONDecodeError:
            yield self.create_text_message("Invalid JSON string for inputs parameter.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            
            # This API returns a Server-Sent Events stream. DifyKnowledgeAPI will return raw or parsed response.
            result = api.run_datasource_node(
                dataset_id=dataset_id,
                node_id=node_id,
                inputs=inputs,
                datasource_type=datasource_type,
                is_published=is_published,
                credential_id=credential_id if credential_id else None
            )

            # Check if result is a raw string (from SSE stream parsing failure/fallback)
            if isinstance(result, str):
                summary = f"Datasource Node executed. Raw Stream Response:\n\n{result[:500]}..."
                yield self.create_text_message(summary)
            else:
                summary = f"Successfully triggered datasource node '{node_id}' execution."
                yield self.create_text_message(summary)
                yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
