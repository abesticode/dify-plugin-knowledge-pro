"""
Cost calculator utility for embedding cost estimation.
"""
from typing import Optional


# Embedding model costs per 1M tokens (in USD)
EMBEDDING_COSTS = {
    "text-embedding-ada-002": 0.10,
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
    "cohere-embed-english-v3.0": 0.10,
    "cohere-embed-multilingual-v3.0": 0.10,
    "voyage-large-2": 0.12,
    "voyage-code-2": 0.12,
}


class CostCalculator:
    """
    Utility class for calculating embedding costs based on model configuration.
    """

    def __init__(
        self,
        embedding_model: Optional[str] = None,
        custom_cost_per_1m: Optional[float] = None
    ):
        """
        Initialize the cost calculator.

        Args:
            embedding_model: The embedding model name (from credentials)
            custom_cost_per_1m: Custom cost per 1M tokens (if model is 'custom')
        """
        self.embedding_model = embedding_model or "text-embedding-ada-002"
        self.custom_cost_per_1m = custom_cost_per_1m

    @classmethod
    def from_credentials(cls, credentials: dict) -> "CostCalculator":
        """
        Create a CostCalculator from Dify credentials.

        Args:
            credentials: The runtime credentials dict

        Returns:
            CostCalculator instance
        """
        embedding_model = credentials.get("embedding_model", "text-embedding-ada-002")
        custom_cost_str = credentials.get("embedding_cost_per_1m", "")
        
        custom_cost = None
        if custom_cost_str:
            try:
                custom_cost = float(custom_cost_str)
            except (ValueError, TypeError):
                custom_cost = None
        
        return cls(embedding_model=embedding_model, custom_cost_per_1m=custom_cost)

    def get_cost_per_1m(self) -> float:
        """
        Get the cost per 1M tokens based on configuration.

        Returns:
            float: Cost per 1M tokens in USD
        """
        if self.embedding_model == "custom" and self.custom_cost_per_1m is not None:
            return self.custom_cost_per_1m
        
        return EMBEDDING_COSTS.get(self.embedding_model, 0.10)

    def get_model_name(self) -> str:
        """
        Get the display name of the embedding model.

        Returns:
            str: Model name for display
        """
        if self.embedding_model == "custom":
            return f"Custom (${self.custom_cost_per_1m:.2f}/1M)" if self.custom_cost_per_1m else "Custom"
        return self.embedding_model

    def calculate_cost(self, tokens: int) -> float:
        """
        Calculate the embedding cost for a given number of tokens.

        Args:
            tokens: Number of tokens

        Returns:
            float: Cost in USD
        """
        cost_per_1m = self.get_cost_per_1m()
        return (tokens / 1_000_000) * cost_per_1m

    def get_cost_info(self, tokens: int, is_estimated: bool = False) -> dict:
        """
        Get cost information as a dictionary for JSON response.

        Args:
            tokens: Number of tokens (actual or estimated)
            is_estimated: Whether the tokens value is an estimate

        Returns:
            dict: Cost information with all relevant fields
        """
        cost = self.calculate_cost(tokens)
        cost_per_1m = self.get_cost_per_1m()
        model_name = self.get_model_name()

        return {
            "tokens": tokens,
            "tokens_is_estimated": is_estimated,
            "cost_usd": round(cost, 8),
            "embedding_model": model_name,
            "cost_per_1m_tokens_usd": cost_per_1m,
        }

    def format_cost_message(self, tokens: int, include_model: bool = True) -> str:
        """
        Format a cost message for display.

        Args:
            tokens: Number of tokens
            include_model: Whether to include model name in message

        Returns:
            str: Formatted cost message
        """
        cost = self.calculate_cost(tokens)
        cost_per_1m = self.get_cost_per_1m()
        model_name = self.get_model_name()

        message = f"\n💰 **Embedding Cost:**\n"
        message += f"- Tokens: **{tokens:,}**\n"
        message += f"- Cost: **${cost:.6f}**\n"
        
        if include_model:
            message += f"- Model: {model_name}\n"
            message += f"- Rate: ${cost_per_1m:.2f} / 1M tokens\n"
        
        return message

    def format_estimated_cost_message(self, estimated_tokens: int) -> str:
        """
        Format an estimated cost message (before actual indexing).

        Args:
            estimated_tokens: Estimated number of tokens

        Returns:
            str: Formatted estimated cost message
        """
        cost = self.calculate_cost(estimated_tokens)
        model_name = self.get_model_name()
        cost_per_1m = self.get_cost_per_1m()

        message = f"💰 **Estimated Embedding Cost:**\n"
        message += f"- Estimated Tokens: ~{estimated_tokens:,}\n"
        message += f"- Estimated Cost: ~${cost:.6f}\n"
        message += f"- Model: {model_name}\n"
        message += f"- Rate: ${cost_per_1m:.2f} / 1M tokens\n"
        message += f"- _(Actual tokens may vary after indexing)_\n"
        
        return message
