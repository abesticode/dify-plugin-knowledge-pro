import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateDatasetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update an existing knowledge base (dataset) in Dify.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        name = tool_parameters.get("name")
        description = tool_parameters.get("description")
        indexing_technique = tool_parameters.get("indexing_technique")
        permission = tool_parameters.get("permission")
        embedding_model = tool_parameters.get("embedding_model")
        embedding_model_provider = tool_parameters.get("embedding_model_provider")
        external_knowledge_id = tool_parameters.get("external_knowledge_id")
        external_knowledge_api_id = tool_parameters.get("external_knowledge_api_id")

        def parse_json_param(param_name):
            val = tool_parameters.get(param_name)
            if val and isinstance(val, str):
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    pass
            return val if isinstance(val, (dict, list)) else None

        retrieval_model = parse_json_param("retrieval_model")
        partial_member_list = parse_json_param("partial_member_list")
        external_retrieval_model = parse_json_param("external_retrieval_model")

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

            # Update the dataset
            result = api.update_dataset(
                dataset_id=dataset_id,
                name=name,
                description=description,
                indexing_technique=indexing_technique,
                permission=permission,
                embedding_model=embedding_model,
                embedding_model_provider=embedding_model_provider,
                retrieval_model=retrieval_model,
                partial_member_list=partial_member_list,
                external_retrieval_model=external_retrieval_model,
                external_knowledge_id=external_knowledge_id,
                external_knowledge_api_id=external_knowledge_api_id
            )

            # Create response
            updated_name = result.get("name", "Unknown")
            summary = f"Dataset '{updated_name}' (ID: {dataset_id}) updated successfully."
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating dataset: {str(e)}")
            return
