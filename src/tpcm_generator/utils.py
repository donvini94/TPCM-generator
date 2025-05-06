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


def convert_to_tpcm_worker(args):
    """Worker function for parallel TPCM conversion.
    
    Args:
        args: Tuple of (xml_path, tpcm_path)
        
    Returns:
        Tuple of (xml_path, tpcm_path, success, error_message)
    """
    xml_path, tpcm_path = args
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
        return (xml_path, tpcm_path, True, result.stdout.strip())
    except subprocess.CalledProcessError as e:
        error_msg = f"Error: {str(e)}"
        if e.stdout:
            error_msg += f" Output: {e.stdout}"
        if e.stderr:
            error_msg += f" Error: {e.stderr}"
        return (xml_path, tpcm_path, False, error_msg)


def convert_multiple_to_tpcm(file_paths, num_processes=None):
    """Convert multiple XML models to TPCM format in parallel.
    
    Args:
        file_paths: List of tuples, each containing (xml_path, tpcm_path)
        num_processes: Number of parallel processes to use (default: CPU count)
        
    Returns:
        Dictionary with results for each conversion
    """
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    import time
    
    start_time = time.time()
    
    # Set number of processes
    if num_processes is None:
        num_processes = min(multiprocessing.cpu_count(), len(file_paths))
    else:
        num_processes = min(num_processes, multiprocessing.cpu_count(), len(file_paths))
    
    print(f"Converting {len(file_paths)} files using {num_processes} processes")
    
    results = {}
    
    # Create paths for input directory
    input_dir = os.path.dirname(file_paths[0][1]) if file_paths else "input"
    os.makedirs(input_dir, exist_ok=True)
    
    # Process files in parallel using ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        for xml_path, tpcm_path, success, message in executor.map(convert_to_tpcm_worker, file_paths):
            results[xml_path] = {
                "tpcm_path": tpcm_path,
                "success": success,
                "message": message,
            }
            if success:
                print(f"Converted {xml_path} to {tpcm_path}")
            else:
                print(f"Failed to convert {xml_path}: {message}")
    
    total_time = time.time() - start_time
    print(f"Total conversion time: {total_time:.2f} seconds")
    
    # Process metadata if available
    metadata_updates = []
    for xml_path, result in results.items():
        metadata_path = os.path.splitext(xml_path)[0] + ".metadata"
        if os.path.exists(metadata_path):
            try:
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Update metadata with conversion info
                metadata["tpcm_conversion"] = {
                    "success": result["success"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "xml_path": xml_path,
                    "tpcm_path": result["tpcm_path"]
                }
                
                # Save updated metadata
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Also copy metadata to the input directory alongside the TPCM file
                if result["success"]:
                    tpcm_metadata_path = os.path.splitext(result["tpcm_path"])[0] + ".metadata"
                    with open(tpcm_metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                
                metadata_updates.append((metadata_path, result["success"]))
            except Exception as e:
                print(f"Error updating metadata for {xml_path}: {e}")
    
    # Summary stats
    successful = sum(1 for r in results.values() if r["success"])
    print(f"Successfully converted {successful} out of {len(file_paths)} files")
    print(f"Updated {len(metadata_updates)} metadata files")
    
    return results


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
