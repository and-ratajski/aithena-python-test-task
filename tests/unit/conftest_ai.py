"""Test fixtures and mocks for Pydantic AI."""

import json
from unittest.mock import patch, MagicMock

import pytest
import pydantic_ai

# Mock the agent decorator in pydantic_ai
@pytest.fixture(autouse=True)
def mock_pydantic_ai():
    """Mock Pydantic AI for testing."""
    with patch('pydantic_ai.agent') as mock_agent:
        # Make the agent decorator a pass-through function
        mock_agent.return_value = lambda func: func
        yield mock_agent
        
# Mock the API responses
@pytest.fixture
def mock_license_response():
    """Mock license detection response."""
    def _create_mock(license_type, license_name):
        return {"license_type": license_type, "license_name": license_name}
    return _create_mock

@pytest.fixture
def mock_copyright_response():
    """Mock copyright extraction response."""
    def _create_mock(copyright_holder):
        return {"copyright_holder": copyright_holder}
    return _create_mock

@pytest.fixture
def mock_function_count_response():
    """Mock function counting response."""
    def _create_mock(count):
        return {"function_count": count}
    return _create_mock

@pytest.fixture
def mock_functions_response():
    """Mock function extraction response."""
    def _create_mock(functions):
        return [{"name": f["name"], "arg_count": f["arg_count"]} for f in functions]
    return _create_mock

@pytest.fixture
def mock_rust_response():
    """Mock Rust code translation response."""
    def _create_mock(rust_code):
        return {"rust_code": rust_code}
    return _create_mock