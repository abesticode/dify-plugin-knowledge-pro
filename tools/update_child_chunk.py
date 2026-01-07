from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateChildChunkTool(Tool):
    """
    Tool for updating the content of an existing child chunk.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a child chunk's content.
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
        content = tool_parameters.get("content", "").strip()

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
        if not content:
            yield self.create_text_message("Content is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.update_child_chunk(
                dataset_id=dataset_id,
                document_id=document_id,
                segment_id=segment_id,
                child_chunk_id=child_chunk_id,
                content=content
            )

            # Format response
            chunk_data = result.get("data", result)
            word_count = chunk_data.get("word_count", 0)
            tokens = chunk_data.get("tokens", 0)
            status = chunk_data.get("status", "processing")

            summary = f"Child chunk updated successfully!\n"
            summary += f"- ID: {child_chunk_id}\n"
            summary += f"- New Word Count: {word_count}\n"
            summary += f"- New Tokens: {tokens}\n"
            summary += f"- Status: {status}\n"
            summary += f"\nThe chunk is being re-indexed."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
