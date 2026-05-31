from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ToggleBuiltInMetadataTool(Tool):
    """
    Tool for enabling or disabling built-in metadata fields.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Enable or disable built-in metadata fields for a knowledge base.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        dataset_id = tool_parameters.get("dataset_id", "").strip()
        action = tool_parameters.get("action", "").strip()

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return

        if action not in ["enable", "disable"]:
            yield self.create_text_message("Action must be 'enable' or 'disable'.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.toggle_built_in_metadata(dataset_id=dataset_id, action=action)

            status = result.get("result", "success")
            summary = f"Built-in metadata fields successfully {action}d for dataset '{dataset_id}'. Result: {status}"

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
