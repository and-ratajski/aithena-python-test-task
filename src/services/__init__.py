"""Services package for the AITHENA test task.

This package contains services for processing files, detecting licenses,
counting functions, analyzing code, and other operations needed for the test task.
"""

from src.services.code_analyzer import (
    CodeAnalyzerError, CopyrightExtractor, FunctionExtractor
)
from src.services.function_counter import FunctionCounter, FunctionCounterError
from src.services.license_detector import LicenseDetector
from src.services.result_handler import ResultHandlerError, ResultSaver

__all__ = [
    # License detection
    'LicenseDetector', 
    
    # Function counting
    'FunctionCounter',
    'FunctionCounterError',
    
    # Code analysis
    'CodeAnalyzerError',
    'CopyrightExtractor',
    'FunctionExtractor',
    
    # Result handling
    'ResultHandlerError',
    'ResultSaver'
]