#!/usr/bin/env python3
"""Run all tests."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_model_generator import TestModelGenerator
from tests.test_conversion import TestConversion

def run_all_tests():
    """Run all test cases."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestModelGenerator))
    test_suite.addTest(unittest.makeSuite(TestConversion))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)