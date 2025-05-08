"""Code analyzer implementation.

This module contains functionality for analyzing code files and extracting metadata.
"""

import json
import logging

from src.llm.protocols import LlmClient


class CodeAnalyzerError(Exception):
    """Exception raised for errors in code analysis."""

    pass


class CopyrightExtractor:
    """Extracts copyright information from code files using LLM."""

    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the copyright extractor with an LLM client.

        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client

    def extract_copyright_holder(self, file_content: str) -> str:
        """Extract copyright holder from code file using LLM.

        Args:
            file_content: The content of the file to analyze

        Returns:
            The name of the copyright holder

        Raises:
            CodeAnalyzerError: If extracting copyright information fails
        """
        system_prompt = """You are an expert in software licensing and copyright law.
Your task is to extract the copyright holder name from code file headers.
Focus only on the copyright information. Be precise and return only the name of the copyright holder.
"""

        prompt = f"""Analyze the following code file header and extract the copyright holder name.
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
Response: {{"copyright_holder": "John Doe"}}

---
Header:
```
# Copyright 2023 Google LLC
#
# Licensed under the Apache License...

def some_function():
    print('do not look at it')
```
Response: {{"copyright_holder": "Google LLC"}}

---
Now extract the copyright holder from this file:
```
{file_content[:1500]}  # Only send the first 500 chars, which should contain the copyright
```
"""

        try:
            response = self.llm_client.generate_response(prompt, system_prompt)

            # Parse the response - we expect a JSON object
            try:
                result = json.loads(response)
                copyright_holder = result.get("copyright_holder", "Unknown")

                return copyright_holder

            except json.JSONDecodeError:
                # If the response isn't valid JSON, fallback to Unknown
                return "Unknown"

        except Exception as e:
            # If LLM request fails, fallback to Unknown
            logging.error("Error extracting copyright holder with LLM: %s", str(e))
            return "Unknown"
