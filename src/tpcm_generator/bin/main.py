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
        help="Max number of interfaces to generate (for random model)",
    )
    parser.add_argument(
        "--components",
        "-c",
        type=int,
        default=10,
        help="Max number of components to generate (for random model)",
    )
    parser.add_argument(
        "--containers",
        "-r",
        type=int,
        default=3,
        help="Max number of resource containers to generate (for random model)",
    )
    parser.add_argument(
        "--max-params",
        type=int,
        default=3,
        help="Max parameters per signature",
    )
    parser.add_argument(
        "--min-sigs",
        type=int,
        default=1,
        help="Min signatures per interface",
    )
    parser.add_argument(
        "--max-sigs",
        type=int,
        default=5,
        help="Max signatures per interface",
    )
    parser.add_argument(
        "--min-provided",
        type=int,
        default=1,
        help="Min provided interfaces per component",
    )
    parser.add_argument(
        "--min-required",
        type=int,
        default=1,
        help="Min required interfaces per component",
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

        import random
        # Generate a unique output name for each model if multiple models
        model_name = args.output
        if args.models > 1:
            # Import utils directly to avoid circular imports
            from tpcm_generator.utils import random_name

            model_name = f"generated_{random_name('')}"

        # For multiple models, generate random model parameters for different model shapes
        if args.models > 1:
            # Set random seed for parameter generation (different from model generation seed)
            param_seed = current_seed + 1000 if current_seed is not None else None
            param_random = random.Random(param_seed)
            
            # Generate random parameters within specified max values
            # Ensure we have at least 2 interfaces for more complex models
            num_interfaces = param_random.randint(2, args.interfaces) if args.interfaces > 1 else 1
            # Ensure at least 2 components for more interesting systems
            num_components = param_random.randint(2, args.components) if args.components > 1 else 1
            # Ensure at least 1 container
            num_containers = param_random.randint(1, args.containers)
            
            # Generate other random parameters
            max_params = param_random.randint(1, args.max_params)
            min_sigs = param_random.randint(1, args.min_sigs)
            max_sigs = param_random.randint(min_sigs, args.max_sigs)
            min_provided = param_random.randint(1, args.min_provided)
            min_required = param_random.randint(1, args.min_required)
        else:
            # Use command line parameters directly for a single model
            num_interfaces = args.interfaces
            num_components = args.components
            num_containers = args.containers
            max_params = args.max_params
            min_sigs = args.min_sigs
            max_sigs = args.max_sigs
            min_provided = args.min_provided
            min_required = args.min_required

        # Make sure the generated directory exists
        os.makedirs("generated", exist_ok=True)
        
        # Add generated directory prefix to model name and set output file
        model_name_with_dir = f"generated/{model_name}"
        output_file = f"{model_name_with_dir}.xml"
        
        # For multiple models, run each generation in a subprocess to ensure complete isolation
        if args.models > 1 and i > 0:
            import sys
            import subprocess
            
            # Build command for subprocess to generate a single model
            cmd = [
                sys.executable, 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "main.py"),
                # Use just the model name without directory prefix - subprocess will add the directory
                f"--output={model_name}",
                f"--interfaces={num_interfaces}",
                f"--components={num_components}",
                f"--containers={num_containers}",
                f"--max-params={max_params}",
                f"--min-sigs={min_sigs}",
                f"--max-sigs={max_sigs}",
                f"--min-provided={min_provided}",
                f"--min-required={min_required}"
            ]
            
            if current_seed is not None:
                cmd.append(f"--seed={current_seed}")
                
            if args.convert:
                cmd.append("--convert")
                
            # Create directories if they don't exist (in case the subprocess needs them)
            os.makedirs("generated", exist_ok=True)
            if args.convert:
                os.makedirs("input", exist_ok=True)
                
            print(
                f"Generating random model {i+1}/{args.models} with "
                f"{num_interfaces} interfaces, {num_components} components, {num_containers} containers, "
                f"{min_sigs}-{max_sigs} signatures per interface, {max_params} max params..."
            )
            
            # Run as a separate process
            result = subprocess.run(cmd, check=True)
            
            # Add a placeholder model (actual model file already created by subprocess)
            generated_models.append(None)
            continue

        # Create a fresh model generator for each model (to avoid shared state)
        print(
            f"Generating random model {i+1}/{args.models} with "
            f"{num_interfaces} interfaces, {num_components} components, {num_containers} containers, "
            f"{min_sigs}-{max_sigs} signatures per interface, {max_params} max params..."
        )
        
        # Configure model generator with all parameters
        config = {
            "max_parameters_per_signature": max_params,
            "min_signatures_per_interface": min_sigs,
            "max_signatures_per_interface": max_sigs,
            "min_provided_interfaces_per_component": min_provided,
            "min_required_interfaces_per_component": min_required
        }
        
        generator = ModelGenerator(seed=current_seed, **config)

        # Generate all model elements and create the complete model
        model, model_resource = generator.generate_complete_model(
            model_name_with_dir,  # Pass the model name with directory prefix
            num_interfaces=num_interfaces,
            num_components=num_components
        )
        generated_models.append(model)
        print(f"Random model generated and saved to {output_file}")

        # Convert to TPCM if requested
        if args.convert:
            # Make sure the input directory exists
            os.makedirs("input", exist_ok=True)
            
            # Create TPCM path with just the base model name (no directory prefix)
            tpcm_path = f"input/{model_name}.tpcm"
            print(f"Converting {output_file} to TPCM format: {tpcm_path}...")
            if convert_to_tpcm(output_file, tpcm_path):
                print(f"Model converted to TPCM format: {tpcm_path}")

    # Return the last generated model for backward compatibility
    return generated_models[-1] if generated_models else None


if __name__ == "__main__":
    main()
