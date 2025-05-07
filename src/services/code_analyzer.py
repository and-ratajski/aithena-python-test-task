"""Code analyzer implementation.

This module contains functionality for analyzing code files and extracting metadata.
"""
import json
from typing import List

from src.data_models.analysis_models import FunctionInfo
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
            print(f"Error extracting copyright holder with LLM: {str(e)}")
            return "Unknown"


class FunctionExtractor:
    """Extracts function information from code files using LLM."""
    
    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the function extractor with an LLM client.
        
        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client
    
    def extract_functions_with_args(self, file_content: str) -> List[FunctionInfo]:
        """Extract function names and argument counts from code using LLM.
        
        Args:
            file_content: The content of the file to analyze
            
        Returns:
            A list of FunctionInfo objects with function names and argument counts
            
        Raises:
            CodeAnalyzerError: If extracting function information fails
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
            response = self.llm_client.generate_response(prompt, system_prompt)
            
            # Parse the response - we expect a JSON array
            try:
                result = json.loads(response)
                
                # Validate the response
                if not isinstance(result, list):
                    raise CodeAnalyzerError("Invalid function information returned by LLM")
                
                functions = []
                for item in result:
                    name = item.get("name")
                    arg_count = item.get("arg_count")
                    
                    if (name is None or not isinstance(name, str) or
                            arg_count is None or not isinstance(arg_count, int) or arg_count < 0):
                        raise CodeAnalyzerError("Invalid function information format")
                    
                    functions.append(FunctionInfo(name=name, arg_count=arg_count))
                
                return functions
                
            except json.JSONDecodeError as e:
                # If the response isn't valid JSON, raise an error
                raise CodeAnalyzerError(f"Failed to parse LLM response as JSON: {str(e)}")
                
        except Exception as e:
            # Catch any errors
            raise CodeAnalyzerError(f"Error extracting function information: {str(e)}")