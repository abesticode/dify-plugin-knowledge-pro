from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListDocumentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the list of documents in a Dify knowledge base with optional keyword search.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "").strip()
        keyword = tool_parameters.get("keyword", "").strip()
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

            # List documents with optional keyword filter
            result = api.list_documents(
                dataset_id=dataset_id,
                keyword=keyword if keyword else None,
                page=page,
                limit=limit
            )

            # Create response
            documents = result.get("data", [])
            total = result.get("total", 0)
            has_more = result.get("has_more", False)

            if not documents:
                if keyword:
                    yield self.create_text_message(f"No documents found matching '{keyword}' in dataset.")
                else:
                    yield self.create_text_message(f"No documents found in dataset '{dataset_id}'.")
            else:
                search_info = f" matching '{keyword}'" if keyword else ""
                summary = f"Found {total} document(s){search_info}. Showing page {page} with {len(documents)} item(s).\n\n"
                
                # List document names and IDs for easy reference
                for i, doc in enumerate(documents, 1):
                    doc_id = doc.get("id", "N/A")
                    doc_name = doc.get("name", "Untitled")
                    word_count = doc.get("word_count", 0)
                    status = doc.get("indexing_status", "N/A")
                    summary += f"{i}. **{doc_name}**\n   ID: `{doc_id}`\n   Words: {word_count} | Status: {status}\n\n"
                
                if has_more:
                    summary += "_More results available. Increase page number to see more._"
                
                yield self.create_text_message(summary)

            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error listing documents: {str(e)}")
            return
