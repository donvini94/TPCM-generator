import sys
import os

# Add project root to path if necessary
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our modules
from utils import setup_metamodel, create_model, save_model
from std_definitions import get_std_definitions
from resource_environment import get_resource_environment


def main():
    """Main entry point for the PCM model generation."""
    # Set up metamodel and create a new model
    rset, PCM = setup_metamodel()
    model = create_model(PCM)

    # Add standard definitions to the model
    std_defs = get_std_definitions(rset)
    std_defs.add_to_model(model)

    # Add resource environment
    resource_env = get_resource_environment(rset)
    resource_env.add_to_model(model)

    # TODO: Add code to call model generation functions
    # This would import and use functions from generator.py

    # Save the model
    save_model(model, "generated_model.xml", rset)

    print("Model generated successfully!")


if __name__ == "__main__":
    main()
