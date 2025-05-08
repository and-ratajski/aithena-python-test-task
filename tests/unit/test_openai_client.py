"""Tests for the OpenAI API client implementation."""

from src.llm.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test suite for the OpenAI client implementation."""

    def test_initialization_with_environment_mock(self, mock_openai_client):
        """Test initialization using the backward-compatible fixture."""
        client = OpenAIClient(client=mock_openai_client)

        assert client.client == mock_openai_client
        assert client.model  # Any value is acceptable, just check it's set
        assert client.max_tokens == 2048  # Default value
        assert client.temperature == 0.7  # Default value

    def test_initialization_with_direct_mock(self, llm_mock):
        """Test initialization using the simplified mock directly."""
        client = OpenAIClient(client=llm_mock)
        assert client.client == llm_mock

    def test_generate_response(self, mock_openai_client_with_custom_response):
        """Test the generate_response method with different parameters."""
        mock_response = "Mocked OpenAI response"
        mock_client = mock_openai_client_with_custom_response(mock_response)
        client = OpenAIClient(client=mock_client)

        prompt = "Tell me a joke"
        system_prompt = "You are a comedian"
        response = client.generate_response(prompt, system_prompt)

        assert response == mock_response

    def test_generate_response_with_custom_params(self, mock_openai_client_with_custom_response):
        """Test generate_response with additional keyword parameters."""
        expected_response = "Response with custom parameters"
        mock_client = mock_openai_client_with_custom_response(expected_response)
        client = OpenAIClient(client=mock_client)

        response = client.generate_response("Test prompt", temperature=0.2, top_p=0.95)

        assert response == expected_response

    def test_rewrite_to_rust(self, mock_openai_client_with_custom_response):
        """Test the rewrite_to_rust method."""
        expected_rust_code = 'fn main() {\n    println!("Hello, Rust!");\n}'
        mock_client = mock_openai_client_with_custom_response(expected_rust_code)
        client = OpenAIClient(client=mock_client)

        python_code = "def hello():\n    print('Hello, Python!')"
        result = client.rewrite_to_rust(python_code)

        assert result == expected_rust_code

    def test_response_extraction(self, mock_openai_client_with_custom_response):
        """Test proper extraction of message content from OpenAI response structure."""
        custom_response = "Content from message.content"
        mock_client = mock_openai_client_with_custom_response(custom_response)
        client = OpenAIClient(client=mock_client)

        response = client.generate_response("Any prompt")

        assert response == custom_response
