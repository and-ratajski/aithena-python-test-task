"""Tests for the license detector module."""
import json
from unittest.mock import MagicMock

from src.services.license_detector import LicenseDetector, LicenseType


class MockLlmClient:
    """Mock implementation of LlmClient for testing."""
    
    def __init__(self, license_responses=None):
        """Initialize with optional mock responses."""
        self.license_responses = license_responses or {}
        self.current_test = None
        
    def generate_response(self, prompt, system_prompt=None, **kwargs):
        """Return a mock response based on current test name."""
        # Default response for unknown license
        default_response = json.dumps({"license_type": "UNKNOWN", "license_name": "Unknown License"})
        
        # Get the name of the current test method from the call stack
        import traceback
        frame_info = traceback.extract_stack()
        for frame in reversed(frame_info):
            func_name = frame[2]
            if func_name.startswith('test_'):
                self.current_test = func_name
                break
        
        # Return response based on current test
        if self.current_test in self.license_responses:
            return self.license_responses[self.current_test]
                
        return default_response
        
    def rewrite_to_rust(self, python_code):
        """Return a mock Rust code."""
        return "// Mock Rust code"


class TestLicenseDetector:
    """Test suite for the LicenseDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # For each test case, define exactly what should be returned
        self.mock_responses = {
            "test_detect_gpl_license": json.dumps({
                "license_type": "COPYLEFT", 
                "license_name": "GNU GPL v3"
            }),
            "test_detect_mit_license": json.dumps({
                "license_type": "PERMISSIVE", 
                "license_name": "MIT License"
            }),
            "test_detect_apache_license": json.dumps({
                "license_type": "PERMISSIVE", 
                "license_name": "Apache License 2.0"
            }),
            "test_detect_proprietary_license": json.dumps({
                "license_type": "PROPRIETARY", 
                "license_name": "Proprietary"
            }),
            "test_unknown_license": json.dumps({
                "license_type": "UNKNOWN", 
                "license_name": "Unknown License"
            })
        }
        
        self.mock_llm = MockLlmClient(self.mock_responses)
        self.detector = LicenseDetector(self.mock_llm)
    
    def test_detect_gpl_license(self):
        """Test detection of GPL license."""
        content = """
        # Foobar is free software: you can redistribute it and/or modify it under the
        # terms of the GNU General Public License as published by the Free Software
        # Foundation, either version 3 of the License, or (at your option) any later
        # version.
        """
        
        license_type, license_name = self.detector.get_license_type(content)
        
        assert license_type == LicenseType.COPYLEFT
        assert "GPL" in license_name
    
    def test_detect_mit_license(self):
        """Test detection of MIT license."""
        content = """
        // MIT License
        //
        // Permission is hereby granted, free of charge, to any person obtaining a copy
        // of this software and associated documentation files (the "Software"), to deal
        // in the Software without restriction, including without limitation the rights
        // to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        // copies of the Software, and to permit persons to whom the Software is
        // furnished to do so.
        """
        
        license_type, license_name = self.detector.get_license_type(content)
        
        assert license_type == LicenseType.PERMISSIVE
        assert "MIT" in license_name
    
    def test_detect_apache_license(self):
        """Test detection of Apache license."""
        content = """
        # Licensed under the Apache License, Version 2.0 (the "License");
        """
        
        license_type, license_name = self.detector.get_license_type(content)
        
        assert license_type == LicenseType.PERMISSIVE
        assert "Apache" in license_name
    
    def test_detect_proprietary_license(self):
        """Test detection of proprietary license."""
        content = """
        // All Rights Reserved.
        """
        
        license_type, license_name = self.detector.get_license_type(content)
        
        assert license_type == LicenseType.PROPRIETARY
        assert "Proprietary" in license_name
    
    def test_unknown_license(self):
        """Test handling of unknown license."""
        content = """
        # This is some code without a clear license
        
        def foo():
            pass
        """
        
        license_type, license_name = self.detector.get_license_type(content)
        
        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"
    
    def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Create a mock that raises an exception
        error_llm = MagicMock()
        error_llm.generate_response.side_effect = Exception("LLM API error")
        
        detector = LicenseDetector(error_llm)
        
        content = """
        # Some license text
        """
        
        license_type, license_name = detector.get_license_type(content)
        
        # Should fallback to UNKNOWN
        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses from LLM."""
        # Create a mock that returns invalid JSON
        invalid_json_llm = MagicMock()
        invalid_json_llm.generate_response.return_value = "Not a valid JSON response"
        
        detector = LicenseDetector(invalid_json_llm)
        
        content = """
        # Some license text
        """
        
        license_type, license_name = detector.get_license_type(content)
        
        # Should fallback to UNKNOWN
        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"