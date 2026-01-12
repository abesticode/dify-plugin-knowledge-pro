from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI
from utils.cost_calculator import CostCalculator


class GetIndexingStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get the document embedding/indexing status with token usage information.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "").strip()
        batch = tool_parameters.get("batch", "").strip()

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not batch:
            yield self.create_text_message("Batch ID is required.")
            return

        try:
            # Get credentials
            api_key = self.runtime.credentials.get("api_key")
            base_url = self.runtime.credentials.get("base_url")

            if not api_key or not base_url:
                yield self.create_text_message("API key and base URL are required.")
                return

            # Create API client and cost calculator
            api = DifyKnowledgeAPI(api_key, base_url)
            cost_calc = CostCalculator.from_credentials(self.runtime.credentials)

            # Get indexing status
            result = api.get_indexing_status(dataset_id=dataset_id, batch=batch)

            # Create response
            data = result.get("data", [])
            if data:
                status_info = data[0]
                indexing_status = status_info.get("indexing_status", "unknown")
                completed = status_info.get("completed_segments", 0)
                total = status_info.get("total_segments", 0)
                tokens = status_info.get("tokens", 0)
                
                progress = f"{completed}/{total}" if total else "N/A"
                
                # Add cost info to result for easy JSON extraction
                if tokens and tokens > 0:
                    result["cost_info"] = cost_calc.get_cost_info(tokens, is_estimated=False)
                else:
                    result["cost_info"] = None
                
                summary = f"📊 **Indexing Status:**\n\n"
                summary += f"- Status: **{indexing_status}**\n"
                summary += f"- Progress: {progress} segments completed\n"
                
                # Token and cost information using configured model
                if tokens and tokens > 0:
                    summary += cost_calc.format_cost_message(tokens)
                
                if indexing_status == "completed":
                    summary += f"\n✅ Indexing completed successfully!"
                elif indexing_status == "indexing":
                    summary += f"\n⏳ Indexing in progress..."
                elif indexing_status == "error":
                    error = status_info.get("error", "Unknown error")
                    summary += f"\n❌ Error: {error}"
            else:
                summary = "No indexing status found for the specified batch."
                result["cost_info"] = None

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error getting indexing status: {str(e)}")
            return
