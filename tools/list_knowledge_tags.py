from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListKnowledgeTagsTool(Tool):
    """
    Tool for listing all knowledge base tags in the workspace.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List all knowledge base tags in the workspace.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.list_workspace_tags()

            # Format response
            tags = result if isinstance(result, list) else result.get("data", result)
            if isinstance(tags, dict) and not tags:
                tags = []
                
            summary = f"Found {len(tags)} knowledge tag(s):\n\n"
            
            for i, tag in enumerate(tags, 1):
                tag_id = tag.get("id", "N/A")
                name = tag.get("name", "N/A")
                binding_count = tag.get("binding_count", 0)
                
                summary += f"{i}. Name: {name}\n"
                summary += f"   ID: {tag_id} | Bound Knowledge Bases: {binding_count}\n\n"

            if not tags:
                summary = "No knowledge tags found in the workspace."

            yield self.create_text_message(summary)
            yield self.create_json_message(tags)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
