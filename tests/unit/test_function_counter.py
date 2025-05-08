"""Tests for the function counter module."""

import pytest

from src.services.function_handlers import FunctionCounter, FunctionCounterError


class TestFunctionCounter:
    """Test suite for the FunctionCounter class."""

    def test_count_two_functions(self, function_counter_mock):
        """Test counting two simple functions."""
        mock_llm = function_counter_mock(2)
        counter = FunctionCounter(mock_llm)

        content = """
        def add(a, b):
            return a + b
            
        def subtract(a, b):
            return a - b
        """
        function_count = counter.count_functions(content)
        assert function_count == 2

    def test_count_class_methods(self, function_counter_mock):
        """Test counting class methods and standalone functions."""
        mock_llm = function_counter_mock(3)
        counter = FunctionCounter(mock_llm)

        content = """
        class Calculator:
            def add(self, a, b):
                return a + b
                
            def subtract(self, a, b):
                return a - b
                
        def multiply(a, b):
            return a * b
        """
        function_count = counter.count_functions(content)
        assert function_count == 3

    def test_count_no_functions(self, function_counter_mock):
        """Test counting when there are no functions."""
        mock_llm = function_counter_mock(0)
        counter = FunctionCounter(mock_llm)

        content = """
        import math

        # No functions here
        x = 10
        y = 20
        result = x + y
        """
        function_count = counter.count_functions(content)
        assert function_count == 0

    def test_count_complex_file(self, function_counter_mock):
        """Test counting functions in a more complex file."""
        mock_llm = function_counter_mock(5)
        counter = FunctionCounter(mock_llm)

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
        function_count = counter.count_functions(content)
        assert function_count == 5  # 2 standalone functions + 3 methods

    def test_llm_error_handling(self, llm_mock_factory):
        """Test handling of LLM errors."""

        def raise_error(*args, **kwargs):
            raise Exception("LLM API error")

        mock_llm = llm_mock_factory(raise_error)
        counter = FunctionCounter(mock_llm)

        with pytest.raises(FunctionCounterError) as exc_info:
            counter._count_functions_with_llm("Sample content")

        assert "error" in str(exc_info.value).lower()

    def test_invalid_json_response(self, llm_mock_factory):
        """Test handling of invalid JSON responses from LLM."""
        mock_llm = llm_mock_factory("Not a valid JSON response")
        counter = FunctionCounter(mock_llm)

        with pytest.raises(FunctionCounterError) as exc_info:
            counter._count_functions_with_llm("Sample content")

        assert "json" in str(exc_info.value).lower()

    def test_invalid_function_count(self, llm_mock_factory):
        """Test handling of invalid function count value in response."""
        invalid_values = [
            ("string", '{"function_count": "two"}'),
            ("negative", '{"function_count": -1}'),
            ("missing", '{"wrong_field": 3}'),
        ]

        for test_name, mock_response in invalid_values:
            mock_llm = llm_mock_factory(mock_response)
            counter = FunctionCounter(mock_llm)

            with pytest.raises(FunctionCounterError) as exc_info:
                counter._count_functions_with_llm("Sample content")

            assert "invalid" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()
