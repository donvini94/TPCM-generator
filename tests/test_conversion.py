#!/usr/bin/env python3
"""Tests for TPCM model conversion."""

import os
import sys
import unittest

class TestConversion(unittest.TestCase):
    """Test cases for model conversion to TPCM format."""
    
    def test_converter_exists(self):
        """Test that the SaveAs.jar converter exists."""
        converter_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "SaveAs.jar"
        )
        self.assertTrue(os.path.exists(converter_path), 
                        f"Converter not found at {converter_path}")
    
    def test_mediastore_tpcm_format(self):
        """Test that MediaStore.tpcm follows the expected format."""
        mediastore_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "MediaStore.tpcm"
        )
        
        if not os.path.exists(mediastore_path):
            self.skipTest(f"MediaStore.tpcm not found at {mediastore_path}")
        
        with open(mediastore_path, 'r') as f:
            content = f.read()
        
        # Check for expected TPCM syntax and structure
        self.assertIn("repository MediaStore {", content, 
                      "Repository declaration should be properly formatted")
        
        # Check component declarations
        self.assertIn("component FileStorage {", content,
                      "Component declaration should be properly formatted")
        
        # Check interface declarations
        self.assertIn("interface IFileStorage {", content,
                      "Interface declaration should be properly formatted")
        
        # Check operation declarations
        self.assertIn("op getFiles(", content,
                      "Operation declaration should be properly formatted")
        
        # Check SEFFs
        self.assertIn("seff", content, "SEFF declarations should exist")
        
        # Check expressions
        self.assertIn("«", content, "Stochastic expressions should be properly formatted")

if __name__ == "__main__":
    unittest.main()