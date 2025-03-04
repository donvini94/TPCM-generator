from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage

rset = ResourceSet()
resource = rset.get_resource(URI("ecores/TPCM.ecore"))
tpcm_root = resource.contents[0]

DynamicRepoLang = DynamicEPackage(tpcm_root)


# Extract and display the metamodel structure
def explore_metamodel(package):
    metamodel_structure = []
    for classifier in package.eClassifiers:
        features = []
        if hasattr(classifier, "eStructuralFeatures"):
            for feature in classifier.eStructuralFeatures:
                feature_info = {
                    "name": feature.name,
                    "type": type(feature).__name__,
                    "eType": feature.eType.name if feature.eType else None,
                }
                features.append(feature_info)
        metamodel_structure.append({"class": classifier.name, "features": features})
    return metamodel_structure


# Traverse and print the metamodel structure
metamodel_structure = explore_metamodel(tpcm_root)
for cls in metamodel_structure:
    print(f"Class: {cls['class']}")
    for feature in cls["features"]:
        print(
            f"  - Feature: {feature['name']}, Type: {feature['type']}, EType: {feature['eType']}"
        )
    print()
