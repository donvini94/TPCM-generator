#!/usr/bin/env python3
"""Main entry point for TPCM model generation."""

import sys
import os
import argparse
import subprocess

# Add project root to path if necessary
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our modules
from model_generator import ModelGenerator, create_minimal_model


def convert_to_tpcm(xml_path, tpcm_path):
    """Convert XML model to TPCM format.
    
    Args:
        xml_path: Path to the XML model file
        tpcm_path: Path to write the TPCM file
        
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        result = subprocess.run(
            ["java", "-jar", "SaveAs.jar", xml_path, tpcm_path],
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(f"Conversion output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting to TPCM: {e}")
        if e.stdout:
            print(f"Converter output: {e.stdout}")
        if e.stderr:
            print(f"Converter error: {e.stderr}")
        return False


def main():
    """Main entry point for the PCM model generation."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate PCM models")
    parser.add_argument(
        "--output", "-o", 
        default="generated",
        help="Base name for output files (without extension)"
    )
    parser.add_argument(
        "--seed", "-s", 
        type=int, 
        help="Random seed for reproducible generation"
    )
    parser.add_argument(
        "--interfaces", "-i", 
        type=int, 
        default=5,
        help="Number of interfaces to generate (for random model)"
    )
    parser.add_argument(
        "--components", "-c", 
        type=int, 
        default=10,
        help="Number of components to generate (for random model)"
    )
    parser.add_argument(
        "--containers", "-r", 
        type=int, 
        default=3,
        help="Number of resource containers to generate (for random model)"
    )
    parser.add_argument(
        "--convert", "-t", 
        action="store_true",
        help="Convert the output to TPCM format"
    )
    parser.add_argument(
        "--minimal", "-m",
        action="store_true",
        help="Generate a minimal working model instead of a random one"
    )
    
    args = parser.parse_args()
    
    output_file = f"{args.output}.xml"
    
    # Choose between minimal and random model generation
    if args.minimal:
        print("Generating minimal working model...")
        model = create_minimal_model(output_file)
        print(f"Minimal model generated and saved to {output_file}")
    else:
        # Create model generator for random generation
        print(f"Generating random model with {args.interfaces} interfaces, {args.components} components, {args.containers} containers...")
        generator = ModelGenerator(seed=args.seed)
        
        # Generate all model elements and create the complete model
        model, model_resource = generator.generate_complete_model(args.output)
        print(f"Random model generated and saved to {output_file}")
    
    # Convert to TPCM if requested
    if args.convert:
        tpcm_path = f"{args.output}.tpcm"
        print(f"Converting to TPCM format: {tpcm_path}...")
        if convert_to_tpcm(output_file, tpcm_path):
            print(f"Model converted to TPCM format: {tpcm_path}")
    
    return model


if __name__ == "__main__":
    main()
