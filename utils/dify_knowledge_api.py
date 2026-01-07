"""
Utility module for Dify Knowledge Base API interactions.
"""
from typing import Any, Optional
import requests


class DifyKnowledgeAPI:
    """
    A utility class for interacting with the Dify Knowledge Base API.
    """

    def __init__(self, api_key: str, base_url: str):
        """
        Initialize the Dify Knowledge API client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL of the Dify API (e.g., https://api.dify.ai/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: int = 60
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Dify API.

        Args:
            method: HTTP method (GET, POST, DELETE, PATCH)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            dict: Response data

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data if data else None,
                params=params,
                timeout=timeout
            )

            # Handle 204 No Content
            if response.status_code == 204:
                return {"success": True, "message": "Operation completed successfully"}

            # Handle successful response
            if response.status_code in [200, 201]:
                return response.json()

            # Handle errors
            error_message = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_message = error_data["message"]
                elif "error" in error_data:
                    error_message = error_data["error"]
            except Exception:
                error_message = response.text or error_message

            raise Exception(error_message)

        except requests.exceptions.ConnectionError:
            raise Exception("Failed to connect to Dify API. Please check your base URL.")
        except requests.exceptions.Timeout:
            raise Exception("Request to Dify API timed out. Please try again.")

    # ==================== Dataset Operations ====================

    def create_dataset(self, name: str, permission: str = "only_me") -> dict[str, Any]:
        """
        Create an empty knowledge base.

        Args:
            name: The name of the knowledge base
            permission: Permission setting ("only_me" or "all_team_members")

        Returns:
            dict: Created dataset information
        """
        return self._make_request(
            method="POST",
            endpoint="/datasets",
            data={"name": name, "permission": permission}
        )

    def list_datasets(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """
        Get the list of knowledge bases.

        Args:
            page: Page number
            limit: Number of items per page

        Returns:
            dict: List of datasets with pagination info
        """
        return self._make_request(
            method="GET",
            endpoint="/datasets",
            params={"page": page, "limit": limit}
        )

    def delete_dataset(self, dataset_id: str) -> dict[str, Any]:
        """
        Delete a knowledge base.

        Args:
            dataset_id: The ID of the dataset to delete

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}"
        )

    # ==================== Document Operations ====================

    def create_document_by_text(
        self,
        dataset_id: str,
        name: str,
        text: str,
        indexing_technique: str = "high_quality",
        process_rule_mode: str = "automatic"
    ) -> dict[str, Any]:
        """
        Create a document from text.

        Args:
            dataset_id: The ID of the dataset
            name: The name of the document
            text: The text content
            indexing_technique: "high_quality" or "economy"
            process_rule_mode: "automatic" or "custom"

        Returns:
            dict: Created document information
        """
        data = {
            "name": name,
            "text": text,
            "indexing_technique": indexing_technique,
            "process_rule": {"mode": process_rule_mode}
        }
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/document/create_by_text",
            data=data
        )

    def update_document_by_text(
        self,
        dataset_id: str,
        document_id: str,
        name: Optional[str] = None,
        text: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Update a document with text.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            name: New name for the document (optional)
            text: New text content (optional)

        Returns:
            dict: Updated document information
        """
        data = {}
        if name:
            data["name"] = name
        if text:
            data["text"] = text

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/update_by_text",
            data=data
        )

    def list_documents(
        self,
        dataset_id: str,
        page: int = 1,
        limit: int = 20
    ) -> dict[str, Any]:
        """
        Get the document list of a knowledge base.

        Args:
            dataset_id: The ID of the dataset
            page: Page number
            limit: Number of items per page

        Returns:
            dict: List of documents with pagination info
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents",
            params={"page": page, "limit": limit}
        )

    def delete_document(self, dataset_id: str, document_id: str) -> dict[str, Any]:
        """
        Delete a document.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}"
        )

    def get_indexing_status(self, dataset_id: str, batch: str) -> dict[str, Any]:
        """
        Get document embedding status (progress).

        Args:
            dataset_id: The ID of the dataset
            batch: The batch ID from document creation

        Returns:
            dict: Indexing status information
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{batch}/indexing-status"
        )

    # ==================== Chunk/Segment Operations ====================

    def add_chunks(
        self,
        dataset_id: str,
        document_id: str,
        segments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Add chunks to a document.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segments: List of segment objects with content, answer, keywords

        Returns:
            dict: Created segments information
        """
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments",
            data={"segments": segments}
        )

    def list_chunks(
        self,
        dataset_id: str,
        document_id: str
    ) -> dict[str, Any]:
        """
        Get chunks from a document.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document

        Returns:
            dict: List of segments
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments"
        )

    def update_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: Optional[str] = None,
        answer: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        enabled: Optional[bool] = None
    ) -> dict[str, Any]:
        """
        Update a chunk in a document.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the segment
            content: New content (optional)
            answer: New answer (optional)
            keywords: New keywords (optional)
            enabled: Enable/disable the segment (optional)

        Returns:
            dict: Updated segment information
        """
        segment = {}
        if content is not None:
            segment["content"] = content
        if answer is not None:
            segment["answer"] = answer
        if keywords is not None:
            segment["keywords"] = keywords
        if enabled is not None:
            segment["enabled"] = enabled

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}",
            data={"segment": segment}
        )

    def delete_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> dict[str, Any]:
        """
        Delete a chunk in a document.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the segment

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )

    def retrieve_chunks(
        self,
        dataset_id: str,
        query: str,
        search_method: str = "keyword_search",
        top_k: int = 5,
        score_threshold_enabled: bool = False,
        score_threshold: Optional[float] = None,
        reranking_enable: bool = False,
        reranking_provider_name: Optional[str] = None,
        reranking_model_name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Retrieve chunks from a knowledge base.

        Args:
            dataset_id: The ID of the dataset
            query: The search query
            search_method: Search method ("keyword_search", "semantic_search", "full_text_search", "hybrid_search")
            top_k: Number of results to return
            score_threshold_enabled: Whether to enable score threshold
            score_threshold: Minimum score threshold
            reranking_enable: Whether to enable reranking
            reranking_provider_name: Reranking model provider
            reranking_model_name: Reranking model name

        Returns:
            dict: Retrieved records
        """
        retrieval_model = {
            "search_method": search_method,
            "reranking_enable": reranking_enable,
            "reranking_mode": None,
            "reranking_model": {
                "reranking_provider_name": reranking_provider_name or "",
                "reranking_model_name": reranking_model_name or ""
            },
            "weights": None,
            "top_k": top_k,
            "score_threshold_enabled": score_threshold_enabled,
            "score_threshold": score_threshold
        }

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/retrieve",
            data={"query": query, "retrieval_model": retrieval_model}
        )

    def get_chunk_details(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> dict[str, Any]:
        """
        Get details of a specific chunk/segment.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the segment/chunk

        Returns:
            dict: Chunk details including content, status, metadata
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )

    # ==================== Child Chunk Operations ====================

    def list_child_chunks(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> dict[str, Any]:
        """
        Get child chunks from a parent segment.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the parent segment
            keyword: Optional search keyword to filter child chunks
            page: Page number for pagination
            limit: Number of items per page (max 100)

        Returns:
            dict: List of child chunks with pagination info
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["q"] = keyword
        
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks",
            params=params
        )

    def create_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: str
    ) -> dict[str, Any]:
        """
        Create a new child chunk under a parent segment.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the parent segment
            content: The content of the child chunk

        Returns:
            dict: Created child chunk information
        """
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks",
            data={"content": content}
        )

    def update_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        child_chunk_id: str,
        content: str
    ) -> dict[str, Any]:
        """
        Update a child chunk's content.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the parent segment
            child_chunk_id: The ID of the child chunk to update
            content: New content for the child chunk

        Returns:
            dict: Updated child chunk information
        """
        return self._make_request(
            method="PATCH",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks/{child_chunk_id}",
            data={"content": content}
        )

    def delete_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        child_chunk_id: str
    ) -> dict[str, Any]:
        """
        Delete a child chunk.

        Args:
            dataset_id: The ID of the dataset
            document_id: The ID of the document
            segment_id: The ID of the parent segment
            child_chunk_id: The ID of the child chunk to delete

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks/{child_chunk_id}"
        )

    # ==================== Metadata Operations ====================

    def add_metadata_field(
        self,
        dataset_id: str,
        name: str,
        field_type: str = "string"
    ) -> dict[str, Any]:
        """
        Add a metadata field to the knowledge base.

        Args:
            dataset_id: The ID of the dataset
            name: The name of the metadata field
            field_type: The type of the field ("string", "number", "time")

        Returns:
            dict: Created metadata field information
        """
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/metadata",
            data={"type": field_type, "name": name}
        )

    def update_metadata_field(
        self,
        dataset_id: str,
        metadata_id: str,
        name: str
    ) -> dict[str, Any]:
        """
        Update a metadata field in the knowledge base.

        Args:
            dataset_id: The ID of the dataset
            metadata_id: The ID of the metadata field
            name: New name for the metadata field

        Returns:
            dict: Updated metadata field information
        """
        return self._make_request(
            method="PATCH",
            endpoint=f"/datasets/{dataset_id}/metadata/{metadata_id}",
            data={"name": name}
        )

    def delete_metadata_field(
        self,
        dataset_id: str,
        metadata_id: str
    ) -> dict[str, Any]:
        """
        Delete a metadata field from the knowledge base.

        Args:
            dataset_id: The ID of the dataset
            metadata_id: The ID of the metadata field

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/metadata/{metadata_id}"
        )

    def list_metadata(self, dataset_id: str) -> dict[str, Any]:
        """
        Get the metadata list of a dataset.

        Args:
            dataset_id: The ID of the dataset

        Returns:
            dict: List of metadata fields
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/metadata"
        )

    def update_document_metadata(
        self,
        dataset_id: str,
        operation_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Modify metadata for documents.

        Args:
            dataset_id: The ID of the dataset
            operation_data: List of operations with document_id and metadata_list

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/metadata",
            data={"operation_data": operation_data}
        )

    def toggle_built_in_metadata(
        self,
        dataset_id: str,
        action: str
    ) -> dict[str, Any]:
        """
        Enable/Disable built-in metadata fields.

        Args:
            dataset_id: The ID of the dataset
            action: "enable" or "disable"

        Returns:
            dict: Success confirmation
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/metadata/built-in/{action}"
        )
