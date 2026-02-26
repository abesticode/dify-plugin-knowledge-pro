from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI
from utils.credential_resolver import resolve_credentials


class DeleteDatasetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete a knowledge base (dataset) from Dify.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return

        try:
            # Resolve credentials (parameter override > provider credentials)
            api_key, base_url = resolve_credentials(tool_parameters, self.runtime.credentials)

            if not api_key or not base_url:
                yield self.create_text_message("API key and base URL are required. Provide them as tool parameters or set up default credentials in the plugin.")
                return

            # Create API client
            api = DifyKnowledgeAPI(api_key, base_url)

            # Delete the dataset
            result = api.delete_dataset(dataset_id=dataset_id)

            # Create response
            summary = f"Dataset '{dataset_id}' deleted successfully."
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error deleting dataset: {str(e)}")
            return
