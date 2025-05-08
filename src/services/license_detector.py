"""License detector implementation.

This module contains functionality for detecting license types using LLM to analyze license texts.
"""

import json
import logging

from src.data_models.license_types import LicenseType
from src.llm.protocols import LlmClient


class LicenseDetector:
    """Detects license types from file content using LLM."""

    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the license detector with an LLM client.

        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client

    def get_license_type(self, file_content: str) -> tuple[LicenseType, str]:
        """Determine the license type of a file using LLM.

        Args:
            file_content: The content of the file to analyze

        Returns:
            A tuple of (LicenseType, license_name)
        """
        system_prompt = """You are an expert in software licensing and copyright law.
Your task is to analyze code file headers to identify the license type and specific license name.
You will categorize licenses into one of these types:
1. PERMISSIVE - Open source licenses that allow code reuse with minimal restrictions (MIT, Apache, BSD, etc.)
2. COPYLEFT - Open source licenses that require derivative works to be distributed under the same license (GPL, LGPL, etc.)
3. PROPRIETARY - Closed source or custom licenses that restrict code reuse
4. UNKNOWN - If you cannot determine the license type

Be precise and focused in your response. DO NOT provide explanations, just the categorization result.
"""

        prompt = f"""Analyze the following code file header and determine its license type. Focus only on the license
text and copyright information.
Respond ONLY with a JSON object that has two fields:
1. "license_type": Must be one of "PERMISSIVE", "COPYLEFT", "PROPRIETARY", or "UNKNOWN"
2. "license_name": The specific license name (e.g., "MIT License", "GNU GPL v3", "Proprietary", "Unknown License")

Examples:
---
Header: 
```
// MIT License
// 
// Copyright (c) 2020 John Doe
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files...
```
Response: {{"license_type": "PERMISSIVE", "license_name": "MIT License"}}

---
Header:
```
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
```
Response: {{"license_type": "COPYLEFT", "license_name": "GNU GPL v3"}}

---
Header:
```
// Copyright (c) 2023 Acme Corp. All rights reserved.
// Proprietary and confidential.
// Unauthorized copying of this file is strictly prohibited.
```
Response: {{"license_type": "PROPRIETARY", "license_name": "Proprietary"}}

---
Now analyze this header:
```
{file_content[:1000]}  # Only send the first 1000 chars, which should contain the license
```
"""

        try:
            response = self.llm_client.generate_response(prompt, system_prompt)

            # Parse the response - we expect a JSON object
            try:
                result = json.loads(response)
                license_type_str = result.get("license_type", "UNKNOWN")
                license_name = result.get("license_name", "Unknown License")

                # Convert string to LicenseType enum
                license_type = LicenseType.UNKNOWN
                if license_type_str == "PERMISSIVE":
                    license_type = LicenseType.PERMISSIVE
                elif license_type_str == "COPYLEFT":
                    license_type = LicenseType.COPYLEFT
                elif license_type_str == "PROPRIETARY":
                    license_type = LicenseType.PROPRIETARY

                return license_type, license_name

            except json.JSONDecodeError:
                # If the response isn't valid JSON, fallback to UNKNOWN
                return LicenseType.UNKNOWN, "Unknown License"

        except Exception as e:
            # If LLM request fails, fallback to UNKNOWN
            logging.error("Error determining license with LLM: %s", str(e))
            return LicenseType.UNKNOWN, "Unknown License"
