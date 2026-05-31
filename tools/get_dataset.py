from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class GetDatasetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get detailed information about a specific knowledge base (dataset) in Dify.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
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

            # Get the dataset
            result = api.get_dataset(dataset_id=dataset_id)

            # Create response
            name = result.get("name", "Unknown")
            doc_count = result.get("document_count", 0)
            summary = f"Retrieved dataset '{name}' successfully. It has {doc_count} document(s)."
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error getting dataset: {str(e)}")
            return
