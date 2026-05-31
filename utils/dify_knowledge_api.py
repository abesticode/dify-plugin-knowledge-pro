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
        files: Optional[dict] = None,
        timeout: int = 60
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Dify API.

        Args:
            method: HTTP method (GET, POST, DELETE, PATCH)
            endpoint: API endpoint path
            data: Request body data (JSON or form data)
            params: Query parameters
            files: Dictionary of file objects for multipart upload
            timeout: Request timeout in seconds

        Returns:
            dict: Response data
        """
        url = f"{self.base_url}{endpoint}"
        
        req_headers = dict(self.headers)
        if files and "Content-Type" in req_headers:
            # Let requests automatically set Content-Type to multipart/form-data
            del req_headers["Content-Type"]

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=req_headers,
                json=data if data and not files else None,
                data=data if data and files else None,
                params=params,
                files=files,
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

    def create_dataset(
        self,
        name: str,
        description: Optional[str] = None,
        indexing_technique: Optional[str] = None,
        permission: str = "only_me",
        provider: str = "vendor",
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
        retrieval_model: Optional[dict] = None,
        external_knowledge_api_id: Optional[str] = None,
        external_knowledge_id: Optional[str] = None,
        summary_index_setting: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Create an empty knowledge base.
        """
        data = {
            "name": name,
            "permission": permission,
            "provider": provider
        }
        if description is not None:
            data["description"] = description
        if indexing_technique is not None:
            data["indexing_technique"] = indexing_technique
        if embedding_model is not None:
            data["embedding_model"] = embedding_model
        if embedding_model_provider is not None:
            data["embedding_model_provider"] = embedding_model_provider
        if retrieval_model is not None:
            data["retrieval_model"] = retrieval_model
        if external_knowledge_api_id is not None:
            data["external_knowledge_api_id"] = external_knowledge_api_id
        if external_knowledge_id is not None:
            data["external_knowledge_id"] = external_knowledge_id
        if summary_index_setting is not None:
            data["summary_index_setting"] = summary_index_setting

        return self._make_request(
            method="POST",
            endpoint="/datasets",
            data=data
        )

    def list_datasets(
        self,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        include_all: bool = False,
        tag_ids: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Get the list of knowledge bases.
        """
        params = {"page": page, "limit": limit}
        if keyword is not None:
            params["keyword"] = keyword
        if include_all:
            params["include_all"] = "true"
        if tag_ids:
            # Depending on how the API expects array, sometimes it's repeated or comma separated
            # Dify docs specify it as string[]. Let's try sending as multiple params or passing a list directly.
            # requests handles list properly if passed as `tag_ids=...`
            params["tag_ids"] = tag_ids

        return self._make_request(
            method="GET",
            endpoint="/datasets",
            params=params
        )

    def get_dataset(self, dataset_id: str) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific knowledge base.
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}"
        )

    def delete_dataset(self, dataset_id: str) -> dict[str, Any]:
        """
        Delete a knowledge base.
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}"
        )

    def update_dataset(
        self,
        dataset_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        indexing_technique: Optional[str] = None,
        permission: Optional[str] = None,
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
        retrieval_model: Optional[dict] = None,
        partial_member_list: Optional[list[dict]] = None,
        external_retrieval_model: Optional[dict] = None,
        external_knowledge_id: Optional[str] = None,
        external_knowledge_api_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Update an existing knowledge base.
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if indexing_technique is not None:
            data["indexing_technique"] = indexing_technique
        if permission is not None:
            data["permission"] = permission
        if embedding_model is not None:
            data["embedding_model"] = embedding_model
        if embedding_model_provider is not None:
            data["embedding_model_provider"] = embedding_model_provider
        if retrieval_model is not None:
            data["retrieval_model"] = retrieval_model
        if partial_member_list is not None:
            data["partial_member_list"] = partial_member_list
        if external_retrieval_model is not None:
            data["external_retrieval_model"] = external_retrieval_model
        if external_knowledge_id is not None:
            data["external_knowledge_id"] = external_knowledge_id
        if external_knowledge_api_id is not None:
            data["external_knowledge_api_id"] = external_knowledge_api_id

        return self._make_request(
            method="PATCH",
            endpoint=f"/datasets/{dataset_id}",
            data=data
        )

    # ==================== Document Operations ====================

    def create_document_by_text(
        self,
        dataset_id: str,
        name: str,
        text: str,
        indexing_technique: Optional[str] = None,
        doc_form: str = "text_model",
        doc_language: str = "English",
        process_rule: Optional[dict] = None,
        retrieval_model: Optional[dict] = None,
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
        original_document_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a document from text.
        """
        data = {
            "name": name,
            "text": text,
            "doc_form": doc_form,
            "doc_language": doc_language
        }
        
        if indexing_technique:
            data["indexing_technique"] = indexing_technique
        if process_rule:
            data["process_rule"] = process_rule
        if retrieval_model:
            data["retrieval_model"] = retrieval_model
        if embedding_model:
            data["embedding_model"] = embedding_model
        if embedding_model_provider:
            data["embedding_model_provider"] = embedding_model_provider
        if original_document_id:
            data["original_document_id"] = original_document_id

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/document/create-by-text",
            data=data
        )

    def create_document_by_file(
        self,
        dataset_id: str,
        file_path: str,
        data_config: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Create a document by uploading a file.
        Requires requests handling multipart/form-data.
        """
        url = f"{self.base_url}/datasets/{dataset_id}/document/create-by-file"
        
        try:
            import json
            import os
            
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")
                
            with open(file_path, "rb") as f:
                files = {"file": f}
                payload = {}
                if data_config:
                    payload["data"] = json.dumps(data_config)
                
                # We need a copy of headers without Content-Type so requests can set multipart boundary automatically
                headers = self.headers.copy()
                if "Content-Type" in headers:
                    del headers["Content-Type"]
                    
                response = requests.request(
                    method="POST",
                    url=url,
                    headers=headers,
                    data=payload,
                    files=files,
                    timeout=60
                )
                
            if response.status_code in [200, 201]:
                return response.json()
                
            error_message = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_message = error_data.get("message", error_data.get("error", error_message))
            except Exception:
                error_message = response.text or error_message
            raise Exception(error_message)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def update_document_by_text(
        self,
        dataset_id: str,
        document_id: str,
        name: Optional[str] = None,
        text: Optional[str] = None,
        process_rule: Optional[dict] = None,
        doc_form: Optional[str] = None,
        doc_language: Optional[str] = None,
        retrieval_model: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Update a document with text.
        """
        data = {}
        if name:
            data["name"] = name
        if text:
            data["text"] = text
        if process_rule:
            data["process_rule"] = process_rule
        if doc_form:
            data["doc_form"] = doc_form
        if doc_language:
            data["doc_language"] = doc_language
        if retrieval_model:
            data["retrieval_model"] = retrieval_model

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/update-by-text",
            data=data
        )

    def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        file_path: Optional[str] = None,
        data_config: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Update a document by uploading a file.
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}/update-by-file"
        
        try:
            import json
            import os
            
            files = {}
            f_handle = None
            if file_path and os.path.exists(file_path):
                f_handle = open(file_path, "rb")
                files = {"file": f_handle}
                
            payload = {}
            if data_config:
                payload["data"] = json.dumps(data_config)
            
            headers = self.headers.copy()
            if "Content-Type" in headers:
                del headers["Content-Type"]
                
            response = requests.request(
                method="POST",
                url=url,
                headers=headers,
                data=payload,
                files=files if files else None,
                timeout=60
            )
            
            if f_handle:
                f_handle.close()
                
            if response.status_code in [200, 201]:
                return response.json()
                
            error_message = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_message = error_data.get("message", error_data.get("error", error_message))
            except Exception:
                error_message = response.text or error_message
            raise Exception(error_message)

        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def list_documents(
        self,
        dataset_id: str,
        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get the document list of a knowledge base.

        Args:
            dataset_id: The ID of the dataset
            keyword: Optional search keyword to filter documents by name
            page: Page number
            limit: Number of items per page
            status: Optional filter by document display status

        Returns:
            dict: List of documents with pagination info
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword
        if status:
            params["status"] = status

        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents",
            params=params
        )

    def get_document(
        self,
        dataset_id: str,
        document_id: str,
        metadata: str = "all"
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific document.
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}",
            params={"metadata": metadata}
        )

    # ==================== Tag Operations ====================

    def list_workspace_tags(self) -> dict[str, Any]:
        """
        Returns the list of all knowledge base tags in the workspace.
        """
        return self._make_request(
            method="GET",
            endpoint="/datasets/tags"
        )

    def create_tag(self, name: str) -> dict[str, Any]:
        """
        Create a new tag for organizing knowledge bases.
        """
        return self._make_request(
            method="POST",
            endpoint="/datasets/tags",
            data={"name": name}
        )

    def delete_tag(self, tag_id: str) -> dict[str, Any]:
        """
        Permanently delete a knowledge base tag.
        """
        return self._make_request(
            method="DELETE",
            endpoint="/datasets/tags",
            data={"tag_id": tag_id}
        )

    def update_tag(self, tag_id: str, name: str) -> dict[str, Any]:
        """
        Rename an existing knowledge base tag.
        """
        return self._make_request(
            method="PATCH",
            endpoint="/datasets/tags",
            data={"tag_id": tag_id, "name": name}
        )

    def bind_tags(self, target_id: str, tag_ids: list[str]) -> dict[str, Any]:
        """
        Bind one or more tags to a knowledge base.
        """
        return self._make_request(
            method="POST",
            endpoint="/datasets/tags/binding",
            data={"target_id": target_id, "tag_ids": tag_ids}
        )

    def unbind_tags(self, target_id: str, tag_ids: list[str]) -> dict[str, Any]:
        """
        Remove one or more tags from a knowledge base.
        """
        return self._make_request(
            method="POST",
            endpoint="/datasets/tags/unbinding",
            data={"target_id": target_id, "tag_ids": tag_ids}
        )

    def list_dataset_tags(self, dataset_id: str) -> dict[str, Any]:
        """
        Returns the list of tags bound to a specific knowledge base.
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/tags"
        )

    def delete_document(self, dataset_id: str, document_id: str) -> dict[str, Any]:
        """
        Delete a document.
        """
        return self._make_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}"
        )
        
    def download_document(self, dataset_id: str, document_id: str) -> dict[str, Any]:
        """
        Get a signed download URL for a document's original uploaded file.
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/download"
        )

    def get_indexing_status(self, dataset_id: str, batch: str) -> dict[str, Any]:
        """
        Get document embedding status (progress).
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{batch}/indexing-status"
        )

    def download_documents_as_zip(self, dataset_id: str, document_ids: list[str]) -> bytes:
        """
        Download multiple uploaded-file documents as a single ZIP archive.
        Returns the raw ZIP bytes.
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/download-zip"
        
        try:
            response = requests.request(
                method="POST",
                url=url,
                headers=self.headers,
                json={"document_ids": document_ids},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.content
                
            error_message = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_message = error_data.get("message", error_data.get("error", error_message))
            except Exception:
                error_message = response.text or error_message
            raise Exception(error_message)

        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def update_document_status_in_batch(self, dataset_id: str, action: str, document_ids: list[str]) -> dict[str, Any]:
        """
        Enable, disable, archive, or unarchive multiple documents at once.
        action options: enable, disable, archive, un_archive
        """
        return self._make_request(
            method="PATCH",
            endpoint=f"/datasets/{dataset_id}/documents/status/{action}",
            data={"document_ids": document_ids}
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
        document_id: str,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get chunks from a document.
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword
        if status:
            params["status"] = status
            
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/segments",
            params=params
        )

    def update_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: Optional[str] = None,
        answer: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        enabled: Optional[bool] = None,
        regenerate_child_chunks: Optional[bool] = None,
        attachment_ids: Optional[list[str]] = None,
        summary: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Update a chunk in a document.
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
        if regenerate_child_chunks is not None:
            segment["regenerate_child_chunks"] = regenerate_child_chunks
        if attachment_ids is not None:
            segment["attachment_ids"] = attachment_ids
        if summary is not None:
            segment["summary"] = summary

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
        reranking_model_name: Optional[str] = None,
        external_retrieval_model: Optional[dict] = None,
        attachment_ids: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Retrieve chunks from a knowledge base.
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
        
        data = {
            "query": query, 
            "retrieval_model": retrieval_model
        }
        
        if external_retrieval_model is not None:
            data["external_retrieval_model"] = external_retrieval_model
        
        if attachment_ids is not None:
            data["attachment_ids"] = attachment_ids

        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/retrieve",
            data=data
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
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword
        
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

    def list_built_in_metadata(self, dataset_id: str) -> dict[str, Any]:
        """
        Returns the list of built-in metadata fields.
        """
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/metadata/built-in"
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
            method="POST",
            endpoint=f"/datasets/{dataset_id}/metadata/built-in/{action}"
        )

    # ==================== Models Operations ====================

    def list_available_models(self, model_type: str) -> dict[str, Any]:
        """
        Retrieve the list of available models by type.

        Args:
            model_type: Type of model to retrieve (e.g. text-embedding, rerank)
        
        Returns:
            dict: Available models for the specified type
        """
        return self._make_request(
            method="GET",
            endpoint=f"/workspaces/current/models/model-types/{model_type}"
        )

    # ==================== Pipeline Operations ====================

    def upload_pipeline_file(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str = "application/octet-stream"
    ) -> dict[str, Any]:
        """Upload a file for use in a knowledge pipeline."""
        files = {"file": (file_name, file_content, mime_type)}
        return self._make_request(
            method="POST",
            endpoint="/datasets/pipeline/file-upload",
            files=files
        )

    def list_datasource_plugins(
        self,
        dataset_id: str,
        is_published: bool = True
    ) -> dict[str, Any]:
        """List the datasource nodes configured in the knowledge pipeline."""
        return self._make_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/pipeline/datasource-plugins",
            params={"is_published": str(is_published).lower()}
        )

    def run_datasource_node(
        self,
        dataset_id: str,
        node_id: str,
        inputs: dict[str, Any],
        datasource_type: str,
        is_published: bool = True,
        credential_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Execute a single datasource node within the knowledge pipeline."""
        payload = {
            "inputs": inputs,
            "datasource_type": datasource_type,
            "is_published": is_published
        }
        if credential_id:
            payload["credential_id"] = credential_id
            
        # The API returns Server-Sent Events stream, but we will try to parse JSON if blocking isn't an option
        # Or just return the raw text if JSON fails
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/pipeline/datasource/nodes/{node_id}/run",
            data=payload
        )

    def run_pipeline(
        self,
        dataset_id: str,
        inputs: dict[str, Any],
        datasource_type: str,
        datasource_info_list: list[dict[str, Any]],
        start_node_id: str,
        is_published: bool = True,
        response_mode: str = "blocking"
    ) -> dict[str, Any]:
        """Execute the full knowledge pipeline for a knowledge base."""
        payload = {
            "inputs": inputs,
            "datasource_type": datasource_type,
            "datasource_info_list": datasource_info_list,
            "start_node_id": start_node_id,
            "is_published": is_published,
            "response_mode": response_mode
        }
        return self._make_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/pipeline/run",
            data=payload
        )

