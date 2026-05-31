import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListDatasetsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the list of knowledge bases (datasets) from Dify.
        """
        # Get parameters
        page = int(tool_parameters.get("page", 1))
        limit = int(tool_parameters.get("limit", 20))
        keyword = tool_parameters.get("keyword")
        include_all = bool(tool_parameters.get("include_all", False))
        
        tag_ids_raw = tool_parameters.get("tag_ids")
        tag_ids = None
        if tag_ids_raw:
            if isinstance(tag_ids_raw, str):
                try:
                    tag_ids = json.loads(tag_ids_raw)
                except json.JSONDecodeError:
                    tag_ids = [t.strip() for t in tag_ids_raw.split(",")]
            elif isinstance(tag_ids_raw, list):
                tag_ids = tag_ids_raw

        try:
            # Get credentials
            api_key = self.runtime.credentials.get("api_key")
            base_url = self.runtime.credentials.get("base_url")

            if not api_key or not base_url:
                yield self.create_text_message("API key and base URL are required.")
                return

            # Create API client
            api = DifyKnowledgeAPI(api_key, base_url)

            # List datasets
            result = api.list_datasets(
                page=page, 
                limit=limit,
                keyword=keyword,
                include_all=include_all,
                tag_ids=tag_ids
            )

            # Create response
            datasets = result.get("data", [])
            total = result.get("total", 0)
            has_more = result.get("has_more", False)

            if not datasets:
                yield self.create_text_message("No datasets found.")
            else:
                summary = f"Found {total} dataset(s). Showing page {page} with {len(datasets)} item(s)."
                if has_more:
                    summary += " More results available."
                yield self.create_text_message(summary)

            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error listing datasets: {str(e)}")
            return
