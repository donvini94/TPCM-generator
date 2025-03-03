# TPCM Generator

A Python tool for generating random Palladio Component Models (PCM) using text-based model generation.

## Project Overview

This tool generates datasets of random text-based Palladio component models (TPCM) and converts them to complete PCM models using the [Palladio-Addons-TextBasedModelGenerator](https://github.com/PalladioSimulator/Palladio-Addons-TextBasedModelGenerator).

The generator creates EMF models programmatically, transforms them to TPCM format, and then to full PCM models.

## Requirements

- Python 3.8+
- PyEcore
- textx
- Java Runtime Environment (for model conversion)
- Nix (optional but recommended for dependency management)

## Project Structure

```
TPCM_generator/
├── main.py                # Main entry point (wrapper)
├── src/                   # Source code package
│   └── tpcm_generator/    # Main package
│       ├── __init__.py    # Package initialization
│       ├── model_factory.py # Factory for creating model elements
│       ├── expression_factory.py # Factory for creating expressions
│       ├── model_generator.py # Random model generation logic
│       ├── utils.py       # Model creation and persistence utilities
│       ├── std_definitions.py # Standard component definitions
│       ├── resource_environment.py # Resource environment definitions
│       └── bin/           # Command-line scripts
│           └── main.py    # Main CLI implementation
├── tests/                 # Test files
│   ├── run_tests.py       # Test runner
│   ├── test_model_factory.py
│   ├── test_model_generator.py
│   └── test_conversion.py
└── ecores/                # Ecore metamodel definitions
    ├── TPCM.ecore         # Primary TPCM metamodel
    ├── stoex.ecore        # Stochastic expressions metamodel
    └── ...                # Other supporting metamodels
```

## Installation

### Using Nix (recommended)

The project includes a `flake.nix` file for reproducible development environments:

```bash
# Enter the development environment
nix develop

# Run Python scripts within the environment
nix develop -c python your_script.py
```

For running scripts directly:

```bash
# Run script in the nix environment
nix develop -c python main.py --output my_model --convert
```

### Manual Installation

First, install the package and dependencies:

```bash
# Install in development mode with Poetry
poetry install

# Or install with pip
pip install -e .
```

Alternatively, just install the dependencies:

```bash
# Install dependencies
pip install pyecore>=0.15.2 textx>=4.1.0
```

## Usage

### Running with Nix

Use the Nix environment to run the Python scripts:

```bash
# Generate a random model
nix develop -c python main.py --output model_name --components 10 --interfaces 5 --containers 3 --convert

# Run the tests
nix develop -c python tests/run_tests.py
```

### Running Manually

If you've installed the package with Poetry:

```bash
# Using the installed command
tpcm-generator --minimal --convert

# Generate a random model
tpcm-generator --output model_name --components 10 --interfaces 5 --containers 3 --convert
```

Or run directly with Python:

```bash
# Generate a minimal working model
python main.py --minimal --convert

# Generate a random model
python main.py --output model_name --components 10 --interfaces 5 --containers 3 --convert

# Run the tests
python -m tests.run_tests
```

### Main Generator Parameters

- `--output`, `-o`: Base name for output files (without extension)
- `--seed`, `-s`: Random seed for reproducible generation
- `--interfaces`, `-i`: Number of interfaces to generate (default: 5)
- `--components`, `-c`: Number of components to generate (default: 10)
- `--containers`, `-r`: Number of resource containers to generate (default: 3)
- `--convert`, `-t`: Convert the output to TPCM format

## Converting Models

The generator creates models in XML format first, then optionally converts them to TPCM format:

```bash
java -jar SaveAs.jar model.xml model.tpcm
```

## Implementation Details

- Uses PyEcore for EMF model creation and manipulation
- Factory pattern for creating model elements and expressions
- Random generation with configurable parameters
- Full model generation including:
  - Repository with components and interfaces
  - System with assembly contexts and connectors
  - Resource environment with containers and linking resources
  - Allocation of components to resource containers
  - Usage model with workload and system calls

## Development Status

This project provides a complete framework for generating random TPCM models. Contributions and feature extensions are welcome.
