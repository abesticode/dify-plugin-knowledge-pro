from collections.abc import Generator
from typing import Any
import json
import time

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


DEFAULT_INDEXING_TECHNIQUE = "high_quality"
DEFAULT_PROCESS_RULE = {"mode": "automatic"}


class CreateDocumentByTextTool(Tool):
    """
    Create a new document or update existing document by name in a Dify knowledge base.
    Supports advanced options like chunk method, document language, custom process rules, and metadata.
    """

    def _validate_pre_processing_rules(self, pre_processing_rules: list | None):
        """Validate pre-processing rules structure."""
        if pre_processing_rules is None:
            raise ValueError("Process rule pre_processing_rules is required for custom/hierarchical mode")
        for rule in pre_processing_rules:
            if not rule.get("id"):
                raise ValueError("Process rule pre_processing_rules id is required")
            if not isinstance(rule.get("enabled"), bool):
                raise ValueError("Process rule pre_processing_rules enabled must be a boolean")

    def _validate_segmentation_rules(self, segmentation: dict | None, mode: str, parent_mode: str | None):
        """Validate segmentation rules structure."""
        if segmentation is None:
            raise ValueError("Process rule segmentation is required for custom/hierarchical mode")

        separator = segmentation.get("separator")
        if separator is None:
            raise ValueError("Process rule segmentation separator is required")
        if not isinstance(separator, str):
            raise ValueError("Process rule segmentation separator must be a string")

        # max_tokens is required unless mode is hierarchical and parent_mode is full-doc
        if not (mode == "hierarchical" and parent_mode == "full-doc"):
            max_tokens = segmentation.get("max_tokens")
            if max_tokens is None:
                raise ValueError("Process rule segmentation max_tokens is required")
            if not isinstance(max_tokens, int):
                raise ValueError("Process rule segmentation max_tokens must be an integer")

    def _validate_process_rule_structure(self, process_rule: dict[str, Any]):
        """Validate the complete process rule structure."""
        mode = process_rule.get("mode")
        if mode not in ["automatic", "custom", "hierarchical"]:
            raise ValueError(f"Invalid process_rule mode: {mode}. Must be 'automatic', 'custom', or 'hierarchical'")

        if mode in ["custom", "hierarchical"]:
            rules = process_rule.get("rules")
            if not rules:
                raise ValueError("Process rule 'rules' is required for custom or hierarchical mode")

            self._validate_pre_processing_rules(rules.get("pre_processing_rules"))
            self._validate_segmentation_rules(rules.get("segmentation"), mode, rules.get("parent_mode"))

    def _resolve_indexing_technique(self, indexing_technique: Any) -> str:
        """Resolve and validate indexing technique."""
        if indexing_technique is None:
            return DEFAULT_INDEXING_TECHNIQUE

        if isinstance(indexing_technique, str):
            stripped = indexing_technique.strip()
            if not stripped:
                return DEFAULT_INDEXING_TECHNIQUE
            return stripped

        raise ValueError("indexing_technique must be a string")

    def _load_process_rule(self, process_rule_raw: Any) -> dict[str, Any]:
        """Load and validate process rule from JSON string."""
        if process_rule_raw is None:
            process_rule = DEFAULT_PROCESS_RULE.copy()
            self._validate_process_rule_structure(process_rule)
            return process_rule

        if not isinstance(process_rule_raw, str):
            raise ValueError("process_rule must be provided as a JSON string")

        process_rule_str = process_rule_raw.strip()
        if not process_rule_str:
            process_rule = DEFAULT_PROCESS_RULE.copy()
            self._validate_process_rule_structure(process_rule)
            return process_rule

        process_rule = json.loads(process_rule_str)
        self._validate_process_rule_structure(process_rule)
        return process_rule

    def _load_metadata(self, metadata_raw: Any) -> list[dict[str, Any]] | None:
        """Load and validate metadata from JSON string."""
        if metadata_raw is None:
            return None

        if not isinstance(metadata_raw, str):
            raise ValueError("metadata_json must be provided as a JSON string")

        metadata_str = metadata_raw.strip()
        if not metadata_str:
            return None

        metadata = json.loads(metadata_str)
        if not isinstance(metadata, list):
            raise ValueError("metadata_json must be a JSON array")

        for item in metadata:
            if not isinstance(item, dict):
                raise ValueError("Each metadata item must be an object")
            if not item.get("id"):
                raise ValueError("Each metadata item must have an 'id' field")
            if not item.get("name"):
                raise ValueError("Each metadata item must have a 'name' field")
            if "value" not in item:
                raise ValueError("Each metadata item must have a 'value' field")

        return metadata

    def _find_document_id_by_name(
        self, base_url: str, headers: dict[str, str], document_name: str
    ) -> str | None:
        """Find document ID by exact name match."""
        params = {"keyword": document_name, "limit": 100, "page": 1}
        response = httpx.get(f"{base_url}/documents", headers=headers, params=params, timeout=60)
        self._raise_for_status(response, "Failed to query existing documents")

        try:
            payload = response.json()
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Unexpected response while searching documents: {error}") from error

        if not isinstance(payload, dict):
            return None

        documents = payload.get("data")
        if not isinstance(documents, list):
            return None

        for item in documents:
            if isinstance(item, dict) and item.get("name") == document_name:
                doc_id = item.get("id")
                if isinstance(doc_id, str) and doc_id:
                    return doc_id
        return None

    def _assign_metadata(
        self,
        base_url: str,
        headers: dict[str, str],
        dataset_id: str,
        document_id: str,
        metadata_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Assign metadata to a document."""
        url = f"{base_url}/datasets/{dataset_id}/documents/metadata"
        data = {
            "operation_data": [
                {
                    "document_id": document_id,
                    "metadata_list": metadata_list
                }
            ]
        }
        
        try:
            response = httpx.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                return {
                    "success": True, 
                    "message": "Metadata assigned successfully"
                }
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", error_json.get("error", response.text))
                except:
                    pass
                return {
                    "success": False, 
                    "message": f"Metadata assignment failed (HTTP {response.status_code}): {error_detail}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Metadata assignment error: {str(e)}"
            }

    @staticmethod
    def _raise_for_status(response: httpx.Response, message: str) -> None:
        """Raise an exception if the response indicates an error."""
        if 200 <= response.status_code < 300:
            return

        detail: str | None = None
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                detail = (
                    parsed.get("message")
                    or parsed.get("error")
                    or parsed.get("detail")
                )
        except json.JSONDecodeError:
            parsed = response.text
            if parsed:
                detail = parsed

        if detail:
            raise RuntimeError(f"{message}: {detail}")

        raise RuntimeError(f"{message}: HTTP {response.status_code}")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new document or update an existing document by name.
        """
        # Get credentials
        api_secret = self.runtime.credentials.get("api_key")
        base_url_credential = self.runtime.credentials.get("base_url")

        if not api_secret:
            yield self.create_text_message("API key is required.")
            return
        if not base_url_credential:
            yield self.create_text_message("Base URL is required.")
            return

        # Get parameters
        dataset_id = tool_parameters.get("dataset_id", "")
        document_name = tool_parameters.get("name", "")
        text = tool_parameters.get("text", "")

        # Validate required parameters
        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return
        if not document_name:
            yield self.create_text_message("Document name is required.")
            return
        if not text:
            yield self.create_text_message("Text content is required.")
            return

        try:
            base_url = base_url_credential.rstrip("/")
            dataset_base_url = f"{base_url}/datasets/{dataset_id}"
            headers = {
                "Authorization": f"Bearer {api_secret}",
                "Content-Type": "application/json",
            }

            # Build request data
            data = {
                "text": text,
                "name": document_name,
                "indexing_technique": self._resolve_indexing_technique(
                    tool_parameters.get("indexing_technique")
                ),
            }

            # Add optional doc_form
            doc_form = tool_parameters.get("doc_form")
            if doc_form not in (None, ""):
                data["doc_form"] = doc_form

            # Add optional doc_language
            doc_language = tool_parameters.get("doc_language")
            if doc_language not in (None, ""):
                data["doc_language"] = doc_language

            # Load and validate process_rule
            try:
                process_rule = self._load_process_rule(tool_parameters.get("process_rule"))
                data["process_rule"] = process_rule
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"Invalid JSON format for process_rule: {e}")
                return
            except ValueError as e:
                yield self.create_text_message(f"Invalid process_rule: {e}")
                return

            # Load metadata
            metadata_list = None
            try:
                metadata_list = self._load_metadata(tool_parameters.get("metadata_json"))
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"Invalid JSON format for metadata_json: {e}")
                return
            except ValueError as e:
                yield self.create_text_message(f"Invalid metadata_json: {e}")
                return

            # Check if document with this name already exists
            existing_document_id = self._find_document_id_by_name(dataset_base_url, headers, document_name)

            if existing_document_id:
                # Update existing document
                operation = "update"
                url = f"{dataset_base_url}/documents/{existing_document_id}/update-by-text"
            else:
                # Create new document
                operation = "create"
                url = f"{dataset_base_url}/document/create-by-text"

            # Make the API request
            response = httpx.post(url, headers=headers, json=data, timeout=120)
            self._raise_for_status(response, f"Failed to {operation} document")

            result = response.json()
            result["operation"] = operation

            # Extract document ID from the response
            final_document_id = None
            
            # For create operation, document ID is in result["document"]["id"]
            if isinstance(result, dict):
                doc_obj = result.get("document")
                if isinstance(doc_obj, dict):
                    final_document_id = doc_obj.get("id")
            
            # For update operation, use the existing document ID
            if not final_document_id and existing_document_id:
                final_document_id = existing_document_id
                if isinstance(result, dict) and "document" not in result:
                    result["document"] = {"id": existing_document_id}

            # Assign metadata if provided and we have a document ID
            metadata_result = None
            if metadata_list and final_document_id:
                # Small delay to ensure document is registered in the system
                time.sleep(1)
                
                metadata_result = self._assign_metadata(
                    base_url,
                    headers,
                    dataset_id,
                    final_document_id,
                    metadata_list
                )
                result["metadata_assignment"] = metadata_result

            # Create response messages
            doc_info = result.get("document", {}) if isinstance(result, dict) else {}
            doc_id_display = doc_info.get("id", final_document_id or "N/A")
            batch = result.get("batch", "") if isinstance(result, dict) else ""

            summary_parts = [
                f"Document '{document_name}' {operation}d successfully.",
                f"ID: {doc_id_display}",
            ]
            if batch:
                summary_parts.append(f"Batch: {batch}")
            if metadata_result:
                if metadata_result.get("success"):
                    summary_parts.append("Metadata assigned successfully.")
                else:
                    summary_parts.append(f"Metadata warning: {metadata_result.get('message')}")
            elif metadata_list:
                summary_parts.append("Warning: Metadata was provided but could not be assigned (no document ID).")

            yield self.create_text_message(" ".join(summary_parts))
            yield self.create_json_message(result)

        except httpx.TimeoutException:
            yield self.create_text_message("Request timed out. The document may still be processing.")
            return
        except RuntimeError as e:
            yield self.create_text_message(str(e))
            return
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
            return
