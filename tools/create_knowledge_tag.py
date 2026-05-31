from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class CreateKnowledgeTagTool(Tool):
    """
    Tool for creating a new knowledge base tag.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new knowledge base tag.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        name = tool_parameters.get("name", "").strip()

        if not name:
            yield self.create_text_message("Tag name is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.create_tag(name=name)

            # Format response
            tag_id = result.get("id", "N/A")
            tag_name = result.get("name", name)
            
            summary = f"Successfully created tag '{tag_name}' (ID: {tag_id})."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
