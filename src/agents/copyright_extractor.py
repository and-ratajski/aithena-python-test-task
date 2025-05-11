import logging

from pydantic_ai import Agent

from src.agents.utils import get_model_from_settings
from src.data_models.response_models import CopyrightInfo

SYSTEM_PROMPT = """
You are an expert in software licensing and copyright law.
Your task is to extract the copyright holder name from code file headers.
Focus only on the copyright information. Be precise and return only the name of the copyright holder.

Analyze the following code file header and extract the copyright holder name.
Respond ONLY with a JSON object with a single field "copyright_holder" which contains the name of the copyright holder.
If no copyright holder is specified, use "Unknown".

Examples:
---
Header: 
```
// MIT License
// 
// Copyright (c) 2020 John Doe
// 
// Permission is hereby granted...
```
Response: {"copyright_holder": "John Doe"}

---
Header:
```
# Copyright 2023 Google LLC
#
# Licensed under the Apache License...

def some_function():
    print('do not look at it')
```
Response: {"copyright_holder": "Google LLC"}

"""


copyright_agent = Agent(
    output_type=CopyrightInfo, system_prompt=SYSTEM_PROMPT, name="copyright_agent", defer_model_check=True
)


def _enrich_copyright_prompt(file_content: str, content_limit: int = 1000) -> str:
    """Enrich the copyright extraction prompt with file content."""
    return f"""
---
Now extract the copyright holder from this file:
```
{file_content[:content_limit]}
```
"""


def extract_copyright_holder(file_content: str) -> CopyrightInfo:
    """Extract the copyright holder information from file content."""
    try:
        # Get model from settings and run the agent
        model = get_model_from_settings()
        result = copyright_agent.run_sync(_enrich_copyright_prompt(file_content), model=model)
        return result.output
    except Exception as e:
        # Log the error and return unknown copyright holder
        logging.error("Error using copyright extractor agent: %s", str(e))
        return CopyrightInfo(copyright_holder="Unknown")
