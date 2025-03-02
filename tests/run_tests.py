#!/usr/bin/env python3
"""Run all tests."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all test cases."""
    # Discover all tests in the tests directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_suite = unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)