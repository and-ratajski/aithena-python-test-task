"""License types definitions.

This module contains the enum definitions for license types.
"""

from enum import Enum, auto


class LicenseType(Enum):
    """Enum representing types of software licenses."""

    PERMISSIVE = auto()  # Open source permissive (MIT, Apache, BSD, etc.)
    COPYLEFT = auto()  # Open source copyleft (GPL, LGPL, AGPL, etc.)
    PROPRIETARY = auto()  # Closed source or custom license
    UNKNOWN = auto()  # License couldn't be determined
