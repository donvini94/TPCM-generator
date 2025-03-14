#!/usr/bin/env python3
"""Main entry point for TPCM model generation."""

import argparse
import subprocess
import os

# Import from our modules
from tpcm_generator.model_generator import ModelGenerator


def convert_to_tpcm(xml_path, tpcm_path):
    """Convert XML model to TPCM format.

    Args:
        xml_path: Path to the XML model file
        tpcm_path: Path to write the TPCM file

    Returns:
        True if conversion was successful, False otherwise
    """
    # Get the directory where the script is located
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    jar_path = os.path.join(base_dir, "SaveAs.jar")

    try:
        result = subprocess.run(
            ["java", "-jar", jar_path, xml_path, tpcm_path],
            check=True,
            capture_output=True,
            text=True,
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
        "--output",
        "-o",
        default="generated",
        help="Base name for output files (without extension)",
    )
    parser.add_argument(
        "--seed", "-s", type=int, help="Random seed for reproducible generation"
    )
    parser.add_argument(
        "--interfaces",
        "-i",
        type=int,
        default=5,
        help="Number of interfaces to generate (for random model)",
    )
    parser.add_argument(
        "--components",
        "-c",
        type=int,
        default=10,
        help="Number of components to generate (for random model)",
    )
    parser.add_argument(
        "--containers",
        "-r",
        type=int,
        default=3,
        help="Number of resource containers to generate (for random model)",
    )
    parser.add_argument(
        "--convert", "-t", action="store_true", help="Convert the output to TPCM format"
    )
    parser.add_argument(
        "--models", "-m", type=int, default=1, help="Number of models to generate"
    )

    args = parser.parse_args()

    # Keep track of generated models
    generated_models = []

    # Generate the specified number of models
    for i in range(args.models):
        # Use a new seed for each model if a seed is specified
        current_seed = args.seed + i if args.seed is not None else None

        # Generate a unique output name for each model if multiple models
        model_name = args.output
        if args.models > 1:
            # Import utils directly to avoid circular imports
            from tpcm_generator.utils import random_name

            model_name = f"generated_{random_name('')}"

        output_file = f"{model_name}.xml"
        
        # For multiple models, run each generation in a subprocess to ensure complete isolation
        if args.models > 1 and i > 0:
            import sys
            import subprocess
            
            # Build command for subprocess to generate a single model
            cmd = [
                sys.executable, 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "main.py"),
                f"--output={model_name}",
                f"--interfaces={args.interfaces}",
                f"--components={args.components}",
                f"--containers={args.containers}"
            ]
            
            if current_seed is not None:
                cmd.append(f"--seed={current_seed}")
                
            if args.convert:
                cmd.append("--convert")
                
            print(
                f"Generating random model {i+1}/{args.models} with {args.interfaces} interfaces, "
                f"{args.components} components, {args.containers} containers..."
            )
            
            # Run as a separate process
            result = subprocess.run(cmd, check=True)
            
            # Add a placeholder model (actual model file already created by subprocess)
            generated_models.append(None)
            continue

        # Create a fresh model generator for each model (to avoid shared state)
        print(
            f"Generating random model {i+1}/{args.models} with {args.interfaces} interfaces, "
            f"{args.components} components, {args.containers} containers..."
        )
        generator = ModelGenerator(seed=current_seed)

        # Generate all model elements and create the complete model
        model, model_resource = generator.generate_complete_model(model_name)
        generated_models.append(model)
        print(f"Random model generated and saved to {output_file}")

        # Convert to TPCM if requested
        if args.convert:
            tpcm_path = f"input/{model_name}.tpcm"
            print(f"Converting to TPCM format: {tpcm_path}...")
            if convert_to_tpcm(output_file, tpcm_path):
                print(f"Model converted to TPCM format: {tpcm_path}")

    # Return the last generated model for backward compatibility
    return generated_models[-1] if generated_models else None


if __name__ == "__main__":
    main()
