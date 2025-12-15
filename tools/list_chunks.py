from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListChunksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get chunks (segments) from a document in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")

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

            # List chunks
            result = api.list_chunks(dataset_id=dataset_id, document_id=document_id)

            # Create response
            data = result.get("data", [])
            doc_form = result.get("doc_form", "unknown")

            if not data:
                yield self.create_text_message(f"No chunks found in document '{document_id}'.")
            else:
                summary = f"Found {len(data)} chunk(s) in document. Document form: {doc_form}"
                yield self.create_text_message(summary)

            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error listing chunks: {str(e)}")
            return
