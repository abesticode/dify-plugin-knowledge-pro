from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class CreateChildChunkTool(Tool):
    """
    Tool for creating a new child chunk under a parent segment.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new child chunk.
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
        if not content:
            yield self.create_text_message("Content is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.create_child_chunk(
                dataset_id=dataset_id,
                document_id=document_id,
                segment_id=segment_id,
                content=content
            )

            # Format response
            chunk_data = result.get("data", result)
            chunk_id = chunk_data.get("id", "N/A")
            word_count = chunk_data.get("word_count", 0)
            tokens = chunk_data.get("tokens", 0)
            status = chunk_data.get("status", "processing")

            summary = f"Child chunk created successfully!\n"
            summary += f"- ID: {chunk_id}\n"
            summary += f"- Parent Segment: {segment_id}\n"
            summary += f"- Word Count: {word_count}\n"
            summary += f"- Tokens: {tokens}\n"
            summary += f"- Status: {status}\n"
            summary += f"\nThe chunk is being indexed and will be available for retrieval shortly."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
