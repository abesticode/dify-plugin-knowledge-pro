from typing import Any

from dify_plugin import ToolProvider


class KnowledgeProProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        No provider-level credentials to validate.
        API key and base URL are provided as parameters on each tool call.
        """
        pass
