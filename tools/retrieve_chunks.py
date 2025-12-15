from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class RetrieveChunksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search and retrieve chunks from a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        query = tool_parameters.get("query", "")
        search_method = tool_parameters.get("search_method", "keyword_search")
        top_k = int(tool_parameters.get("top_k", 5))
        score_threshold_enabled = tool_parameters.get("score_threshold_enabled", False)
        score_threshold = tool_parameters.get("score_threshold")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not query:
            yield self.create_text_message("Search query is required.")
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

            # Retrieve chunks
            result = api.retrieve_chunks(
                dataset_id=dataset_id,
                query=query,
                search_method=search_method,
                top_k=top_k,
                score_threshold_enabled=score_threshold_enabled,
                score_threshold=float(score_threshold) if score_threshold else None
            )

            # Create response
            records = result.get("records", [])
            query_content = result.get("query", {}).get("content", query)

            if not records:
                yield self.create_text_message(f"No matching chunks found for query: '{query_content}'")
            else:
                summary = f"Found {len(records)} matching chunk(s) for query: '{query_content}'"
                yield self.create_text_message(summary)

            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error retrieving chunks: {str(e)}")
            return
