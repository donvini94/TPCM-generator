# PCM-Generator

A Python tool for generating random Palladio Component Models (PCM) using text-based model generation.

## Project Overview

This tool generates datasets of random text-based Palladio component models (TPCM) and converts them to complete PCM models using the [Palladio-Addons-TextBasedModelGenerator](https://github.com/PalladioSimulator/Palladio-Addons-TextBasedModelGenerator).

The generator creates EMF models programmatically, transforms them to TPCM format, and then to full PCM models.

## Requirements

- Python 3.8+
- PyEcore
- Palladio-Addons-TextBasedModelGenerator

## Project Structure

```
PCM-Generator/
├── main.py           # Entry point for model generation
├── generator.py      # Core model generation logic
├── util.py           # Model creation and persistence utilities
├── std_definitions.py # Standard component definitions (singleton)
└── resource_environment.py # Resource environment definitions (singleton)
```

## Usage

Run the generation process using `main.py` with appropriate parameters:

```bash
python main.py --num-models 10 --min-components 3 --max-components 10 --min-interfaces 2 --max-interfaces 8
```

### Parameters

- `--num-models`: Number of random models to generate
- `--min-components`: Minimum number of components per model
- `--max-components`: Maximum number of components per model
- `--min-interfaces`: Minimum number of interfaces per model
- `--max-interfaces`: Maximum number of interfaces per model

## Implementation Details

- Uses PyEcore for EMF model creation and manipulation
- Implements singleton pattern for standard definitions and resource environments
- Generates models with randomized structure while maintaining valid PCM constraints
- Leverages Palladio-Addons-TextBasedModelGenerator for model transformation

## Development Status

This project is currently under development. Core functionality is implemented but additional features and optimizations are planned.
