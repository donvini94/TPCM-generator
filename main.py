# Suppose that metamodel A.ecore has references to B.ecore as '../../B.ecore'.

# Path of A.ecore is 'a/b/A.ecore' and B.ecore is '.'

from pyecore.resources import ResourceSet, URI

rset = ResourceSet()

resource = rset.get_resource(URI("Ecore.ecore"))  # Load B.ecore first

root = resource.contents[0]

rset.metamodel_registry["Ecore.ecore"] = (
    root  # Register 'B' metamodel at 'file path' uri
)

resource = rset.get_resource(URI("pcm.ecore"))  # Load B.ecore first

root = resource.contents[0]

rset.metamodel_registry["Ecore.ecore"] = (
    root  # Register 'B' metamodel at 'file path' uri
)
resource = rset.get_resource(URI("RepoLang.ecore"))

mm_root = resource.contents[0]
from pyecore.utils import DynamicEPackage

MyMetamodel = DynamicEPackage(
    mm_root
)  # We create a DynamicEPackage for the loaded root

a_instance = MyMetamodel.Repository()

b_instance = MyMetamodel.Component()

b_instance.name = "vincenzo"

a_instance.elements += b_instance
model = rset.create_resource(URI("model.tpcm"))

model.append(a_instance)

model.save()
