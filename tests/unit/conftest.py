"""Test fixtures and mocks for unit tests."""

import json
from typing import Any, Callable, Dict, Optional, Union
from unittest.mock import MagicMock

import pytest
from anthropic import Anthropic
from openai import OpenAI


class SimpleLlmMock:
    """
    A simplified mock for LLM clients that works with both OpenAI and Anthropic interfaces.

    This mock makes it easy to configure responses for tests without complex setup.
    """

    def __init__(self, response: Union[str, Callable] = None):
        """
        Initialize with optional predefined response.

        Args:
            response: String response to return, or a callable that returns a response
        """
        self.response = response or "Default mock response"
        self.last_prompt = None
        self.last_system_prompt = None
        self.last_kwargs = {}

        # Add client-specific mock structures
        self.messages = MagicMock()
        self.chat = MagicMock()
        self.chat.completions = MagicMock()

        # Set up basic methods for both client types
        self.messages.create = self._mock_anthropic_create
        self.chat.completions.create = self._mock_openai_create

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        """
        Record arguments and return the configured response.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters passed to the LLM

        Returns:
            The configured mock response
        """
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        self.last_kwargs = kwargs

        # If response is callable, call it with the inputs
        if callable(self.response):
            return self.response(prompt, system_prompt, **kwargs)
        return self.response

    def _mock_anthropic_create(self, **kwargs: Any):
        """Mock for Anthropic's messages.create method."""
        response_text = self.generate_response(
            kwargs.get("messages", [{}])[0].get("content", ""),
            kwargs.get("system", ""),
            **{k: v for k, v in kwargs.items() if k not in ["messages", "system"]},
        )

        # Store for tests
        self.messages.last_messages = kwargs.get("messages", [])
        self.messages.last_system = kwargs.get("system", "")
        self.messages.last_model = kwargs.get("model", "")

        # Return in Anthropic format
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=response_text)]
        return mock_response

    def _mock_openai_create(self, **kwargs: Any):
        """Mock for OpenAI's chat.completions.create method."""
        system_prompt = None
        user_prompt = ""

        # Extract messages
        for message in kwargs.get("messages", []):
            if message.get("role") == "system":
                system_prompt = message.get("content", "")
            elif message.get("role") == "user":
                user_prompt = message.get("content", "")

        # Generate response
        response_text = self.generate_response(
            user_prompt, system_prompt, **{k: v for k, v in kwargs.items() if k != "messages"}
        )

        # Store for tests
        self.chat.completions.last_messages = kwargs.get("messages", [])
        self.chat.completions.last_model = kwargs.get("model", "")

        # Create OpenAI-style response
        mock_message = MagicMock(content=response_text)
        mock_choice = MagicMock(message=mock_message, finish_reason="stop", index=0)
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        return mock_response

    def rewrite_to_rust(self, python_code: str) -> str:
        """
        Simplified mock for Rust rewriting.

        Args:
            python_code: The Python code to convert

        Returns:
            Mock Rust code
        """
        self.last_prompt = python_code
        if callable(self.response) and "rust" in str(self.response):
            return self.response(python_code)
        return 'fn main() {\n    println!("Hello from Rust");\n}'


@pytest.fixture
def llm_mock():
    """Basic LLM mock that returns a default response."""
    return SimpleLlmMock()


@pytest.fixture
def llm_mock_factory():
    """
    Factory fixture that creates LLM mocks with specified responses.

    Returns a function that creates mock instances with custom responses.
    """

    def _create_mock(response):
        return SimpleLlmMock(response)

    return _create_mock


@pytest.fixture
def license_detector_mock():
    """
    Mock for license detection tests with configurable license types.

    Returns a function that creates mocks with preconfigured license responses.
    """

    def _create_license_response(license_type: str, license_name: str):
        return SimpleLlmMock(json.dumps({"license_type": license_type, "license_name": license_name}))

    return _create_license_response


@pytest.fixture
def function_counter_mock():
    """
    Mock for function counting tests with configurable function counts.

    Returns a function that creates mocks with preconfigured function count responses.
    """

    def _create_counter_response(count: int):
        return SimpleLlmMock(json.dumps({"function_count": count}))

    return _create_counter_response


@pytest.fixture
def function_extractor_mock():
    """
    Mock for function extraction tests with configurable function information.

    Returns a function that creates mocks with preconfigured function information responses.
    """

    def _create_extractor_response(functions: list):
        """
        Create a mock that returns the specified functions list.

        Args:
            functions: List of dictionaries with function information
                (each with 'name' and 'arg_count' keys)
        """
        return SimpleLlmMock(json.dumps(functions))

    return _create_extractor_response


# Client-specific fixtures for backward compatibility
@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    # This wraps our simple mock in a format matching Anthropic's API
    llm_mock = SimpleLlmMock()

    mock_client = MagicMock(spec=Anthropic)
    mock_messages = MagicMock()

    def mock_create(**kwargs: Any):
        # Store parameters for inspection in tests
        response = llm_mock.generate_response(
            kwargs.get("messages", [{}])[0].get("content", ""),
            kwargs.get("system", ""),
            **{k: v for k, v in kwargs.items() if k not in ["messages", "system"]},
        )

        # Make parameters accessible for tests
        mock_messages.last_model = kwargs.get("model", "")
        mock_messages.last_messages = kwargs.get("messages", [])
        mock_messages.last_system = kwargs.get("system", "")

        # Create a response object compatible with Anthropic's structure
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=response)]
        return mock_response

    mock_messages.create = mock_create
    mock_client.messages = mock_messages

    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    # This wraps our simple mock in a format matching OpenAI's API
    llm_mock = SimpleLlmMock()

    mock_client = MagicMock(spec=OpenAI)
    mock_chat = MagicMock()
    mock_completions = MagicMock()

    def mock_create(**kwargs: Any):
        # Extract system prompt and user prompt from messages
        system_prompt = None
        user_prompt = ""

        for message in kwargs.get("messages", []):
            if message.get("role") == "system":
                system_prompt = message.get("content", "")
            elif message.get("role") == "user":
                user_prompt = message.get("content", "")

        # Generate response using our simplified mock
        response = llm_mock.generate_response(
            user_prompt, system_prompt, **{k: v for k, v in kwargs.items() if k != "messages"}
        )

        # Make parameters accessible for tests
        mock_completions.last_model = kwargs.get("model", "")
        mock_completions.last_messages = kwargs.get("messages", [])

        # Create a response object compatible with OpenAI's structure
        mock_message = MagicMock(content=response, role="assistant")
        mock_choice = MagicMock(message=mock_message, index=0, finish_reason="stop")
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        return mock_response

    mock_completions.create = mock_create
    mock_chat.completions = mock_completions
    mock_client.chat = mock_chat

    return mock_client


@pytest.fixture
def mock_anthropic_client_with_custom_response():
    """Factory fixture for creating Anthropic clients with custom responses."""

    def create_client(response_text: str):
        # Use our SimpleLlmMock with fixed response
        llm_mock = SimpleLlmMock(response_text)

        mock_client = MagicMock(spec=Anthropic)
        mock_messages = MagicMock()

        def mock_create(**kwargs):
            # Store parameters for inspection in tests
            response = llm_mock.generate_response(
                kwargs.get("messages", [{}])[0].get("content", ""), kwargs.get("system", "")
            )

            # Make parameters accessible for tests
            mock_messages.last_messages = kwargs.get("messages", [])
            mock_messages.last_system = kwargs.get("system", "")

            # Create a response object compatible with Anthropic's structure
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=response)]
            return mock_response

        mock_messages.create = mock_create
        mock_client.messages = mock_messages

        return mock_client

    return create_client


@pytest.fixture
def mock_openai_client_with_custom_response():
    """Factory fixture for creating OpenAI clients with custom responses."""

    def create_client(response_text: str):
        # Use our SimpleLlmMock with fixed response
        llm_mock = SimpleLlmMock(response_text)

        mock_client = MagicMock(spec=OpenAI)
        mock_chat = MagicMock()
        mock_completions = MagicMock()

        def mock_create(**kwargs):
            # Extract system prompt and user prompt from messages
            system_prompt = None
            user_prompt = ""

            for message in kwargs.get("messages", []):
                if message.get("role") == "system":
                    system_prompt = message.get("content", "")
                elif message.get("role") == "user":
                    user_prompt = message.get("content", "")

            # Generate response using our simplified mock
            response = llm_mock.generate_response(user_prompt, system_prompt)

            # Make parameters accessible for tests
            mock_completions.last_messages = kwargs.get("messages", [])

            # Create a response object compatible with OpenAI's structure
            mock_message = MagicMock(content=response, role="assistant")
            mock_choice = MagicMock(message=mock_message, index=0, finish_reason="stop")
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            return mock_response

        mock_completions.create = mock_create
        mock_chat.completions = mock_completions
        mock_client.chat = mock_chat

        return mock_client

    return create_client
