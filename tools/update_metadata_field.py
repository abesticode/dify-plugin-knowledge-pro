from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateMetadataFieldTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a metadata field in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        metadata_id = tool_parameters.get("metadata_id", "")
        name = tool_parameters.get("name", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not metadata_id:
            yield self.create_text_message("Metadata ID is required.")
            return
        if not name:
            yield self.create_text_message("New field name is required.")
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

            # Update metadata field
            result = api.update_metadata_field(
                dataset_id=dataset_id,
                metadata_id=metadata_id,
                name=name
            )

            # Create response
            summary = f"Metadata field '{metadata_id}' updated successfully. New name: '{name}'"
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating metadata field: {str(e)}")
            return
