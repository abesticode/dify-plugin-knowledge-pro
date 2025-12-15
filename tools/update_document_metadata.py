from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateDocumentMetadataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update metadata values for a document in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")
        metadata_id = tool_parameters.get("metadata_id", "")
        metadata_name = tool_parameters.get("metadata_name", "")
        metadata_value = tool_parameters.get("metadata_value", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not metadata_id:
            yield self.create_text_message("Metadata field ID is required.")
            return
        if not metadata_name:
            yield self.create_text_message("Metadata field name is required.")
            return
        if not metadata_value:
            yield self.create_text_message("Metadata value is required.")
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

            # Build operation data
            operation_data = [
                {
                    "document_id": document_id,
                    "metadata_list": [
                        {
                            "id": metadata_id,
                            "name": metadata_name,
                            "value": metadata_value
                        }
                    ]
                }
            ]

            # Update document metadata
            result = api.update_document_metadata(
                dataset_id=dataset_id,
                operation_data=operation_data
            )

            # Create response
            summary = f"Document '{document_id}' metadata updated successfully. Field '{metadata_name}' set to '{metadata_value}'"
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating document metadata: {str(e)}")
            return
