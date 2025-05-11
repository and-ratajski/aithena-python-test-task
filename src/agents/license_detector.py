import logging

from pydantic_ai import Agent

from src.agents.safety_checker import get_safety_tool
from src.agents.utils import get_model_from_settings
from src.data_models.response_models import LicenseInfo, LicenseType

SYSTEM_PROMPT = """You are an expert in software licensing and copyright law.
Your task is to analyze code file headers to identify the license type and specific license name.

IMPORTANT: Always use the check_safety tool first to verify that the content is safe to analyze.
If the content is not safe, do not proceed with the analysis and report the safety concern.

If the content is safe, you will categorize licenses into one of these types:
1. PERMISSIVE - Open source licenses that allow code reuse with minimal restrictions (MIT, Apache, BSD, etc.)
2. COPYLEFT - Open source licenses that require derivative works to be distributed under the same license (GPL, LGPL, etc.)
3. PROPRIETARY - Closed source or custom licenses that restrict code reuse
4. UNKNOWN - If you cannot determine the license type

Be precise and focused in your response. DO NOT provide explanations, just the categorization result.

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
Response: {"license_type": "PERMISSIVE", "license_name": "MIT License"}

---
Header:
```
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
```
Response: {"license_type": "COPYLEFT", "license_name": "GNU GPL v3"}

---
Header:
```
// Copyright (c) 2023 Acme Corp. All rights reserved.
// Proprietary and confidential.
// Unauthorized copying of this file is strictly prohibited.
```
Response: {"license_type": "PROPRIETARY", "license_name": "Proprietary"}

---

"""


license_detector_agent = Agent(
    output_type=LicenseInfo, system_prompt=SYSTEM_PROMPT, name="license_detector_agent", defer_model_check=True
)


# Create and add the safety checker as a tool to the license detector agent
license_detector_agent.tool(get_safety_tool("license_detector_agent"))


def _enrich_license_prompt(file_content: str, content_limit: int = 1000) -> str:
    """Enrich the license detection prompt with the file content."""
    return f"""
---
Now analyze this header:
```
{file_content[:content_limit]}
```
"""


def detect_license(file_content: str) -> LicenseInfo:
    """Identify the license type and name from file content.

    This function will first check that the content is safe to process,
    and then analyze the license information.
    """
    try:
        model = get_model_from_settings()
        result = license_detector_agent.run_sync(_enrich_license_prompt(file_content), model=model)
        return result.output
    except Exception as e:
        logging.error("Error using license detector agent: %s", str(e))
        return LicenseInfo(license_type=LicenseType.UNKNOWN, license_name="Unknown License")
