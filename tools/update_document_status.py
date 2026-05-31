import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateDocumentStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update the status of multiple documents in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        action = tool_parameters.get("action", "")
        
        document_ids_raw = tool_parameters.get("document_ids")
        document_ids = []
        if document_ids_raw:
            if isinstance(document_ids_raw, str):
                try:
                    document_ids = json.loads(document_ids_raw)
                except json.JSONDecodeError:
                    document_ids = [d.strip() for d in document_ids_raw.split(",")]
            elif isinstance(document_ids_raw, list):
                document_ids = document_ids_raw

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not action:
            yield self.create_text_message("Action is required.")
            return
        if not document_ids:
            yield self.create_text_message("Document IDs are required.")
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

            # Update document status
            result = api.update_document_status_in_batch(
                dataset_id=dataset_id,
                action=action,
                document_ids=document_ids
            )

            # Create response
            res_str = result.get("result", "success")
            
            summary = f"Documents {action}d successfully. Result: {res_str}"
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating document status: {str(e)}")
            return
