from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListDatasetTagsTool(Tool):
    """
    Tool for listing tags bound to a specific knowledge base.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List tags bound to a specific knowledge base.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        dataset_id = tool_parameters.get("dataset_id", "").strip()

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.list_dataset_tags(dataset_id=dataset_id)

            tags = result.get("data", [])
            total = result.get("total", len(tags))

            summary = f"Found {total} tag(s) bound to dataset '{dataset_id}':\n\n"
            
            for i, tag in enumerate(tags, 1):
                tag_id = tag.get("id", "N/A")
                name = tag.get("name", "N/A")
                
                summary += f"{i}. Name: {name} (ID: {tag_id})\n"

            if not tags:
                summary = f"No tags bound to dataset '{dataset_id}'."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
