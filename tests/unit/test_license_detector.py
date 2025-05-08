"""Tests for the license detector module."""

from src.data_models.license_types import LicenseType
from src.services.license_detector import LicenseDetector


class TestLicenseDetector:
    """Test suite for the LicenseDetector class."""

    def test_detect_gpl_license(self, license_detector_mock):
        """Test detection of GPL license."""
        mock_llm = license_detector_mock("COPYLEFT", "GNU GPL v3")
        detector = LicenseDetector(mock_llm)

        content = """
        # Foobar is free software: you can redistribute it and/or modify it under the
        # terms of the GNU General Public License as published by the Free Software
        # Foundation, either version 3 of the License, or (at your option) any later
        # version.
        """
        license_type, license_name = detector.get_license_type(content)

        assert license_type == LicenseType.COPYLEFT
        assert "GPL" in license_name

    def test_detect_mit_license(self, license_detector_mock):
        """Test detection of MIT license."""
        mock_llm = license_detector_mock("PERMISSIVE", "MIT License")
        detector = LicenseDetector(mock_llm)

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
        license_type, license_name = detector.get_license_type(content)

        assert license_type == LicenseType.PERMISSIVE
        assert "MIT" in license_name

    def test_detect_apache_license(self, license_detector_mock):
        """Test detection of Apache license."""
        mock_llm = license_detector_mock("PERMISSIVE", "Apache License 2.0")
        detector = LicenseDetector(mock_llm)

        content = '# Licensed under the Apache License, Version 2.0 (the "License");'
        license_type, license_name = detector.get_license_type(content)

        assert license_type == LicenseType.PERMISSIVE
        assert "Apache" in license_name

    def test_detect_proprietary_license(self, license_detector_mock):
        """Test detection of proprietary license."""
        mock_llm = license_detector_mock("PROPRIETARY", "Proprietary")
        detector = LicenseDetector(mock_llm)

        content = "// All Rights Reserved."
        license_type, license_name = detector.get_license_type(content)

        assert license_type == LicenseType.PROPRIETARY
        assert "Proprietary" in license_name

    def test_unknown_license(self, license_detector_mock):
        """Test handling of unknown license."""
        mock_llm = license_detector_mock("UNKNOWN", "Unknown License")
        detector = LicenseDetector(mock_llm)

        content = """
        # This is some code without a clear license
        
        def foo():
            pass
        """
        license_type, license_name = detector.get_license_type(content)

        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"

    def test_llm_error_handling(self, llm_mock_factory):
        """Test handling of LLM errors."""

        def raise_error(*args, **kwargs):
            raise Exception("LLM API error")

        mock_llm = llm_mock_factory(raise_error)
        detector = LicenseDetector(mock_llm)

        license_type, license_name = detector.get_license_type("Sample content")

        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"

    def test_invalid_json_response(self, llm_mock_factory):
        """Test handling of invalid JSON responses from LLM."""
        mock_llm = llm_mock_factory("Not a valid JSON response")
        detector = LicenseDetector(mock_llm)

        license_type, license_name = detector.get_license_type("Sample content")

        assert license_type == LicenseType.UNKNOWN
        assert license_name == "Unknown License"
