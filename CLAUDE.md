# CLAUDE.md - Project Guidelines

## Build Commands
```bash
# Install dependencies
poetry install

# Run the generator
python main.py

# Update dependencies
poetry update
```

## Project Structure
- `ecores/` - Metamodel definitions (Ecore files)
- `input/` - Input files for generation
- `output/` - Generated models

## Code Style
- Use Google-style docstrings with Args/Returns sections
- 4-space indentation
- ~88 character line length
- Snake_case for variables/functions, CamelCase for classes
- Import order: stdlib -> third-party -> local
- Return type annotations encouraged

## Error Handling
- Use descriptive error messages
- Validate inputs at function boundaries
- Prefer early returns over deep nesting

## Development
This project uses PyEcore to work with Ecore metamodels and generate models based on them. Models are exported as XML files that can be used in other tools.