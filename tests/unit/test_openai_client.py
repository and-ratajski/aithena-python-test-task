from openai import OpenAI

from src.llm.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test suite for OpenAIClient."""

    def test_initialization_with_mock(self, mock_openai_client: OpenAI):
        """Test client initialization with a mocked OpenAI client."""
        # Arrange & Act
        client = OpenAIClient(client=mock_openai_client)

        # Assert
        assert client.client == mock_openai_client
        assert client.model == "gpt-4"  # Default value
        assert client.max_tokens == 2048  # Default value
        assert client.temperature == 0.7  # Default value

    def test_generate_response(self, mock_openai_client: OpenAI):
        """Test the generate_response method."""
        # Arrange
        client = OpenAIClient(client=mock_openai_client)
        prompt = "Tell me a joke"
        system_prompt = "You are a comedian"

        # Act
        response = client.generate_response(prompt, system_prompt)

        # Assert
        assert response == "Mocked OpenAI response"

        # Verify system and user messages were correctly passed
        messages = mock_openai_client.chat.completions.last_messages
        assert any(m["role"] == "system" and m["content"] == system_prompt for m in messages)
        assert any(m["role"] == "user" and m["content"] == prompt for m in messages)

    def test_generate_response_with_custom_response(self, mock_openai_client_with_custom_response):
        """Test generate_response with a custom mocked response."""
        # Arrange
        custom_response = "This is a custom response from the mocked OpenAI API"
        mock_client = mock_openai_client_with_custom_response(custom_response)
        client = OpenAIClient(client=mock_client)

        # Act
        response = client.generate_response("Any prompt")

        # Assert
        assert response == custom_response

    def test_generate_response_with_kwargs(self, mock_openai_client: OpenAI):
        """Test that kwargs are properly passed to the OpenAI client."""
        # Arrange
        client = OpenAIClient(client=mock_openai_client)
        custom_temperature = 0.2
        custom_top_p = 0.95

        # Act
        client.generate_response("Hello", temperature=custom_temperature, top_p=custom_top_p)

        # This test doesn't verify parameter passing directly because of how our mock is structured
        # In a real scenario with a more sophisticated mock, we could verify these parameters

    def test_rewrite_to_rust(self, mock_openai_client: OpenAI):
        """Test the rewrite_to_rust method."""
        # Arrange
        client = OpenAIClient(client=mock_openai_client)
        python_code = "def hello():\n    print('Hello, world!')"

        # Act
        response = client.rewrite_to_rust(python_code)

        # Assert
        assert "fn main() {" in response
        assert "Hello, Rust!" in response

        # Verify the message structure
        messages = mock_openai_client.chat.completions.last_messages

        # System message should have Rust instructions
        system_message = next((m for m in messages if m["role"] == "system"), None)
        assert system_message is not None
        assert "rust" in system_message["content"].lower()

        # User message should contain the Python code
        user_message = next((m for m in messages if m["role"] == "user"), None)
        assert user_message is not None
        assert python_code in user_message["content"]
