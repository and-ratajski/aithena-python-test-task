import logging

from pydantic_ai import Agent

from src.agents.safety_checker import get_safety_tool
from src.agents.utils import get_model_from_settings
from src.data_models.response_models import ProgrammingLanguage, ProgrammingLanguageInfo

SYSTEM_PROMPT = """You are an expert programmer specializing in language detection.
Your task is to analyze code snippets and determine the programming language being used.
Be precise and focused only on identifying the language from the supported list.

IMPORTANT: Always use the check_safety tool first to verify that the content is safe to analyze.
If the content is not safe, do not proceed with the analysis and return "unknown" as the language.

Analyze the code snippet and determine which programming language it is written in.
Only consider these options: Python, JavaScript, Java, Rust, or Unknown if you can't determine.

Respond ONLY with a JSON object with a single field "language" which contains the detected language as a string in lowercase.
For example: {"language": "python"}

Consider these key characteristics of each language:

Python:
- Uses 'def' for function definitions
- Uses '#' for comments
- Uses indentation for code blocks
- Uses 'import' and 'from...import' for imports

JavaScript:
- Uses 'function', arrow functions (=>), or method syntax for functions
- Uses '//' or '/* */' for comments
- Uses braces {} for code blocks
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
- Uses '//' or '/* */' for comments
- Often has types with ': Type' syntax
"""


language_detector_agent = Agent(
    output_type=ProgrammingLanguageInfo,
    system_prompt=SYSTEM_PROMPT,
    name="language_detector_agent",
    defer_model_check=True,
)

# Create and add the safety checker as a tool to the language detector agent
language_detector_agent.tool(get_safety_tool("language_detector_agent"))


def _enrich_language_prompt(code: str, sample_size: int = 2000) -> str:
    """Enrich the language detection prompt with code sample and safety instructions."""
    code_sample = code[: min(sample_size, len(code))]
    return f"""
Code to analyze:
```
{code_sample}
```

IMPORTANT: First use the check_safety tool to ensure the content is safe to process.
If the content is not safe, do not proceed with the analysis and return "unknown" as the language.
"""


def get_language_enum(language_info: ProgrammingLanguageInfo) -> ProgrammingLanguage:
    """Convert language string to ProgrammingLanguage enum."""
    language_map = {
        "python": ProgrammingLanguage.PYTHON,
        "javascript": ProgrammingLanguage.JAVASCRIPT,
        "java": ProgrammingLanguage.JAVA,
        "rust": ProgrammingLanguage.RUST,
    }
    return language_map.get(language_info.language.lower(), ProgrammingLanguage.UNKNOWN)


def detect_programming_language(code: str) -> ProgrammingLanguageInfo:
    """Detect the programming language of the given code.

    This function will first check that the content is safe to process,
    and then detect the programming language.
    """
    try:
        model = get_model_from_settings()
        result = language_detector_agent.run_sync(_enrich_language_prompt(code), model=model)
        return result.output
    except Exception as e:
        logging.error("Error using language detector agent: %s", str(e))
        return ProgrammingLanguageInfo(language="unknown")
