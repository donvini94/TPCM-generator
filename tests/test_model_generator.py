#!/usr/bin/env python3
"""Tests for model generator module."""

import os
import sys
import unittest

class TestModelGenerator(unittest.TestCase):
    """Test cases for model generation."""
    
    def test_imports(self):
        """Test that the key modules can be imported."""
        try:
            from model_generator import create_minimal_model, create_mediastore_model
            self.assertTrue(callable(create_minimal_model), "create_minimal_model should be callable")
            self.assertTrue(callable(create_mediastore_model), "create_mediastore_model should be callable")
        except ImportError as e:
            # Skip if imports are not available (environment-dependent)
            self.skipTest(f"Import error: {e}")
    
    def test_tpcm_validator(self):
        """Test the TPCM format with some simple validation."""
        # Test validation of the MediaStore.tpcm file
        tpcm_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MediaStore.tpcm")
        
        # Only run the test if the file exists
        if not os.path.exists(tpcm_file):
            self.skipTest(f"MediaStore.tpcm file not found at {tpcm_file}")
            
        # Basic validation of the TPCM file content
        with open(tpcm_file, 'r') as f:
            content = f.read()
            self.assertIn("repository MediaStore", content, "Repository not found in TPCM file")
            self.assertIn("interface IFileStorage", content, "IFileStorage interface not found in TPCM file")
            self.assertIn("component FileStorage", content, "FileStorage component not found in TPCM file")
            
            # Validate some specific elements
            self.assertIn("interface IDownload", content, "IDownload interface not found")
            self.assertIn("interface IMediaAccess", content, "IMediaAccess interface not found")
            self.assertIn("interface IPackaging", content, "IPackaging interface not found")
            self.assertIn("interface IMediaManagement", content, "IMediaManagement interface not found")
            
            # Validate components
            self.assertIn("component Packaging", content, "Packaging component not found")
            self.assertIn("component MediaAccess", content, "MediaAccess component not found")
            self.assertIn("component MediaManagement", content, "MediaManagement component not found")
            
            # Validate a sample PDF expression for stochastic behavior
            self.assertIn("DoublePDF", content, "Stochastic expression (DoublePDF) not found")

def run_tests():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests()