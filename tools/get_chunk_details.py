from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class GetChunkDetailsTool(Tool):
    """
    Tool for getting detailed information of a specific chunk/segment.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get details of a specific chunk.
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
            result = api.get_chunk_details(dataset_id, document_id, segment_id)

            # Format response
            chunk_data = result.get("data", result)
            summary = f"Chunk Details:\n"
            summary += f"- ID: {chunk_data.get('id', 'N/A')}\n"
            summary += f"- Position: {chunk_data.get('position', 'N/A')}\n"
            summary += f"- Word Count: {chunk_data.get('word_count', 'N/A')}\n"
            summary += f"- Tokens: {chunk_data.get('tokens', 'N/A')}\n"
            summary += f"- Hit Count: {chunk_data.get('hit_count', 0)}\n"
            summary += f"- Status: {chunk_data.get('status', 'N/A')}\n"
            summary += f"- Enabled: {chunk_data.get('enabled', True)}\n"
            
            keywords = chunk_data.get('keywords', [])
            if keywords:
                summary += f"- Keywords: {', '.join(keywords)}\n"

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
