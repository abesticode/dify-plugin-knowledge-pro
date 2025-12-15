from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateChunkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a chunk (segment) in a document.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")
        segment_id = tool_parameters.get("segment_id", "")
        content = tool_parameters.get("content", "")
        answer = tool_parameters.get("answer", "")
        keywords_str = tool_parameters.get("keywords", "")
        enabled = tool_parameters.get("enabled")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not segment_id:
            yield self.create_text_message("Segment ID is required.")
            return

        # Check if at least one update field is provided
        if not content and not answer and not keywords_str and enabled is None:
            yield self.create_text_message("At least one field (content, answer, keywords, or enabled) is required to update.")
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

            # Parse keywords
            keywords = None
            if keywords_str:
                keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

            # Update chunk
            result = api.update_chunk(
                dataset_id=dataset_id,
                document_id=document_id,
                segment_id=segment_id,
                content=content if content else None,
                answer=answer if answer else None,
                keywords=keywords,
                enabled=enabled
            )

            # Create response
            data = result.get("data", [])
            if data:
                updated_id = data[0].get("id", segment_id)
                summary = f"Chunk '{updated_id}' updated successfully."
            else:
                summary = "Chunk updated but no data returned."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating chunk: {str(e)}")
            return
