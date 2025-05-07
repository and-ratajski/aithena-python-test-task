"""Function counter implementation.

This module contains functionality for counting functions in code files using LLM.
"""
import json

from src.llm.protocols import LlmClient, LLMClientError


class FunctionCounterError(Exception):
    """Exception raised for errors in the function counter."""
    pass


class FunctionCounter:
    """Counts functions in code files using LLM."""
    
    def __init__(self, llm_client: LlmClient) -> None:
        """Initialize the function counter with an LLM client.
        
        Args:
            llm_client: An implementation of the LlmClient Protocol
        """
        self.llm_client = llm_client
    
    def count_functions(self, file_content: str) -> int:
        """Count the number of functions in a file using LLM.
        
        Args:
            file_content: The content of the file to analyze
            
        Returns:
            The number of functions in the file
            
        Raises:
            FunctionCounterError: If counting functions fails
        """
        system_prompt = """You are an expert code analyzer specialized in identifying functions in code.
Your task is to count the exact number of function definitions in the provided code.
Focus only on function counting. Be precise and return only the count as a number.
"""
        
        prompt = f"""Analyze the following code and count the number of function definitions it contains.
Respond ONLY with a JSON object with a single field "function_count" which contains the integer number of functions found.

Examples:
---
Code: 
```python
def add(a, b):
    return a + b
    
def subtract(a, b):
    return a - b
```
Response: {{"function_count": 2}}

---
Code:
```python
class Calculator:
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        return a - b
        
def multiply(a, b):
    return a * b
```
Response: {{"function_count": 3}}

---
Code:
```python
import math

# No functions here
x = 10
y = 20
result = x + y
```
Response: {{"function_count": 0}}

---
Now count the functions in this code:
```
{file_content}
```
"""
        
        try:
            response = self.llm_client.generate_response(prompt, system_prompt)
            
            # Parse the response - we expect a JSON object
            try:
                result = json.loads(response)
                function_count = result.get("function_count")
                
                # Validate the response
                if function_count is None or not isinstance(function_count, int) or function_count < 0:
                    raise FunctionCounterError("Invalid function count returned by LLM")
                
                return function_count
                
            except json.JSONDecodeError as e:
                # If the response isn't valid JSON, raise an error
                raise FunctionCounterError(f"Failed to parse LLM response as JSON: {str(e)}")
                
        except LLMClientError as e:
            # If LLM request fails, raise a specific error
            raise FunctionCounterError(f"LLM request failed: {str(e)}")
        except Exception as e:
            # Catch any other unexpected errors
            raise FunctionCounterError(f"Unexpected error counting functions: {str(e)}")