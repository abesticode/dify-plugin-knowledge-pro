from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListBuiltInMetadataTool(Tool):
    """
    Tool for listing built-in metadata fields of a dataset.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List built-in metadata fields.
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
            result = api.list_built_in_metadata(dataset_id=dataset_id)

            fields = result.get("fields", [])

            summary = f"Found {len(fields)} built-in metadata field(s) for dataset '{dataset_id}':\n\n"
            
            for i, field in enumerate(fields, 1):
                name = field.get("name", "N/A")
                f_type = field.get("type", "N/A")
                
                summary += f"{i}. Name: {name} | Type: {f_type}\n"

            if not fields:
                summary = f"No built-in metadata fields found for dataset '{dataset_id}'."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
