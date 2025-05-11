"""Agents module for the AITHENA task solver.

This module provides AI-powered agents using Pydantic AI for various tasks:
- License detection
- Copyright extraction
- Programming language detection
- Function analysis
- Code translation
"""

from src.agents.code_translator import rewrite_to_rust
from src.agents.copyright_extractor import extract_copyright_holder
from src.agents.function_analyzer import count_functions, extract_functions_with_args
from src.agents.language_detector import detect_programming_language
from src.agents.license_detector import detect_license
from src.agents.utils import ANTHROPIC, OPENAI, configure_pydantic_ai

__all__ = [
    # Configuration
    "configure_pydantic_ai",
    "ANTHROPIC",
    "OPENAI",
    # Agent functions
    "detect_license",
    "extract_copyright_holder",
    "detect_programming_language",
    "count_functions",
    "extract_functions_with_args",
    "rewrite_to_rust",
]
