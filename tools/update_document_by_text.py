import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI


class UpdateDocumentByTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a document with text in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_id = tool_parameters.get("document_id", "")
        name = tool_parameters.get("name")
        text = tool_parameters.get("text")
        doc_form = tool_parameters.get("doc_form")
        doc_language = tool_parameters.get("doc_language")

        def parse_json_param(param_name):
            val = tool_parameters.get(param_name)
            if val and isinstance(val, str):
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    pass
            return val if isinstance(val, dict) else None

        process_rule = parse_json_param("process_rule")
        retrieval_model = parse_json_param("retrieval_model")

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
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

            # Update document
            result = api.update_document_by_text(
                dataset_id=dataset_id,
                document_id=document_id,
                name=name,
                text=text,
                process_rule=process_rule,
                doc_form=doc_form,
                doc_language=doc_language,
                retrieval_model=retrieval_model
            )

            # Create response
            doc_obj = result.get("document", {})
            batch = result.get("batch", "")
            
            summary = f"Document updated successfully. Batch: {batch}"
            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error updating document: {str(e)}")
            return
