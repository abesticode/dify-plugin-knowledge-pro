from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class DeleteChildChunkTool(Tool):
    """
    Tool for deleting a child chunk from a parent segment.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete a child chunk.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "").strip()
        document_id = tool_parameters.get("document_id", "").strip()
        segment_id = tool_parameters.get("segment_id", "").strip()
        child_chunk_id = tool_parameters.get("child_chunk_id", "").strip()

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not segment_id:
            yield self.create_text_message("Segment ID is required.")
            return
        if not child_chunk_id:
            yield self.create_text_message("Child Chunk ID is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.delete_child_chunk(
                dataset_id=dataset_id,
                document_id=document_id,
                segment_id=segment_id,
                child_chunk_id=child_chunk_id
            )

            summary = f"Child chunk deleted successfully!\n"
            summary += f"- Deleted ID: {child_chunk_id}\n"
            summary += f"- Parent Segment: {segment_id}"

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
