from typing import Literal

from typing_extensions import TypeVar

from src.llm import AnthropicClient, LlmClient, OpenAIClient

ProviderType = TypeVar("ProviderType", bound=Literal["anthropic", "openai"])


def get_llm_client(provider: ProviderType = "anthropic") -> LlmClient:
    """Factory function to get an LlmClient implementation based on provider.

    This demonstrates how clients can be used interchangeably through the Protocol.

    Args:
        provider: The LLM provider to use ('anthropic' or 'openai')

    Returns:
        An LlmClient implementation

    Raises:
        ValueError: If an invalid provider is specified
    """
    if provider.lower() == "anthropic":
        return AnthropicClient()
    elif provider.lower() == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
