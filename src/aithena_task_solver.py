"""AITHENA Task Solver implementation.

This module contains the main logic for solving the AITHENA test task as described in task.md.
It analyzes Python files, extracts license information, counts and extracts functions,
and saves results in the appropriate format.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from src.llm.protocols import LlmClient
from src.services.function_counter import FunctionCounter, FunctionCounterError
from src.services.license_detector import LicenseDetector, LicenseType


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


class TaskSolverError(Exception):
    """Exception raised for errors in the task solver."""
    pass


def extract_functions_with_args(llm_client: LlmClient, file_content: str) -> List[FunctionInfo]:
    """Extract function names and argument counts from code using LLM.

    Args:
        llm_client: An implementation of the LlmClient Protocol
        file_content: The content of the file to analyze

    Returns:
        A list of FunctionInfo objects with function names and argument counts

    Raises:
        TaskSolverError: If extracting function information fails
    """
    system_prompt = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to extract all function names and count the number of arguments for each function.
Include class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly required.
Be precise and focus only on the function extraction task.
"""

    prompt = f"""Analyze the following code and extract all function names along with the number of arguments each function takes.
Count only real parameters, not self or cls for methods.
Include standalone functions and class methods but exclude built-in special methods (like __init__, __str__, etc.) unless explicitly asked.

Respond ONLY with a JSON array where each element is an object with two fields:
1. "name": The function name as a string
2. "arg_count": The number of arguments as an integer

Examples:
---
Code: 
```python
def add(a, b):
    return a + b
    
def subtract(a, b):
    return a - b
```
Response: [{{"name": "add", "arg_count": 2}}, {{"name": "subtract", "arg_count": 2}}]

---
Code:
```python
class Calculator:
    def __init__(self, initial=0):
        self.value = initial
        
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        return a - b
        
def multiply(a, b):
    return a * b
```
Response: [{{"name": "add", "arg_count": 2}}, {{"name": "subtract", "arg_count": 2}}, {{"name": "multiply", "arg_count": 2}}]

---
Now extract the functions from this code:
```
{file_content}
```
"""

    try:
        response = llm_client.generate_response(prompt, system_prompt)

        # Parse the response - we expect a JSON array
        try:
            result = json.loads(response)

            # Validate the response
            if not isinstance(result, list):
                raise TaskSolverError("Invalid function information returned by LLM")

            functions = []
            for item in result:
                name = item.get("name")
                arg_count = item.get("arg_count")

                if (name is None or not isinstance(name, str) or
                        arg_count is None or not isinstance(arg_count, int) or arg_count < 0):
                    raise TaskSolverError("Invalid function information format")

                functions.append(FunctionInfo(name=name, arg_count=arg_count))

            return functions

        except json.JSONDecodeError as e:
            # If the response isn't valid JSON, raise an error
            raise TaskSolverError(f"Failed to parse LLM response as JSON: {str(e)}")

    except Exception as e:
        # Catch any errors
        raise TaskSolverError(f"Error extracting function information: {str(e)}")


def extract_copyright_holder(llm_client: LlmClient, file_content: str) -> str:
    """Extract copyright holder from code file using LLM.

    Args:
        llm_client: An implementation of the LlmClient Protocol
        file_content: The content of the file to analyze

    Returns:
        The name of the copyright holder

    Raises:
        TaskSolverError: If extracting copyright information fails
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
```
Response: {{"copyright_holder": "Google LLC"}}

---
Now extract the copyright holder from this file:
```
{file_content[:500]}  # Only send the first 500 chars, which should contain the copyright
```
"""

    try:
        response = llm_client.generate_response(prompt, system_prompt)

        # Parse the response - we expect a JSON object
        try:
            result = json.loads(response)
            copyright_holder = result.get("copyright_holder", "Unknown")

            return copyright_holder

        except json.JSONDecodeError:
            # If the response isn't valid JSON, fallback to Unknown
            return "Unknown"

    except Exception:
        # If LLM request fails, fallback to Unknown
        return "Unknown"


def save_result_to_json(result: FileAnalysisResult, output_dir: str) -> str:
    """Save analysis result to a JSON file.

    Args:
        result: The FileAnalysisResult to save
        output_dir: The directory to save the result to

    Returns:
        The path to the saved file

    Raises:
        TaskSolverError: If saving fails
    """
    # Create directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create output file path
    file_name_stem = Path(result.file_name).stem
    output_file = os.path.join(output_dir, f"{file_name_stem}_analysis.json")

    # Convert result to dict
    result_dict = {
        "file_name": result.file_name,
        "copyright_holder": result.copyright_holder,
        "license_name": result.license_name,
        "license_type": result.license_type.name,
    }

    # Add function information if available
    if result.function_count is not None:
        result_dict["function_count"] = result.function_count

    if result.functions is not None:
        result_dict["functions"] = [
            {"name": f.name, "arg_count": f.arg_count}
            for f in result.functions
        ]

    try:
        with open(output_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
        return output_file
    except Exception as e:
        raise TaskSolverError(f"Failed to save result to JSON: {str(e)}")


def save_rust_code(file_name: str, rust_code: str, output_dir: str) -> str:
    """Save Rust code to a file.

    Args:
        file_name: The original file name
        rust_code: The Rust code to save
        output_dir: The directory to save the code to

    Returns:
        The path to the saved file

    Raises:
        TaskSolverError: If saving fails
    """
    # Create directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create output file path
    file_name_stem = Path(file_name).stem
    output_file = os.path.join(output_dir, f"{file_name_stem}_rust_functions.rs")

    try:
        with open(output_file, 'w') as f:
            f.write(rust_code)
        return output_file
    except Exception as e:
        raise TaskSolverError(f"Failed to save Rust code: {str(e)}")


def process_file(llm_client: LlmClient, file_name: str, file_content: str) -> Tuple[FileAnalysisResult, List[str]]:
    """Process a file according to the AITHENA task requirements.

    This is the main function that implements the logic described in task.md.

    Args:
        llm_client: An implementation of the LlmClient Protocol
        file_name: The name of the file being processed
        file_content: The content of the file to analyze

    Returns:
        A tuple of (FileAnalysisResult, list of saved file paths)

    Raises:
        TaskSolverError: If processing fails
    """
    output_dir = "results"
    saved_files = []

    try:
        # Initialize services
        license_detector = LicenseDetector(llm_client)
        function_counter = FunctionCounter(llm_client)

        # Detect license
        license_type, license_name = license_detector.get_license_type(file_content)

        # Extract copyright holder
        copyright_holder = extract_copyright_holder(llm_client, file_content)

        # Initialize result
        result = FileAnalysisResult(
            file_name=file_name,
            copyright_holder=copyright_holder,
            license_name=license_name,
            license_type=license_type
        )

        # Apply logic based on license type
        if license_type == LicenseType.PERMISSIVE:
            # For permissive licenses: extract function names with arg counts
            result.functions = extract_functions_with_args(llm_client, file_content)

        elif license_type == LicenseType.COPYLEFT:
            # For copyleft licenses: count functions first
            function_count = function_counter.count_functions(file_content)
            result.function_count = function_count

            if function_count > 2:
                # If more than 2 functions: extract function names with arg counts
                result.functions = extract_functions_with_args(llm_client, file_content)
            else:
                # If 2 or fewer functions: rewrite to Rust
                rust_code = llm_client.rewrite_to_rust(file_content)
                result.rust_code = rust_code

                # Save Rust code
                rust_file_path = save_rust_code(file_name, rust_code, output_dir)
                saved_files.append(rust_file_path)

        # For all cases: save structured data
        json_file_path = save_result_to_json(result, output_dir)
        saved_files.append(json_file_path)

        return result, saved_files

    except Exception as e:
        raise TaskSolverError(f"Failed to process file {file_name}: {str(e)}")