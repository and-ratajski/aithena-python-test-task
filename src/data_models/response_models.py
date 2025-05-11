"""License types definitions.

This module contains the enum definitions for license types.
"""

from enum import Enum, auto

from pydantic import BaseModel, Field


class LicenseType(Enum):
    """Enum representing types of software licenses."""

    PERMISSIVE = auto()  # Open source permissive (MIT, Apache, BSD, etc.)
    COPYLEFT = auto()  # Open source copyleft (GPL, LGPL, AGPL, etc.)
    PROPRIETARY = auto()  # Closed source or custom license
    UNKNOWN = auto()  # License couldn't be determined


class ProgrammingLanguage(Enum):
    """Enum representing programming languages that can be detected."""

    PYTHON = auto()
    JAVASCRIPT = auto()
    JAVA = auto()
    RUST = auto()
    UNKNOWN = auto()


class CopyrightInfo(BaseModel):
    """Information about copyright extracted from code."""

    copyright_holder: str = Field(
        description="The name of the copyright holder",
        examples=["OpenAI", "Anthropic", "John Doe", "Example Corporation"],
    )


class FunctionCountInfo(BaseModel):
    """Information about the number of functions in code."""

    function_count: int = Field(
        description="The total number of unique function definitions", ge=0, examples=[0, 2, 5, 10]
    )


class ProgrammingLanguageInfo(BaseModel):
    """Information about the programming language of code."""

    language: str = Field(
        description="The detected programming language", examples=["python", "javascript", "java", "rust", "unknown"]
    )


class LicenseInfo(BaseModel):
    """Information about a license extracted from code."""

    license_type: LicenseType = Field(
        description="Type of license (PERMISSIVE, COPYLEFT, PROPRIETARY, UNKNOWN)",
        examples=["PERMISSIVE", "COPYLEFT", "PROPRIETARY", "UNKNOWN"],
    )
    license_name: str = Field(
        description="Name of the license",
        examples=["MIT License", "GNU GPL v3", "Apache License 2.0", "Proprietary", "Unknown License"],
    )


class RustTranslation(BaseModel):
    """Rust code translation of Python code."""

    rust_code: str = Field(description="Rust code equivalent to the provided Python code")


class ContentSafetyInfo(BaseModel):
    """Information about the safety of the content."""

    is_safe: bool = Field(description="Whether the content is safe to process", examples=[True, False])
    reason: str = Field(
        description="Reason why the content is considered unsafe, if applicable",
        default="",
        examples=["Contains jailbreak attempt", "Contains prompt injection", "No safety issues detected"],
    )
    severity: str = Field(
        description="Severity of the safety issue, if applicable",
        default="none",
        examples=["none", "low", "medium", "high", "critical"],
    )
