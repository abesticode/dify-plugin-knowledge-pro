from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class AddChunksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Add chunks (segments) to a document in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")
        content = tool_parameters.get("content", "")
        answer = tool_parameters.get("answer", "")
        keywords_str = tool_parameters.get("keywords", "")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not content:
            yield self.create_text_message("Chunk content is required.")
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
            keywords = []
            if keywords_str:
                keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

            # Build segment object
            segment = {"content": content}
            if answer:
                segment["answer"] = answer
            if keywords:
                segment["keywords"] = keywords

            # Add chunks
            result = api.add_chunks(
                dataset_id=dataset_id,
                document_id=document_id,
                segments=[segment]
            )

            # Create response
            data = result.get("data", [])
            if data:
                chunk_id = data[0].get("id", "N/A")
                summary = f"Chunk added successfully to document. Chunk ID: {chunk_id}"
            else:
                summary = "Chunk added but no data returned."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error adding chunk: {str(e)}")
            return
