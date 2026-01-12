from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dify_knowledge_api import DifyKnowledgeAPI
from utils.cost_calculator import CostCalculator


class AddChunksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Add chunks (segments) to a document in a Dify knowledge base.
        """
        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "").strip()
        document_id = tool_parameters.get("document_id", "").strip()
        content = tool_parameters.get("content", "").strip()
        answer = tool_parameters.get("answer", "").strip()
        keywords_str = tool_parameters.get("keywords", "").strip()

        # Validate parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_id:
            yield self.create_text_message("Document ID is required.")
            return
        if not content:
            yield self.create_text_message("Chunk content is required.")
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

            # Parse keywords
            keywords = []
            if keywords_str:
                keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

            # Build segment object
            segment = {"content": content}
            if answer:
                segment["answer"] = answer
            if keywords:
                segment["keywords"] = keywords

            # Add chunks
            result = api.add_chunks(
                dataset_id=dataset_id,
                document_id=document_id,
                segments=[segment]
            )

            # Create response with token usage info
            data = result.get("data", [])
            if data:
                chunk_data = data[0]
                chunk_id = chunk_data.get("id", "N/A")
                word_count = chunk_data.get("word_count", 0)
                tokens = chunk_data.get("tokens", 0)
                status = chunk_data.get("status", "processing")
                
                # Determine if tokens are actual or estimated
                if tokens and tokens > 0:
                    is_estimated = False
                    token_count = tokens
                else:
                    is_estimated = True
                    token_count = int(len(content) / 4)  # Estimate
                
                # Add cost info to result for easy JSON extraction
                result["cost_info"] = cost_calc.get_cost_info(token_count, is_estimated=is_estimated)
                result["cost_info"]["word_count"] = word_count
                
                summary = f"✅ Chunk added successfully!\n\n"
                summary += f"📊 **Chunk Information:**\n"
                summary += f"- Chunk ID: `{chunk_id}`\n"
                summary += f"- Word Count: {word_count}\n"
                summary += f"- Tokens: {tokens if tokens else f'~{token_count} (estimated)'}\n"
                summary += f"- Status: {status}\n"
                
                # Add cost information using configured model
                if not is_estimated:
                    summary += cost_calc.format_cost_message(token_count)
                else:
                    summary += cost_calc.format_estimated_cost_message(token_count)
            else:
                summary = "Chunk added but no data returned."
                result["cost_info"] = None

            yield self.create_text_message(summary)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error adding chunk: {str(e)}")
            return
