from anthropic import Anthropic

from src.llm.anthropic_client import AnthropicClient


class TestAnthropicClient:
    """Test suite for AnthropicClient."""

    def test_initialization_with_mock(self, mock_anthropic_client: Anthropic):
        """Test client initialization with a mocked Anthropic client."""
        client = AnthropicClient(client=mock_anthropic_client)

        assert client.client == mock_anthropic_client
        assert client.max_tokens == 4096  # Default value
        assert client.temperature == 0.7  # Default value

    def test_generate_response(self, mock_anthropic_client: Anthropic):
        """Test the generate_response method."""
        client = AnthropicClient(client=mock_anthropic_client)
        prompt = "Tell me a joke"
        system_prompt = "You are a comedian"

        response = client.generate_response(prompt, system_prompt)

        assert response == "Mocked Anthropic response"
        assert mock_anthropic_client.messages.last_messages == [{"role": "user", "content": prompt}]
        assert mock_anthropic_client.messages.last_system == system_prompt

    def test_generate_response_with_custom_response(self, mock_anthropic_client_with_custom_response):
        """Test generate_response with a custom mocked response."""
        custom_response = "This is a custom response from the mocked Anthropic API"
        mock_client = mock_anthropic_client_with_custom_response(custom_response)
        client = AnthropicClient(client=mock_client)

        response = client.generate_response("Any prompt")

        assert response == custom_response

    def test_rewrite_to_rust(self, mock_anthropic_client: Anthropic):
        """Test the rewrite_to_rust method."""
        client = AnthropicClient(client=mock_anthropic_client)
        python_code = "def hello():\n    print('Hello, world!')"

        response = client.rewrite_to_rust(python_code)

        assert "fn main() {" in response
        assert "println!(\"Hello, world!\");" in response
        
        # Verify the system prompt was correctly formed with Rust instructions
        assert "rust" in mock_anthropic_client.messages.last_system.lower()
        
        # Verify the prompt contains the Python code
        assert python_code in mock_anthropic_client.messages.last_messages[0]["content"]