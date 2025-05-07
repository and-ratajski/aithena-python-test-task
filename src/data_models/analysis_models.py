"""Analysis result data models.

This module contains data models for representing analysis results.
"""
from dataclasses import dataclass
from typing import List, Optional

from src.data_models.license_types import LicenseType


@dataclass
class FunctionInfo:
    """Information about a function extracted from code."""
    name: str
    arg_count: int


@dataclass
class FileAnalysisResult:
    """Result of file analysis, containing all extracted information."""
    file_name: str
    copyright_holder: str
    license_name: str
    license_type: LicenseType
    function_count: Optional[int] = None
    functions: Optional[List[FunctionInfo]] = None
    rust_code: Optional[str] = None