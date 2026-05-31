from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class GetDocumentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get detailed information about a specific document in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")
        metadata_filter = tool_parameters.get("metadata_filter", "all")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
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

            # Get document details
            result = api.get_document(
                dataset_id=dataset_id, 
                document_id=document_id,
                metadata=metadata_filter
            )

            # Create response
            name = result.get("name", "Unknown")
            status = result.get("display_status", result.get("indexing_status", "Unknown"))
            tokens = result.get("tokens", 0)
            
            summary = f"Retrieved document '{name}' successfully. Status: {status}, Tokens: {tokens}."
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error getting document: {str(e)}")
            return
