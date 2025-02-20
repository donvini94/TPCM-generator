import random
import string
import os

from utils import setup_metamodel, create_model, save_model
from std_definitions import get_std_definitions
from resource_environment import get_resource_environment


class PCMModelGenerator:
    """Generator for random PCM models."""

    def __init__(self, ecore_path="ecores/TPCM.ecore"):
        """Initialize the generator with metamodel."""
        self.rset, self.PCM = setup_metamodel(ecore_path)
        self.std_defs = get_std_definitions(self.rset)
        self.resource_env = get_resource_environment(self.rset)

    def generate_random_name(self, prefix="", length=5):
        """Generate a random name with optional prefix."""
        random_part = "".join(
            random.choice(string.ascii_letters) for _ in range(length)
        )
        return f"{prefix}{random_part}"

    def generate_model(self, num_components=None, num_interfaces=None):
        """Generate a random model with specified complexity.

        Args:
            num_components: Number or range of components to generate
            num_interfaces: Number or range of interfaces to generate

        Returns:
            A generated PCM model with standard definitions
        """
        # Create new empty model
        model = create_model(self.PCM)

        # Add standard definitions
        self.std_defs.add_to_model(model)

        # Add resource environment
        self.resource_env.add_to_model(model)

        # TODO: Implement random model generation logic
        # This would use the standard elements from std_defs.get_element()
        # and generate random components, interfaces, etc.

        return model

    def save_model(self, model, filename):
        """Save a model to a file.

        Args:
            model: The PCM model to save
            filename: The filename to save to
        """
        save_model(model, filename, self.rset)

    def generate_and_save_models(
        self,
        num_models,
        output_dir="generated_models",
        num_components=(2, 10),
        num_interfaces=(2, 5),
    ):
        """Generate multiple models and save them.

        Args:
            num_models: Number of models to generate
            output_dir: Directory to save models in
            num_components: Number or range of components per model
            num_interfaces: Number or range of interfaces per model

        Returns:
            List of generated model filenames
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        filenames = []
        for i in range(num_models):
            model = self.generate_model(num_components, num_interfaces)
            filename = f"{output_dir}/model_{i+1}.xml"
            self.save_model(model, filename)
            filenames.append(filename)

        return filenames


# Example usage:
def generate_example_model():
    """Example function showing how to use the generator."""
    generator = PCMModelGenerator()
    model = generator.generate_model(num_components=(3, 7), num_interfaces=(2, 5))
    generator.save_model(model, "example_generated_model.xml")
    return model
