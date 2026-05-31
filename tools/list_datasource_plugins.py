from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListDatasourcePluginsTool(Tool):
    """
    Tool for listing datasource nodes configured in a knowledge pipeline.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List datasource plugins.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        dataset_id = tool_parameters.get("dataset_id", "").strip()
        is_published = tool_parameters.get("is_published")
        
        if is_published is not None and isinstance(is_published, str):
            is_published = is_published.lower() == "true"
        elif is_published is None:
            is_published = True

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.list_datasource_plugins(dataset_id=dataset_id, is_published=is_published)

            nodes = result if isinstance(result, list) else result.get("data", result)
            if isinstance(nodes, dict):
                nodes = [nodes]

            summary = f"Found {len(nodes)} datasource node(s) in pipeline for dataset '{dataset_id}':\n\n"
            
            for i, node in enumerate(nodes, 1):
                node_id = node.get("node_id", "Unknown")
                title = node.get("title", "Unknown")
                ds_type = node.get("datasource_type", "Unknown")
                
                summary += f"{i}. Title: {title}\n"
                summary += f"   Node ID: {node_id}\n"
                summary += f"   Type: {ds_type}\n\n"

            if not nodes:
                summary = f"No datasource nodes found for dataset '{dataset_id}'."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
