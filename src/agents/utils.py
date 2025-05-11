"""Utility functions for agent configuration and usage."""

import os
from typing import Optional

import anthropic
import openai
from dotenv import load_dotenv
from pydantic_ai import settings

# Load environment variables
load_dotenv()

# Define provider types
ANTHROPIC = "anthropic"
OPENAI = "openai"


def get_model_from_settings():
    """Get the configured model from pydantic_ai settings.

    Returns:
        str: The model name to use based on the configured provider
    """
    provider = settings.model_provider

    if provider == "anthropic":
        return settings.anthropic_model_name
    elif provider == "openai":
        return settings.openai_model_name
    else:
        # Default to Anthropic model if provider is not recognized
        return "claude-3-sonnet-20240229"


def configure_pydantic_ai(provider: str = ANTHROPIC) -> None:
    """Configure Pydantic AI with the specified provider.

    Args:
        provider: The LLM provider to use (anthropic or openai)

    Raises:
        ValueError: If the required API key is not set in environment variables
    """
    # Configure provider-specific settings
    if provider == ANTHROPIC:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required in environment variables.")

        # Set Anthropic-specific settings
        model_name = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-sonnet-20240229")

        # Configure anthropic client
        settings.anthropic_api_key = api_key
        settings.anthropic_model_name = model_name
        settings.model_provider = "anthropic"

    elif provider == OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required in environment variables.")

        # Set OpenAI-specific settings
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

        # Configure OpenAI client
        settings.openai_api_key = api_key
        settings.openai_model_name = model_name
        settings.model_provider = "openai"

    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Additional common settings
    settings.max_retries = int(os.getenv("LLM_MAX_RETRIES", "5"))
