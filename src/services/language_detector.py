"""Language detection service.

This module contains functionality for detecting programming languages in code files.
"""

import json
from enum import Enum, auto

from src.llm.protocols import LlmClient, LLMClientError


class ProgrammingLanguage(Enum):
    """Enum representing programming languages that can be detected."""

    PYTHON = auto()
    JAVASCRIPT = auto()
    JAVA = auto()
    RUST = auto()
    UNKNOWN = auto()


class LanguageDetectionError(Exception):
    """Exception raised for errors in language detection."""

    pass


class LanguageDetector:
    """Detects programming languages in code files using LLM."""

    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the language detector with an LLM client.

        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client

        # Map of language names to enum values
        self._language_map: dict[str, ProgrammingLanguage] = {
            "python": ProgrammingLanguage.PYTHON,
            "javascript": ProgrammingLanguage.JAVASCRIPT,
            "java": ProgrammingLanguage.JAVA,
            "rust": ProgrammingLanguage.RUST,
            "unknown": ProgrammingLanguage.UNKNOWN,
        }

    def detect_language(self, code: str) -> ProgrammingLanguage:
        """Detect the programming language of the provided code using LLM.

        Args:
            code: The code content to analyze

        Returns:
            The detected programming language

        Raises:
            LanguageDetectionError: If language detection fails
        """
        try:
            sample_size = min(2000, len(code))
            code_sample = code[:sample_size]

            system_prompt = """You are an expert programmer specializing in language detection.
Your task is to analyze code snippets and determine the programming language being used.
Be precise and focused only on identifying the language from the supported list.
"""

            prompt = f"""Analyze the following code snippet and determine which programming language it is written in.
Only consider these options: Python, JavaScript, Java, Rust, or Unknown if you can't determine.

Respond ONLY with a JSON object with a single field "language" which contains the detected language as a string.
For example: {{"language": "python"}}

Consider these key characteristics of each language:

Python:
- Uses 'def' for function definitions
- Uses '#' for comments
- Uses indentation for code blocks
- Uses 'import' and 'from...import' for imports

JavaScript:
- Uses 'function', arrow functions (=>), or method syntax for functions
- Uses '//' or '/* */' for comments
- Uses braces {{}} for code blocks
- Uses 'const', 'let', 'var' for variable declarations

Java:
- Uses public/private/protected modifiers
- Class-based with 'class' keyword
- Method definitions inside classes
- Uses 'import' statements and package declarations
- Strongly typed with type declarations

Rust:
- Uses 'fn' for function definitions
- Uses 'struct', 'enum', 'impl' keywords
- Uses 'let' for variable declarations
- Uses '//'' or '/* */' for comments
- Often has types with ': Type' syntax

Code to analyze:
```
{code_sample}
```
"""

            response = self.llm_client.generate_response(prompt, system_prompt)

            # Parse the response - we expect a JSON object
            try:
                result = json.loads(response)
                language_name = result.get("language", "unknown").lower()

                # Map the language name to ProgrammingLanguage enum
                return self._language_map.get(language_name, ProgrammingLanguage.UNKNOWN)

            except json.JSONDecodeError as e:
                # If the response isn't valid JSON, try to extract the language name
                try:
                    # Try to handle cases where LLM outputs something like "Python"
                    language_name = response.strip().lower()
                    if language_name in self._language_map:
                        return self._language_map[language_name]
                    else:
                        # If we couldn't extract a valid language, return UNKNOWN
                        return ProgrammingLanguage.UNKNOWN
                except Exception:
                    # If all else fails, return UNKNOWN
                    return ProgrammingLanguage.UNKNOWN

        except LLMClientError as e:
            raise LanguageDetectionError(f"LLM request failed: {str(e)}")
        except Exception as e:
            raise LanguageDetectionError(f"Error detecting language: {str(e)}")
