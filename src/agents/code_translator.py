import logging

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from src.agents.utils import get_model_from_settings

# System prompt for Python to Rust translation
RUST_TRANSLATION_SYSTEM_PROMPT = """You are an expert programmer in both Python and Rust.
Your task is to convert Python code to equivalent Rust code.
Produce clean, idiomatic Rust that captures the same functionality as the original Python.
Include appropriate error handling but DO NOT add unnecessary documentation or comments.

The Rust code should be valid, but MUST ONLY include exact translations of the Python functions that are present.

General conversion guidelines:
- Replace Python lists with Rust vectors
- Replace Python dictionaries with Rust HashMaps
- Use appropriate Rust error handling (Result/Option types)
- Add proper type annotations
- Convert Python classes to Rust structs and impl blocks
- Replace Python's dynamic typing with Rust's static typing
- Preserve any license or copyright comments from the original code
- Maintain the same functionality and behavior as the Python code
- IMPORTANT: Do not add docstring/documentation comments to functions unless they were in the original Python code
- IMPORTANT: Do not add a main function if it's not in the original Python code
- IMPORTANT: Only translate the functions that are in the original Python code - nothing more or less

Analyze the provided Python code and convert it to equivalent Rust code.
Respond ONLY with a JSON object with a single field "rust_code" which contains the complete Rust code as a string.
"""


class RustTranslation(BaseModel):
    """Rust code translation of Python code."""

    rust_code: str = Field(description="Rust code equivalent to the provided Python code")


# Create Agent for code translation
rust_translation_agent = Agent(
    output_type=RustTranslation,
    system_prompt=RUST_TRANSLATION_SYSTEM_PROMPT,
    name="rust_translation_agent",
    defer_model_check=True,
)


def _enrich_translation_prompt(python_code: str) -> str:
    """Enrich the translation prompt with Python code to translate."""
    return f"""
Convert this Python code to equivalent Rust code:

```python
{python_code}
```

Make sure to:
1. Preserve any license/copyright information as comments
2. Use idiomatic Rust patterns
3. Handle errors appropriately
4. Add type annotations
5. DO NOT add documentation comments to functions
6. DO NOT add a main function if it's not present in the original Python code
7. Translate ONLY the functions that are in the original Python code, nothing more or less
8. It also applies to main functions - if the original Python code has a main function, translate it to Rust,
   otherwise do not add one.
"""


def rewrite_to_rust(python_code: str) -> RustTranslation:
    """Convert Python code to equivalent Rust code."""
    try:
        model = get_model_from_settings()
        result = rust_translation_agent.run_sync(_enrich_translation_prompt(python_code), model=model)
        return result.output
    except Exception as e:
        # Log the error and return minimal Rust code
        logging.error("Error using rust translation agent: %s", str(e))
        return RustTranslation(rust_code="// Error translating Python to Rust")
