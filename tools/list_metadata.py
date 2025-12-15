from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListMetadataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the list of metadata fields in a Dify knowledge base.
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

            # List metadata fields
            result = api.list_metadata(dataset_id=dataset_id)

            # Create response
            doc_metadata = result.get("doc_metadata", [])
            built_in_enabled = result.get("built_in_field_enabled", False)

            if not doc_metadata:
                summary = f"No metadata fields found in dataset '{dataset_id}'. Built-in fields enabled: {built_in_enabled}"
            else:
                summary = f"Found {len(doc_metadata)} metadata field(s) in dataset. Built-in fields enabled: {built_in_enabled}"

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error listing metadata fields: {str(e)}")
            return
