# CLAUDE.md - TPCM Generator Project Guidelines

## Build Commands
```bash
# setup nix environment
nix develop
# Install dependencies
poetry install

# Run the generator 
python main.py

# Run all tests
python tests/run_tests.py

# Run a single test
python -m unittest tests.test_model_factory.test_create_minimal_repository

```

## Project Structure
- `ecores/` - Metamodel definitions (Ecore files)
- `input/` - Input files for generation
- `output/` - Generated models
- `tests/` - Unit tests

## Code Style
- Use Google-style docstrings with Args/Returns sections
- 4-space indentation, ~88 character line length
- Snake_case for variables/functions, CamelCase for classes
- Type annotations for function parameters and returns
- Import order: stdlib → third-party (pyecore, etc.) → local
- Class methods that create objects should return the created object

## Error Handling
- Use descriptive error messages
- Validate inputs at function boundaries
- Prefer early returns over deep nesting
- Use assertions for internal logic verification

## Development
This project uses PyEcore to work with Ecore metamodels and generate models based on them. Models are exported as XML files that can be used with Palladio Component Model tooling.


## Important information:
- SaveAs.jar is fixed and correct. It is used to convert xml models to .tpcm files. It does not need to be changed. If a correct .xml is provided, the model will be converted correctly. Otherwise the input model is wrong. 
- The .ecore metamodel files are fixed and unchangeable. 
- Do not try to setup virtual environments or install dependencies with pip. If you have dependency issues, remember to use nix develop to drop into a dev shell with the installed dependencies. 
