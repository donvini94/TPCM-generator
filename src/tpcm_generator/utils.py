from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage


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
