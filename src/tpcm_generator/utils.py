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
    suffix = "".join(random.choices(string.ascii_uppercase, k=8))
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
    def __init__(self, data):
        self.data = data
        self.remaining = list(data)
        self.remaining_provided = list(data)

    def sample(self, count_provided, count_required):
        if count_provided + count_required > len(self.data):
            raise ValueError("2 * n cannot be greater than the size of the data set")

        if len(self.remaining_provided) < count_provided:
            self.remaining_provided = list(self.data)

        list_provided = random.sample(self.remaining_provided, count_provided)
        self.remaining_provided = list(
            set(self.remaining_provided) - set(list_provided)
        )
        self.remaining = list(set(self.remaining) - set(list_provided))

        if len(self.remaining) < count_required:
            self.remaining = list(set(self.data) - set(list_provided))

        list_required = random.sample(self.remaining, count_required)
        self.remaining = list(set(self.remaining) - set(list_required))

        return list_provided, list_required


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
