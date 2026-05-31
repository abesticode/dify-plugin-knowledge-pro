from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class DeleteKnowledgeTagTool(Tool):
    """
    Tool for deleting a knowledge base tag.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete a knowledge base tag.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        tag_id = tool_parameters.get("tag_id", "").strip()

        if not tag_id:
            yield self.create_text_message("Tag ID is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.delete_tag(tag_id=tag_id)

            summary = f"Successfully deleted tag with ID '{tag_id}'."

            yield self.create_text_message(summary)
            yield self.create_json_message({"status": "success", "tag_id": tag_id})

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
