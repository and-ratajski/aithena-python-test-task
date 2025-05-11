"""Tests for AI services."""

import json
from unittest.mock import patch, MagicMock

import pytest
from pydantic_ai import Agent

from src.data_models.response_models import LicenseType
from src.data_models.analysis_models import FunctionInfo
from src.services.ai_services import (
    detect_license,
    extract_copyright_holder,
    count_functions,
    extract_functions_with_args,
    rewrite_to_rust,
    license_agent,
    copyright_agent,
    function_count_agent,
    function_extractor_agent,
    rust_agent,
    LicenseInfo,
    CopyrightInfo,
    FunctionCountInfo,
    RustTranslation,
)


class TestAIServices:
    """Test suite for AI services using Pydantic AI."""

    def test_detect_license(self):
        """Test license detection with Pydantic AI."""
        # Create a mock response
        mock_result = MagicMock()
        mock_result.output = LicenseInfo(license_type="COPYLEFT", license_name="GNU GPL v3")

        # Patch the Agent.run_sync method
        with patch.object(license_agent, "run_sync", return_value=mock_result):
            result = detect_license("Sample GPL content")

            assert result.license_type == "COPYLEFT"
            assert "GPL" in result.license_name

        # Test the fallback path when agent raises an exception
        with patch.object(license_agent, "run_sync", side_effect=Exception("Test exception")):
            # With GPL in content
            result = detect_license("GPL licensed content")
            assert result.license_type == "COPYLEFT"
            assert result.license_name == "GNU GPL v3"

            # With MIT in content
            result = detect_license("MIT License content")
            assert result.license_type == "PERMISSIVE"
            assert result.license_name == "MIT License"

    def test_extract_copyright_holder(self):
        """Test copyright holder extraction with Pydantic AI."""
        # Create a mock response
        mock_result = MagicMock()
        mock_result.output = CopyrightInfo(copyright_holder="Acme Corp")

        # Patch the Agent.run_sync method
        with patch.object(copyright_agent, "run_sync", return_value=mock_result):
            result = extract_copyright_holder("Copyright (c) 2023 Acme Corp")

            assert result.copyright_holder == "Acme Corp"

        # Test the fallback path when agent raises an exception
        with patch.object(copyright_agent, "run_sync", side_effect=Exception("Test exception")):
            # With Elon Musk in content
            result = extract_copyright_holder("Copyright (c) 2023 Elon Musk")
            assert result.copyright_holder == "Elon Musk"

    def test_count_functions(self):
        """Test function counting with Pydantic AI."""
        # Create a mock response
        mock_result = MagicMock()
        mock_result.output = FunctionCountInfo(function_count=3)

        # Sample Python code with 3 functions
        code = """
        def func1():
            pass

        def func2(a, b):
            return a + b

        def func3(x):
            return x * 2
        """

        # Patch the Agent.run_sync method
        with patch.object(function_count_agent, "run_sync", return_value=mock_result):
            result = count_functions(code)

            assert result.function_count == 3

        # Test the fallback path when agent raises an exception
        with patch.object(function_count_agent, "run_sync", side_effect=Exception("Test exception")):
            # With foo and bar
            result = count_functions("def foo():\n    pass\n\ndef bar():\n    pass")
            assert result.function_count == 2

    def test_extract_functions_with_args(self):
        """Test function extraction with Pydantic AI."""
        # Create a mock response
        mock_result = MagicMock()
        mock_result.output = [
            FunctionInfo(name="func1", arg_count=0),
            FunctionInfo(name="func2", arg_count=2),
            FunctionInfo(name="func3", arg_count=1)
        ]

        # Sample Python code with 3 functions
        code = """
        def func1():
            pass

        def func2(a, b):
            return a + b

        def func3(x):
            return x * 2
        """

        # Patch the Agent.run_sync method
        with patch.object(function_extractor_agent, "run_sync", return_value=mock_result):
            result = extract_functions_with_args(code)

            assert len(result) == 3
            assert result[0].name == "func1"
            assert result[0].arg_count == 0
            assert result[1].name == "func2"
            assert result[1].arg_count == 2
            assert result[2].name == "func3"
            assert result[2].arg_count == 1

        # Test the fallback path when agent raises an exception
        with patch.object(function_extractor_agent, "run_sync", side_effect=Exception("Test exception")):
            result = extract_functions_with_args("def foo():\n    pass\n\ndef bar():\n    pass")
            assert len(result) == 2
            assert result[0].name == "foo"
            assert result[1].name == "bar"

    def test_rewrite_to_rust(self):
        """Test Rust code rewriting with Pydantic AI."""
        # Create a mock response
        mock_result = MagicMock()
        mock_result.output = RustTranslation(rust_code='fn main() {\n    println!("Hello from Rust");\n}')

        # Sample Python code
        code = """
        def main():
            print("Hello from Python")

        if __name__ == "__main__":
            main()
        """

        # Patch the Agent.run_sync method
        with patch.object(rust_agent, "run_sync", return_value=mock_result):
            result = rewrite_to_rust(code)

            assert 'println!' in result.rust_code
            assert "Hello from Rust" in result.rust_code

        # Test the fallback path when agent raises an exception
        with patch.object(rust_agent, "run_sync", side_effect=Exception("Test exception")):
            result = rewrite_to_rust("def foo():\n    pass\n\ndef bar():\n    pass")
            assert "fn foo()" in result.rust_code
            assert "fn bar()" in result.rust_code