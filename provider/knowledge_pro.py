from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class KnowledgeProProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Check if api_key is provided
            if "api_key" not in credentials or not credentials.get("api_key"):
                raise ToolProviderCredentialValidationError("Dify API key is required.")

            # Check if base_url is provided
            if "base_url" not in credentials or not credentials.get("base_url"):
                raise ToolProviderCredentialValidationError("Dify API base URL is required.")

            api_key = credentials.get("api_key")
            base_url = credentials.get("base_url", "").rstrip("/")

            # Try to validate credentials by listing datasets
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{base_url}/datasets?page=1&limit=1",
                headers=headers,
                timeout=30
            )

            if response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API key. Please check your credentials.")
            elif response.status_code == 403:
                raise ToolProviderCredentialValidationError("Access forbidden. Please check your API key permissions.")
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"Failed to validate credentials: {response.status_code} - {response.text}"
                )

        except requests.exceptions.ConnectionError:
            raise ToolProviderCredentialValidationError(
                "Failed to connect to Dify API. Please check your base URL."
            )
        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError(
                "Connection to Dify API timed out. Please try again."
            )
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
