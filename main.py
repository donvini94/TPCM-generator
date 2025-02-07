from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage

rset = ResourceSet()


tpcm_resource = rset.get_resource(URI("ecores/TPCM.ecore"))
tpcm_metamodel = tpcm_resource.contents[0]
rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel

# pcm_resource = rset.get_resource(URI("ecores/pcm.ecore"))
# pcm_metamodel = pcm_resource.contents[0]
# rset.metamodel_registry[pcm_metamodel.nsURI] = pcm_metamodel
#
# ecore_resource = rset.get_resource(URI("ecores/Ecore.ecore"))
# ecore_metamodel = ecore_resource.contents[0]
# rset.metamodel_registry[ecore_metamodel.nsURI] = ecore_metamodel


PCM = DynamicEPackage(tpcm_metamodel)

# model has fragments and imports
model_instance = PCM.Model()

std_definitions = PCM.Import()
std_definitions.importURI = "std_definitions.tpcm"
model_instance.imports += std_definitions

resource_environment = PCM.Import()
resource_environment.importURI = "ResourceEnvironment.tpcm"
model_instance.imports += resource_environment

repository_instance = PCM.Repository()
repository_instance.name = "MediaStore"


datatype_instance = PCM.ComposedDatatype()
datatype_instance.name = "FileContent"
repository_instance.contents += datatype_instance


component_instance = PCM.Component()
component_instance.name = "C1"
repository_instance.contents += component_instance


model_instance.fragments += repository_instance

model_resource = rset.create_resource(URI("model.xml"))
model_resource.append(model_instance)
model_resource.save()

print("Model saved to model.xml")
