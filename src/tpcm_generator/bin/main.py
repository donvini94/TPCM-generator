#!/usr/bin/env python3
"""Main entry point for TPCM model generation."""

import argparse
import os
import random
import sys
import multiprocessing
from multiprocessing import Process, Lock, Queue

# Import from our modules
from tpcm_generator.model_generator import ModelGenerator
from tpcm_generator.utils import convert_to_tpcm, random_name


# Global lock for process-safe printing
print_lock = Lock()


def generate_model_process(model_index, total_models, args_dict, model_name=None):
    """Process function to generate a single model.
    
    Args:
        model_index: Index of the model to generate (0-based)
        total_models: Total number of models to generate
        args_dict: Dictionary with command line arguments
        model_name: Optional model name, if None a random name will be generated
    """
    try:
        # Use a new seed for each model if a seed is specified
        current_seed = args_dict.get('seed') + model_index if args_dict.get('seed') is not None else None

        # Generate a unique output name for each model
        if model_name is None:
            model_name = f"generated_{random_name('')}"

        # Generate random model parameters for different model shapes
        param_seed = current_seed + 1000 if current_seed is not None else None
        param_random = random.Random(param_seed)

        # Generate random parameters within specified max values
        # Ensure we have at least 2 interfaces for more complex models
        num_interfaces = (
            param_random.randint(5, args_dict.get('interfaces', 5)) 
            if args_dict.get('interfaces', 5) > 1 else 1
        )
        # Ensure at least 2 components for more interesting systems
        num_components = (
            param_random.randint(2, args_dict.get('components', 10)) 
            if args_dict.get('components', 10) > 1 else 1
        )
        # Ensure at least 1 container
        num_containers = param_random.randint(1, args_dict.get('containers', 3))

        # Generate other random parameters
        max_params = param_random.randint(1, args_dict.get('max_params', 3))
        min_sigs = param_random.randint(1, args_dict.get('min_sigs', 1))
        max_sigs = param_random.randint(min_sigs, args_dict.get('max_sigs', 5))
        min_provided = param_random.randint(1, args_dict.get('min_provided', 1))
        min_required = param_random.randint(1, args_dict.get('min_required', 1))

        # Make sure the generated directory exists
        os.makedirs("generated", exist_ok=True)

        # Add generated directory prefix to model name and set output file
        model_name_with_dir = f"generated/{model_name}"
        output_file = f"{model_name_with_dir}.xml"

        # Print process-safe using a lock
        with print_lock:
            print(
                f"Generating random model {model_index+1}/{total_models} with "
                f"{num_interfaces} interfaces, {num_components} components, {num_containers} containers, "
                f"{min_sigs}-{max_sigs} signatures per interface, {max_params} max params..."
            )

        # Configure model generator with all parameters
        config = {
            "max_parameters_per_signature": max_params,
            "min_signatures_per_interface": min_sigs,
            "max_signatures_per_interface": max_sigs,
            "min_provided_interfaces_per_component": min_provided,
            "min_required_interfaces_per_component": min_required,
        }

        # Create a fresh model generator instance in each process
        generator = ModelGenerator(seed=current_seed, **config)

        # Generate all model elements and create the complete model
        model, model_resource = generator.generate_complete_model(
            model_name_with_dir,  # Pass the model name with directory prefix
            num_interfaces=num_interfaces,
            num_components=num_components,
        )
        
        with print_lock:
            print(f"Random model generated and saved to {output_file}")

        # Convert to TPCM if requested
        if args_dict.get('convert', False):
            # Make sure the input directory exists
            os.makedirs("input", exist_ok=True)

            # Create TPCM path with just the base model name (no directory prefix)
            tpcm_path = f"input/{model_name}.tpcm"
            with print_lock:
                print(f"Converting {output_file} to TPCM format: {tpcm_path}...")
            
            # Try to load the metadata file
            import json
            metadata_path = os.path.splitext(output_file)[0] + ".metadata"
            
            try:
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        
                    # Update metadata with TPCM conversion info
                    import time
                    conversion_start = time.time()
                    conversion_success = convert_to_tpcm(output_file, tpcm_path)
                    conversion_time = round(time.time() - conversion_start, 3)
                    
                    metadata["tpcm_conversion"] = {
                        "success": conversion_success,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "time_seconds": conversion_time,
                        "xml_path": output_file,
                        "tpcm_path": tpcm_path
                    }
                    
                    # Save updated metadata
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                        
                    if conversion_success:
                        # Also copy metadata to the input directory alongside the TPCM file
                        tpcm_metadata_path = os.path.splitext(tpcm_path)[0] + ".metadata"
                        with open(tpcm_metadata_path, 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        with print_lock:
                            print(f"Model converted to TPCM format: {tpcm_path}")
                            print(f"Metadata saved to: {tpcm_metadata_path}")
                else:
                    # If metadata file doesn't exist, just do the conversion
                    if convert_to_tpcm(output_file, tpcm_path):
                        with print_lock:
                            print(f"Model converted to TPCM format: {tpcm_path}")
            except Exception as e:
                # If there's an error handling metadata, still try the conversion
                with print_lock:
                    print(f"Warning: Error handling metadata: {e}")
                if convert_to_tpcm(output_file, tpcm_path):
                    with print_lock:
                        print(f"Model converted to TPCM format: {tpcm_path}")

        return True
    except Exception as e:
        with print_lock:
            print(f"Error generating model {model_index}: {e}")
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
    parser.add_argument(
        "--processes", "-p", 
        type=int, 
        default=multiprocessing.cpu_count(),
        help="Number of processes to use (default: number of CPU cores)"
    )

    args = parser.parse_args()

    # Create output directories
    os.makedirs("generated", exist_ok=True)
    if args.convert:
        os.makedirs("input", exist_ok=True)

    # Handle single model case without multiprocessing overhead
    if args.models == 1:
        model_name = args.output
        result = generate_model_process(0, 1, vars(args), model_name)
        return True if result else None
    else:
        # Convert args to dictionary for easy passing to processes
        args_dict = vars(args)
        
        # Determine number of processes to use (min of processes, models, and cpu_count)
        num_processes = min(args.processes, args.models, multiprocessing.cpu_count())
        
        print(f"Generating {args.models} models using {num_processes} processes")
        
        # Create a process pool
        processes = []
        
        for i in range(args.models):
            # Create and start a new process for each model
            p = Process(target=generate_model_process, args=(i, args.models, args_dict))
            p.start()
            processes.append(p)
            
            # Wait for processes to complete before starting new ones if we've reached max
            if len(processes) >= num_processes:
                for p in processes:
                    p.join()
                # Clear the completed processes
                processes = []
        
        # Wait for any remaining processes to complete
        for p in processes:
            p.join()
            
        print(f"Successfully generated {args.models} models")
        return True


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')  # This helps with PyEcore compatibility
    main()
