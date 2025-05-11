import logging

from pydantic_ai import Agent

from src.agents.safety_checker import get_safety_tool
from src.agents.utils import get_model_from_settings
from src.data_models.response_models import RustTranslation

RUST_TRANSLATION_SYSTEM_PROMPT = """You are an expert programmer in both Python and Rust.
Your task is to convert Python code to equivalent Rust code.
Produce clean, idiomatic Rust that captures the same functionality as the original Python.
Include appropriate error handling but DO NOT add unnecessary documentation or comments.

IMPORTANT: Always use the check_safety tool first to verify that the content is safe to analyze.
If the content is not safe, do not proceed with the translation and return empty code.

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


rust_translation_agent = Agent(
    output_type=RustTranslation,
    system_prompt=RUST_TRANSLATION_SYSTEM_PROMPT,
    name="rust_translation_agent",
    defer_model_check=True,
)

# Create and add the safety checker as a tool to the translation agent
rust_translation_agent.tool(get_safety_tool("rust_translation_agent"))


def _enrich_translation_prompt(python_code: str) -> str:
    """Enrich the translation prompt with Python code to translate and safety instructions."""
    return f"""
Convert this Python code to equivalent Rust code:

```python
{python_code}
```

IMPORTANT: First use the check_safety tool to ensure the content is safe to process.
If the content is not safe, do not translate the code and return an empty string.

If the content is safe, make sure to:
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
    """Convert Python code to equivalent Rust code.

    This function will first check that the content is safe to process,
    and then translate the Python code to Rust.
    """
    try:
        model = get_model_from_settings()
        result = rust_translation_agent.run_sync(_enrich_translation_prompt(python_code), model=model)
        return result.output
    except Exception as e:
        logging.error("Error using rust translation agent: %s", str(e))
        return RustTranslation(rust_code="// Error translating Python to Rust")
