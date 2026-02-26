"""
Utility module for resolving API credentials from tool parameters.

API key and base URL are provided directly as tool parameters.
No provider-level credentials are used.
"""
from typing import Any, Optional


def resolve_credentials(
    tool_parameters: dict[str, Any],
    runtime_credentials: dict[str, Any] | None = None
) -> tuple[Optional[str], Optional[str]]:
    """
    Resolve API key and base URL from tool parameters.

    Args:
        tool_parameters: The tool's input parameters (should contain api_key, base_url)
        runtime_credentials: Unused (kept for backward compatibility)

    Returns:
        tuple: (api_key, base_url) - resolved credentials
    """
    api_key = (tool_parameters.get("api_key") or "").strip()
    base_url = (tool_parameters.get("base_url") or "").strip()

    return api_key or None, base_url or None
