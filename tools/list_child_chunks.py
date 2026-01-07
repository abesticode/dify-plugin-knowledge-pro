from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListChildChunksTool(Tool):
    """
    Tool for listing child chunks from a parent segment.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List child chunks from a parent segment.
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
        keyword = tool_parameters.get("keyword", "")
        page = int(tool_parameters.get("page", 1))
        limit = int(tool_parameters.get("limit", 20))

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not segment_id:
            yield self.create_text_message("Segment ID is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.list_child_chunks(
                dataset_id=dataset_id,
                document_id=document_id,
                segment_id=segment_id,
                keyword=keyword if keyword else None,
                page=page,
                limit=limit
            )

            # Format response
            child_chunks = result.get("data", [])
            total = result.get("total", len(child_chunks))
            total_pages = result.get("total_pages", 1)
            current_page = result.get("page", page)

            summary = f"Found {total} child chunk(s) (Page {current_page}/{total_pages}):\n\n"
            
            for i, chunk in enumerate(child_chunks, 1):
                chunk_id = chunk.get("id", "N/A")
                content = chunk.get("content", "")
                word_count = chunk.get("word_count", 0)
                status = chunk.get("status", "N/A")
                
                # Truncate content for display
                display_content = content[:100] + "..." if len(content) > 100 else content
                
                summary += f"{i}. ID: {chunk_id}\n"
                summary += f"   Content: {display_content}\n"
                summary += f"   Words: {word_count} | Status: {status}\n\n"

            if not child_chunks:
                summary = f"No child chunks found for segment {segment_id}."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
