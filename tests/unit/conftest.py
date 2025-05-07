from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from anthropic import Anthropic
from openai import OpenAI


class SimplifiedMockResponse:
    """Generic mock response that can be used for both clients."""
    
    def __init__(self, text_content: str):
        # For Anthropic
        self.content = [Mock(text=text_content)]
        
        # For OpenAI
        mock_message = Mock(content=text_content, role="assistant")
        mock_choice = Mock(message=mock_message, index=0, finish_reason="stop")
        self.choices = [mock_choice]

        self.id = "mock-id"
        self.created = 1234567890
        self.model = "mock-model"
        self.usage = {"total_tokens": 30}


@pytest.fixture
def mock_anthropic_client() -> Anthropic:
    """Fixture for a mock Anthropic client with configurable responses.
    
    Returns:
        A mocked Anthropic client for testing
    """
    # Create base mock client
    mock_client = MagicMock(spec=Anthropic)
    
    # Mock the messages namespace
    mock_messages = MagicMock()
    
    # Configure the create method
    def mock_create(**kwargs: Any) -> SimplifiedMockResponse:
        # Store parameters for inspection in tests
        mock_messages.last_model = kwargs.get("model", "")
        mock_messages.last_messages = kwargs.get("messages", [])
        mock_messages.last_system = kwargs.get("system", "")
        
        # Special case for Rust code conversion
        if kwargs.get("system") and "rust" in kwargs.get("system", "").lower():
            return SimplifiedMockResponse("fn main() {\n    println!(\"Hello, world!\");\n}")
        
        return SimplifiedMockResponse("Mocked Anthropic response")
    
    # Assign the create method to the messages namespace
    mock_messages.create = mock_create
    mock_client.messages = mock_messages
    
    return mock_client


@pytest.fixture
def mock_openai_client() -> OpenAI:
    """Fixture for a mock OpenAI client with configurable responses.
    
    Returns:
        A mocked OpenAI client for testing
    """
    # Create base mock client
    mock_client = MagicMock(spec=OpenAI)
    
    # Set up nested structure: client.chat.completions
    mock_chat = MagicMock()
    mock_completions = MagicMock()
    
    # Configure the create method
    def mock_create(**kwargs: Any) -> SimplifiedMockResponse:
        # Store parameters for inspection in tests
        mock_completions.last_model = kwargs.get("model", "")
        mock_completions.last_messages = kwargs.get("messages", [])
        
        # Special case for Rust code conversion
        for message in kwargs.get("messages", []):
            if message.get("role") == "system" and "rust" in message.get("content", "").lower():
                return SimplifiedMockResponse("fn main() {\n    println!(\"Hello, Rust!\");\n}")
        
        return SimplifiedMockResponse("Mocked OpenAI response")
    
    # Assign the create method and build the object structure
    mock_completions.create = mock_create
    mock_chat.completions = mock_completions
    mock_client.chat = mock_chat
    
    return mock_client


@pytest.fixture
def mock_anthropic_client_with_custom_response() -> callable:
    """Factory fixture for creating Anthropic clients with custom responses.
    
    Returns:
        A function that produces configured mock clients
    """
    def create_client(response_text: str) -> Anthropic:
        mock_client = MagicMock(spec=Anthropic)
        mock_messages = MagicMock()
        
        def custom_create(**kwargs: Any) -> SimplifiedMockResponse:
            mock_messages.last_messages = kwargs.get("messages", [])
            mock_messages.last_system = kwargs.get("system", "")
            return SimplifiedMockResponse(response_text)
        
        mock_messages.create = custom_create
        mock_client.messages = mock_messages
        return mock_client
    
    return create_client


@pytest.fixture
def mock_openai_client_with_custom_response() -> callable:
    """Factory fixture for creating OpenAI clients with custom responses.
    
    Returns:
        A function that produces configured mock clients
    """
    def create_client(response_text: str) -> OpenAI:
        mock_client = MagicMock(spec=OpenAI)
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        
        def custom_create(**kwargs: Any) -> SimplifiedMockResponse:
            mock_completions.last_messages = kwargs.get("messages", [])
            return SimplifiedMockResponse(response_text)
        
        mock_completions.create = custom_create
        mock_chat.completions = mock_completions
        mock_client.chat = mock_chat
        return mock_client
    
    return create_client