"""OpenAI LLM client implementation."""

import os
from typing import Dict, Any, Optional, List, cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from src.llm.protocols import LlmClient, LLMClientError

load_dotenv()


class OpenAIClient(LlmClient):
    """Client for interacting with OpenAI's models.
    
    This class provides an implementation of the LlmClient protocol
    for OpenAI's models (GPT-4, etc.).
    
    Note: This class implements the LlmClient Protocol implicitly by
    providing compatible method signatures.
    """
    
    def __init__(self, client: Optional[OpenAI] = None) -> None:
        """Initialize the OpenAI client using environment variables.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not set in environment variables
        """
        if client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required in environment variables.")
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = client
        
        self.model = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2048"))  # Different from Anthropic
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate a response from OpenAI models.
        
        Args:
            prompt: The user message to send to the model
            system_prompt: Optional system prompt to set context
            **kwargs: Additional parameters to pass to the OpenAI API
            
        Returns:
            The generated text response
            
        Raises:
            LLMClientError: If the API request fails
        """
        try:
            messages: List[Dict[str, str]] = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare parameters with defaults that can be overridden
            params: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
            
            # Override defaults with any provided kwargs
            for key, value in kwargs.items():
                if key != "messages":  # Don't override messages
                    params[key] = value
            
            response: ChatCompletion = self.client.chat.completions.create(**params)
            
            # Extract the response text from the first choice
            if response.choices and response.choices[0].message.content:
                return cast(str, response.choices[0].message.content)
            return ""
            
        except Exception as e:
            raise LLMClientError(f"Error generating response from OpenAI: {str(e)}")
    
    def rewrite_to_rust(self, python_code: str) -> str:
        """Rewrite Python code to equivalent Rust code.
        
        Args:
            python_code: The Python code to convert to Rust
            
        Returns:
            Equivalent Rust code
            
        Raises:
            LLMClientError: If the API request fails
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