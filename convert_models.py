#!/usr/bin/env python3
"""Utility script to convert multiple XML models to TPCM format in parallel."""

import os
import sys
import argparse
import glob
from src.tpcm_generator.utils import convert_multiple_to_tpcm


def main():
    """Main entry point for the XML to TPCM converter."""
    parser = argparse.ArgumentParser(description="Convert multiple XML models to TPCM format in parallel")
    parser.add_argument(
        "--input-dir", 
        "-i", 
        default="generated", 
        help="Directory containing XML model files"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="input",
        help="Directory to write TPCM files to"
    )
    parser.add_argument(
        "--pattern",
        "-p",
        default="*.xml",
        help="File pattern to match (default: *.xml)"
    )
    parser.add_argument(
        "--processes",
        "-j",
        type=int,
        default=None,
        help="Number of processes to use (default: CPU count)"
    )
    parser.add_argument(
        "--remove-existing",
        "-r", 
        action="store_true",
        help="Remove existing TPCM files in output directory"
    )
    
    args = parser.parse_args()
    
    # Make sure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all XML files in the input directory
    pattern = os.path.join(args.input_dir, args.pattern)
    xml_files = glob.glob(pattern)
    
    if not xml_files:
        print(f"No XML files found matching pattern {pattern}")
        return 1
    
    print(f"Found {len(xml_files)} XML files")
    
    # Remove existing TPCM files if requested
    if args.remove_existing:
        removed = 0
        for xml_path in xml_files:
            base_name = os.path.basename(os.path.splitext(xml_path)[0])
            tpcm_path = os.path.join(args.output_dir, f"{base_name}.tpcm")
            if os.path.exists(tpcm_path):
                os.remove(tpcm_path)
                removed += 1
        if removed > 0:
            print(f"Removed {removed} existing TPCM files")
    
    # Create conversion tuples
    conversion_paths = []
    for xml_path in xml_files:
        base_name = os.path.basename(os.path.splitext(xml_path)[0])
        tpcm_path = os.path.join(args.output_dir, f"{base_name}.tpcm")
        conversion_paths.append((xml_path, tpcm_path))
    
    # Run the conversion
    results = convert_multiple_to_tpcm(conversion_paths, args.processes)
    
    # Print summary
    successful = sum(1 for r in results.values() if r["success"])
    if successful == len(xml_files):
        print(f"All {successful} files converted successfully")
        return 0
    else:
        print(f"Converted {successful} out of {len(xml_files)} files successfully")
        return 1


if __name__ == "__main__":
    sys.exit(main())