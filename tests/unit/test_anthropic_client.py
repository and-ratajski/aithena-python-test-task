"""Tests for the Anthropic API client implementation."""

from src.llm.anthropic_client import AnthropicClient


class TestAnthropicClient:
    """Test suite for the Anthropic client implementation."""

    def test_initialization_with_environment_mock(self, mock_anthropic_client):
        """Test initialization using the backward-compatible fixture."""
        client = AnthropicClient(client=mock_anthropic_client)

        assert client.client == mock_anthropic_client
        assert client.model  # Just check it's set, value might vary by environment
        assert client.max_tokens == 4096  # Default value
        assert client.temperature == 0.7  # Default value

    def test_initialization_with_direct_mock(self, llm_mock):
        """Test initialization using the simplified mock directly."""
        client = AnthropicClient(client=llm_mock)
        assert client.client == llm_mock

    def test_generate_response(self, llm_mock_factory):
        """Test the generate_response method with different parameters."""
        mock_response = "Mocked Anthropic response"
        mock_client = llm_mock_factory(mock_response)
        client = AnthropicClient(client=mock_client)

        prompt = "Tell me a joke"
        system_prompt = "You are a comedian"
        response = client.generate_response(prompt, system_prompt)

        assert response == mock_response
        assert mock_client.last_prompt == prompt
        assert mock_client.last_system_prompt == system_prompt

    def test_generate_response_with_custom_params(self, mock_anthropic_client_with_custom_response):
        """Test generate_response with additional keyword parameters."""
        custom_response = "Response with custom parameters"
        mock_client = mock_anthropic_client_with_custom_response(custom_response)
        client = AnthropicClient(client=mock_client)

        response = client.generate_response("Test prompt", temperature=0.2, max_tokens=500)

        assert response == custom_response

    def test_rewrite_to_rust(self, mock_anthropic_client_with_custom_response):
        """Test the rewrite_to_rust method."""
        expected_rust_code = 'fn main() {\n    println!("Hello, Rust!");\n}'
        mock_client = mock_anthropic_client_with_custom_response(expected_rust_code)
        client = AnthropicClient(client=mock_client)

        python_code = "def hello():\n    print('Hello, Python!')"
        result = client.rewrite_to_rust(python_code)

        assert result == expected_rust_code
