from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListDocumentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the list of documents in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        page = int(tool_parameters.get("page", 1))
        limit = int(tool_parameters.get("limit", 20))

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

            # List documents
            result = api.list_documents(dataset_id=dataset_id, page=page, limit=limit)

            # Create response
            documents = result.get("data", [])
            total = result.get("total", 0)
            has_more = result.get("has_more", False)

            if not documents:
                yield self.create_text_message(f"No documents found in dataset '{dataset_id}'.")
            else:
                summary = f"Found {total} document(s) in dataset. Showing page {page} with {len(documents)} item(s)."
                if has_more:
                    summary += " More results available."
                yield self.create_text_message(summary)

            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error listing documents: {str(e)}")
            return
