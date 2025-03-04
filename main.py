#!/usr/bin/env python3
"""Main entry point for TPCM model generation."""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from tpcm_generator.bin.main import main

if __name__ == "__main__":
    main()