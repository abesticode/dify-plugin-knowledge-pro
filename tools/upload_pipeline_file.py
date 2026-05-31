import os
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.dify_knowledge_api import DifyKnowledgeAPI


class UploadPipelineFileTool(Tool):
    """
    Tool for uploading a file for use in a knowledge pipeline.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Upload a file to the knowledge pipeline.
        """
        # Get credentials
        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url")

        if not api_key or not base_url:
            yield self.create_text_message("API key and base URL are required.")
            return

        file_path = tool_parameters.get("file_path", "").strip()
        mime_type = tool_parameters.get("mime_type", "application/octet-stream").strip()

        if not file_path:
            yield self.create_text_message("File path is required.")
            return

        if not os.path.exists(file_path):
            yield self.create_text_message(f"File not found at path: {file_path}")
            return

        file_name = os.path.basename(file_path)

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            api = DifyKnowledgeAPI(api_key, base_url)
            result = api.upload_pipeline_file(
                file_content=file_content,
                file_name=file_name,
                mime_type=mime_type
            )

            file_id = result.get("id", "Unknown")
            
            summary = f"Successfully uploaded file '{file_name}' to pipeline. (ID: {file_id})"

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
