from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class CreateDatasetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new empty knowledge base (dataset) in Dify.
        """
        # Get parameters
        name = tool_parameters.get("name", "")
        permission = tool_parameters.get("permission", "only_me")

        # Validate parameters
        if not name:
            yield self.create_text_message("Dataset name is required.")
            return

        try:
            # Get credentials
            api_key = self.runtime.credentials.get("api_key")
            base_url = self.runtime.credentials.get("base_url")

            if not api_key or not base_url:
                yield self.create_text_message("API key and base URL are required.")
                return

            # Create API client
            api = DifyKnowledgeAPI(api_key, base_url)

            # Create the dataset
            result = api.create_dataset(name=name, permission=permission)

            # Create response
            summary = f"Dataset '{result.get('name', name)}' created successfully with ID: {result.get('id', 'N/A')}"
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error creating dataset: {str(e)}")
            return
