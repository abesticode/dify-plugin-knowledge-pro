from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateKnowledgeTagTool(Tool):
    """
    Tool for renaming an existing knowledge base tag.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Rename an existing knowledge base tag.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        tag_id = tool_parameters.get("tag_id", "").strip()
        name = tool_parameters.get("name", "").strip()

        if not tag_id:
            yield self.create_text_message("Tag ID is required.")
            return
            
        if not name:
            yield self.create_text_message("New tag name is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.update_tag(tag_id=tag_id, name=name)

            tag_name = result.get("name", name)
            summary = f"Successfully updated tag to '{tag_name}' (ID: {tag_id})."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
