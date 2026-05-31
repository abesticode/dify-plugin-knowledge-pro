from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI
import json


class UnbindKnowledgeTagsTool(Tool):
    """
    Tool for removing tags from a knowledge base.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Remove tags from a knowledge base.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        target_id = tool_parameters.get("target_id", "").strip()
        tag_ids_str = tool_parameters.get("tag_ids", "")

        if not target_id:
            yield self.create_text_message("Target (Knowledge Base) ID is required.")
            return

        if not tag_ids_str:
            yield self.create_text_message("Tag IDs are required.")
            return

        # Parse tag_ids
        tag_ids = []
        try:
            tag_ids = json.loads(tag_ids_str)
            if not isinstance(tag_ids, list):
                tag_ids = [str(tag_ids)]
        except json.JSONDecodeError:
            tag_ids = [t.strip() for t in tag_ids_str.split(",") if t.strip()]

        if not tag_ids:
            yield self.create_text_message("Valid Tag IDs must be provided.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            api.unbind_tags(target_id=target_id, tag_ids=tag_ids)

            summary = f"Successfully unbound {len(tag_ids)} tag(s) from knowledge base '{target_id}'."

            yield self.create_text_message(summary)
            yield self.create_json_message({"status": "success", "target_id": target_id, "unbound_tags": tag_ids})

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
