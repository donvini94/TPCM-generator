#!/usr/bin/env python3
"""Tests for model generator module."""

import os
import sys
import subprocess
import unittest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_generator import create_minimal_model
from utils import setup_metamodel, save_model
from model_factory import ModelFactory

class TestModelGenerator(unittest.TestCase):
    """Test cases for model generation."""
    
    def test_minimal_model_creation(self):
        """Test that a minimal model can be created."""
        test_xml = "test_minimal.xml"
        
        try:
            # Create minimal model
            model = create_minimal_model(test_xml)
            
            # Check that file exists
            self.assertTrue(os.path.exists(test_xml), f"Model file {test_xml} not created")
            self.assertGreater(os.path.getsize(test_xml), 0, "Model file is empty")
        finally:
            # Clean up
            if os.path.exists(test_xml):
                os.remove(test_xml)
    
    def test_model_has_expected_structure(self):
        """Test that the minimal model has the expected structure."""
        # Set up metamodel
        rset, PCM = setup_metamodel()
        
        # Create minimal model
        model = create_minimal_model()
        
        # Check model structure
        self.assertEqual(len(model.fragments), 3, "Model should have 3 fragments")
        
        # Find repository fragment
        repository = None
        for fragment in model.fragments:
            if fragment.eClass.name == "Repository" and fragment.name == "MinimalRepository":
                repository = fragment
                break
        
        # Check repository
        self.assertIsNotNone(repository, "Repository fragment not found")
        self.assertGreater(len(repository.contents), 0, "Repository should have contents")
        
        # Check for interface
        interface = None
        for content in repository.contents:
            if content.eClass.name == "DomainInterface" and content.name == "IFileStorage":
                interface = content
                break
        
        self.assertIsNotNone(interface, "Interface not found in repository")
        self.assertGreater(len(interface.contents), 0, "Interface should have operations")

def run_tests():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests()