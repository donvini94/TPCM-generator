from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
import string
import random
import os
import subprocess


def setup_metamodel(ecore_path="ecores/TPCM.ecore"):
    """Set up the PCM metamodel and return the resource set and PCM package.

    Args:
        ecore_path: Path to the TPCM.ecore file

    Returns:
        Tuple of (ResourceSet, DynamicEPackage)
    """
    rset = ResourceSet()
    tpcm_resource = rset.get_resource(URI(ecore_path))
    tpcm_metamodel = tpcm_resource.contents[0]
    rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel
    PCM = DynamicEPackage(tpcm_metamodel)
    return rset, PCM


def create_model(PCM):
    """Create a new empty PCM model.

    Args:
        PCM: The PCM dynamic package

    Returns:
        A new empty PCM model
    """
    return PCM.Model()


def save_model(model, filename, rset):
    """Save a model to a file.

    Args:
        model: The PCM model to save
        filename: The filename to save to
        rset: The ResourceSet to use
    """
    model_resource = rset.create_resource(URI(filename))
    model_resource.append(model)
    model_resource.save()
    return model_resource

def random_name(prefix):
        """Generate a random name with a given prefix.

        Args:
            prefix: Prefix for the name

        Returns:
            A random name string
        """
        suffix = "".join(random.choices(string.ascii_uppercase, k=5))
        return f"{prefix}_{suffix}"

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
    print(jar_path)

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
class UniqueRandomInterfaceSampler:
    """Samples interfaces for components, handling provided and required roles.

    This handles edge cases like having fewer interfaces than requested
    and ensures valid sampling even with very small numbers of interfaces.
    """
    def __init__(self, data):
        self.data = list(data)  # Create a copy to avoid modifying the original

    def sample(self, count_provided, count_required):
        """Sample interfaces for provided and required roles.

        Args:
            count_provided: Desired number of provided interfaces
            count_required: Desired number of required interfaces

        Returns:
            Tuple of (provided_interfaces, required_interfaces)
        """
        # Handle empty interfaces case
        if not self.data:
            return [], []

        # Get total available interfaces
        available = len(self.data)

        # Adjust counts if more requested than available
        count_provided = min(count_provided, available)
        count_required = min(count_required, available)

        # Special case: If we only have one interface, use it for both roles
        if available == 1:
            return self.data, self.data

        # If total requested interfaces exceeds available,
        # we need to share some interfaces between provided and required
        if count_provided + count_required > available:
            # We'll need some overlap - distribute interfaces proportionally
            total_requested = count_provided + count_required

            # Calculate how many interfaces need to be shared
            overlap_count = count_provided + count_required - available

            # First, ensure we have enough for provided interfaces
            all_interfaces = self.data.copy()
            random.shuffle(all_interfaces)

            # Split interfaces into three groups:
            # 1. Provided-only
            # 2. Shared (both provided and required)
            # 3. Required-only
            shared_count = overlap_count
            provided_only_count = count_provided - shared_count
            required_only_count = count_required - shared_count

            # Adjust if we have negative values
            if provided_only_count < 0:
                shared_count += provided_only_count
                provided_only_count = 0
            if required_only_count < 0:
                shared_count += required_only_count
                required_only_count = 0

            # Ensure we don't exceed available interfaces
            total_count = provided_only_count + shared_count + required_only_count
            if total_count > available:
                # Scale everything down proportionally
                scale_factor = available / total_count
                provided_only_count = max(0, int(provided_only_count * scale_factor))
                shared_count = max(0, int(shared_count * scale_factor))
                required_only_count = max(0, int(required_only_count * scale_factor))

                # Handle any remaining interfaces
                remaining = available - (provided_only_count + shared_count + required_only_count)
                if remaining > 0:
                    # Prioritize shared interfaces
                    shared_count += remaining

            # Create the groups
            start_idx = 0
            provided_only = all_interfaces[start_idx:start_idx + provided_only_count]
            start_idx += provided_only_count

            shared = all_interfaces[start_idx:start_idx + shared_count]
            start_idx += shared_count

            required_only = all_interfaces[start_idx:start_idx + required_only_count]

            # Create final lists
            provided_interfaces = provided_only + shared
            required_interfaces = required_only + shared

            return provided_interfaces, required_interfaces
        else:
            # If we have enough interfaces, just randomly select distinct sets
            all_interfaces = self.data.copy()
            random.shuffle(all_interfaces)

            provided_interfaces = all_interfaces[:count_provided]

            # For required interfaces, use distinct ones first then reuse if needed
            remaining = [i for i in all_interfaces if i not in provided_interfaces]

            if len(remaining) >= count_required:
                # We have enough distinct interfaces
                required_interfaces = random.sample(remaining, count_required)
            else:
                # Need to reuse some provided interfaces
                required_interfaces = remaining.copy()
                additional_needed = count_required - len(required_interfaces)
                additional = random.sample(provided_interfaces, additional_needed)
                required_interfaces.extend(additional)

            return provided_interfaces, required_interfaces


class UniqueRandomSampler:
    def __init__(self, data):
        self.data = data
        self.remaining = list(data)

    def sample(self):
        if not self.remaining:
            self.remaining = list(self.data)

        choice = random.choice(self.remaining)
        self.remaining.remove(choice)
        return choice


def add_to_dictionary(key, value, dict):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = []
        dict[key].append(value)
