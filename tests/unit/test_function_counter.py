"""Tests for the function counter module."""
import json
from unittest.mock import MagicMock

import pytest

from src.services.function_handlers import FunctionCounter, FunctionCounterError


class MockLlmClient:
    """Mock implementation of LlmClient for testing."""
    
    def __init__(self, function_count_responses=None):
        """Initialize with optional mock responses."""
        self.function_count_responses = function_count_responses or {}
        self.current_test = None
        
    def generate_response(self, prompt, system_prompt=None, **kwargs):
        """Return a mock response based on current test name."""
        # Default response for empty code
        default_response = json.dumps({"function_count": 0})
        
        # Get the name of the current test method from the call stack
        import traceback
        frame_info = traceback.extract_stack()
        for frame in reversed(frame_info):
            func_name = frame[2]
            if func_name.startswith('test_'):
                self.current_test = func_name
                break
        
        # Return response based on current test
        if self.current_test in self.function_count_responses:
            return self.function_count_responses[self.current_test]
                
        return default_response
        
    def rewrite_to_rust(self, python_code):
        """Return a mock Rust code."""
        return "// Mock Rust code"


class TestFunctionCounter:
    """Test suite for the FunctionCounter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # For each test case, define exactly what should be returned
        self.mock_responses = {
            "test_count_two_functions": json.dumps({
                "function_count": 2
            }),
            "test_count_class_methods": json.dumps({
                "function_count": 3
            }),
            "test_count_no_functions": json.dumps({
                "function_count": 0
            }),
            "test_count_complex_file": json.dumps({
                "function_count": 5
            }),
        }
        
        self.mock_llm = MockLlmClient(self.mock_responses)
        self.counter = FunctionCounter(self.mock_llm)
    
    def test_count_two_functions(self):
        """Test counting two simple functions."""
        content = """
        def add(a, b):
            return a + b
            
        def subtract(a, b):
            return a - b
        """
        
        function_count = self.counter.count_functions(content)
        
        assert function_count == 2
    
    def test_count_class_methods(self):
        """Test counting class methods and standalone functions."""
        content = """
        class Calculator:
            def add(self, a, b):
                return a + b
                
            def subtract(self, a, b):
                return a - b
                
        def multiply(a, b):
            return a * b
        """
        
        function_count = self.counter.count_functions(content)
        
        assert function_count == 3
    
    def test_count_no_functions(self):
        """Test counting when there are no functions."""
        content = """
        import math

        # No functions here
        x = 10
        y = 20
        result = x + y
        """
        
        function_count = self.counter.count_functions(content)
        
        assert function_count == 0
    
    def test_count_complex_file(self):
        """Test counting functions in a more complex file."""
        content = """
        import os
        from typing import List, Dict, Any

        def function1(arg1, arg2=None):
            '''This is function 1'''
            return arg1 + arg2
            
        class MyClass:
            def __init__(self, value):
                self.value = value
                
            def method1(self):
                return self.value
                
            def method2(self, x):
                return self.value + x
                
        # Lambda doesn't count as a named function
        my_lambda = lambda x: x * 2
                
        def function2(items: List[str]) -> Dict[str, Any]:
            result = {}
            for item in items:
                result[item] = len(item)
            return result
        """
        
        function_count = self.counter.count_functions(content)
        
        assert function_count == 5  # 2 standalone functions + 3 methods
    
    def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Create a mock that raises an exception
        error_llm = MagicMock()
        error_llm.generate_response.side_effect = Exception("LLM API error")
        
        counter = FunctionCounter(error_llm)
        
        # Must bypass the pattern-based detection for this test
        # Use content that won't be recognized by the patterns
        content = """
        THIS IS NOT VALID CODE AND WILL FORCE LLM FALLBACK
        """
        
        # Directly test the LLM-based method
        with pytest.raises(FunctionCounterError) as exc_info:
            counter._count_functions_with_llm(content)
            
        assert "error" in str(exc_info.value).lower()
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses from LLM."""
        # Create a mock that returns invalid JSON
        invalid_json_llm = MagicMock()
        invalid_json_llm.generate_response.return_value = "Not a valid JSON response"
        
        counter = FunctionCounter(invalid_json_llm)
        
        # Directly test the LLM-based method
        with pytest.raises(FunctionCounterError) as exc_info:
            counter._count_functions_with_llm("some content")
            
        assert "json" in str(exc_info.value).lower()
    
    def test_invalid_function_count(self):
        """Test handling of invalid function count value in response."""
        # Create mocks that return invalid function count values
        for invalid_value, mock_response in [
            ("string", json.dumps({"function_count": "two"})),
            (-1, json.dumps({"function_count": -1})),
            (None, json.dumps({"wrong_field": 3}))
        ]:
            invalid_llm = MagicMock()
            invalid_llm.generate_response.return_value = mock_response
            
            counter = FunctionCounter(invalid_llm)
            
            # Directly test the LLM-based method
            with pytest.raises(FunctionCounterError) as exc_info:
                counter._count_functions_with_llm("some content")
                
            assert "invalid" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()