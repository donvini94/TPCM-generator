#!/usr/bin/env python3
"""Tests for TPCM model conversion."""

import os
import sys
import subprocess
import unittest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_generator import create_minimal_model

class TestConversion(unittest.TestCase):
    """Test cases for model conversion to TPCM format."""
    
    def test_conversion_to_tpcm(self):
        """Test that a model can be converted to TPCM format."""
        test_xml = "test_conversion.xml"
        test_tpcm = "test_conversion.tpcm"
        
        try:
            # Create minimal model
            model = create_minimal_model(test_xml)
            
            # Check that XML file exists
            self.assertTrue(os.path.exists(test_xml), f"Model file {test_xml} not created")
            
            # Try to convert to TPCM
            result = subprocess.run(
                ["java", "-jar", "SaveAs.jar", test_xml, test_tpcm],
                capture_output=True,
                text=True
            )
            
            # Check conversion result
            self.assertEqual(result.returncode, 0, 
                             f"Conversion failed: {result.stderr}")
            
            # Check that TPCM file exists
            self.assertTrue(os.path.exists(test_tpcm), 
                            f"TPCM file {test_tpcm} not created")
            
            # Check TPCM file content
            with open(test_tpcm, 'r') as f:
                content = f.read()
                
            # Basic checks on TPCM content
            self.assertIn("repository MinimalRepository", content, 
                          "Repository not found in TPCM")
            self.assertIn("interface IFileStorage", content, 
                          "Interface not found in TPCM")
            
        finally:
            # Clean up
            for f in [test_xml, test_tpcm]:
                if os.path.exists(f):
                    os.remove(f)

def run_tests():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests()