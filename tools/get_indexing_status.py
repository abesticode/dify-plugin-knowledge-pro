from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class GetIndexingStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the document embedding/indexing status.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        batch = tool_parameters.get("batch", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not batch:
            yield self.create_text_message("Batch ID is required.")
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

            # Get indexing status
            result = api.get_indexing_status(dataset_id=dataset_id, batch=batch)

            # Create response
            data = result.get("data", [])
            if data:
                status_info = data[0]
                indexing_status = status_info.get("indexing_status", "unknown")
                completed = status_info.get("completed_segments", 0)
                total = status_info.get("total_segments", 0)
                progress = f"{completed}/{total}" if total else "N/A"
                summary = f"Indexing status: {indexing_status}. Progress: {progress} segments completed."
            else:
                summary = "No indexing status found for the specified batch."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error getting indexing status: {str(e)}")
            return
