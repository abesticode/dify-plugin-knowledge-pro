from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class ListAvailableModelsTool(Tool):
    """
    Tool for listing available models by type in the workspace.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        List available models by type in the workspace.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        model_type = tool_parameters.get("model_type", "").strip()

        if not model_type:
            yield self.create_text_message("Model type is required.")
            return

        try:
            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.list_available_models(model_type=model_type)

            providers = result.get("data", [])

            summary = f"Found {len(providers)} provider(s) for model type '{model_type}':\n\n"
            
            for provider_idx, provider_data in enumerate(providers, 1):
                provider = provider_data.get("provider", "Unknown")
                status = provider_data.get("status", "N/A")
                models = provider_data.get("models", [])
                
                summary += f"{provider_idx}. Provider: {provider} (Status: {status})\n"
                
                for model_idx, model_data in enumerate(models, 1):
                    model = model_data.get("model", "Unknown")
                    model_status = model_data.get("status", "N/A")
                    summary += f"   - Model: {model} | Status: {model_status}\n"

                summary += "\n"

            if not providers:
                summary = f"No models found for type '{model_type}'."

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
