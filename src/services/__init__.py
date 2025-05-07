"""Services package for the AITHENA test task.

This package contains services for processing files, detecting licenses,
counting functions, and other operations needed for the test task.
"""

from src.services.license_detector import LicenseDetector, LicenseType
from src.services.function_counter import FunctionCounter, FunctionCounterError

__all__ = [
    'LicenseDetector', 
    'LicenseType',
    'FunctionCounter',
    'FunctionCounterError'
]