"""Anthropic Claude LLM client implementation."""

import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from anthropic import Anthropic, AnthropicError

from src.llm.protocols import LlmClient, LLMClientError

load_dotenv()


class AnthropicClient(LlmClient):
    """Client for interacting with Anthropic's Claude models.
    
    This class provides an implementation of the LlmClient protocol
    for Anthropic's Claude models.
    
    Note: This class implements the LlmClient Protocol implicitly by
    providing compatible method signatures.
    """
    
    def __init__(self, client: Optional[Anthropic] = None) -> None:
        """Initialize the Anthropic client using environment variables.
        
        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set in environment variables
        """
        if client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY is required in environment variables.")
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = client
        
        self.model = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-sonnet-20240229")
        self.max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))  # Different from OpenAI
        self.temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
        

    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate a response from Claude.
        
        Args:
            prompt: The user message to send to Claude
            system_prompt: Optional system prompt to set context
            **kwargs: Additional parameters to pass to the Claude API
            
        Returns:
            The generated text response
            
        Raises:
            AnthropicError: If the API request fails
        """
        try:
            message_params: Dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            }
            
            if system_prompt:
                message_params["system"] = system_prompt
                
            response = self.client.messages.create(**message_params)
            return response.content[0].text
            
        except AnthropicError as e:
            raise LLMClientError(f"Error generating response from Claude: {str(e)}")
    
    def rewrite_to_rust(self, python_code: str) -> str:
        """Rewrite Python code to equivalent Rust code.
        
        Args:
            python_code: The Python code to convert to Rust
            
        Returns:
            Equivalent Rust code
            
        Raises:
            AnthropicError: If the API request fails
        """
        system_prompt = """You are an expert programmer in both Python and Rust. 
        Your task is to convert Python code to equivalent Rust code.
        Produce clean, idiomatic Rust that captures the same functionality as the original Python.
        Include appropriate error handling and comments in the Rust code.
        The Rust code should be complete, valid, and ready to compile."""
        
        prompt = f"""Please convert the following Python code to equivalent Rust code:

```python
{python_code}
```

Provide only the Rust code, without any explanations."""
        
        return self.generate_response(prompt, system_prompt)