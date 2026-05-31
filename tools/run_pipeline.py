from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class RunPipelineTool(Tool):
    """
    Tool for executing a full knowledge pipeline.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Run a knowledge pipeline.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        dataset_id = tool_parameters.get("dataset_id", "").strip()
        datasource_type = tool_parameters.get("datasource_type", "").strip()
        start_node_id = tool_parameters.get("start_node_id", "").strip()
        inputs_str = tool_parameters.get("inputs", "{}").strip()
        ds_info_str = tool_parameters.get("datasource_info_list", "[]").strip()
        
        is_published = tool_parameters.get("is_published")
        if is_published is not None and isinstance(is_published, str):
            is_published = is_published.lower() == "true"
        elif is_published is None:
            is_published = True

        if not dataset_id or not datasource_type or not start_node_id:
            yield self.create_text_message("Dataset ID, Datasource Type, and Start Node ID are required.")
            return

        try:
            inputs = json.loads(inputs_str) if inputs_str else {}
        except json.JSONDecodeError:
            yield self.create_text_message("Invalid JSON string for inputs parameter.")
            return

        try:
            ds_info_list = json.loads(ds_info_str) if ds_info_str else []
            if not isinstance(ds_info_list, list):
                yield self.create_text_message("datasource_info_list must be a JSON array.")
                return
        except json.JSONDecodeError:
            yield self.create_text_message("Invalid JSON string for datasource_info_list parameter.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            
            # Using response_mode=blocking by default for easier tool consumption
            result = api.run_pipeline(
                dataset_id=dataset_id,
                inputs=inputs,
                datasource_type=datasource_type,
                datasource_info_list=ds_info_list,
                start_node_id=start_node_id,
                is_published=is_published,
                response_mode="blocking"
            )

            # Sometimes blocking API still returns stream if an error occurs.
            if isinstance(result, str):
                summary = f"Pipeline execution completed. Response:\n\n{result[:500]}..."
                yield self.create_text_message(summary)
            else:
                summary = "Pipeline executed successfully in blocking mode."
                yield self.create_text_message(summary)
                yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
