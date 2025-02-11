from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage

rset = ResourceSet()
tpcm_resource = rset.get_resource(URI("ecores/TPCM.ecore"))
tpcm_metamodel = tpcm_resource.contents[0]
rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel


PCM = DynamicEPackage(tpcm_metamodel)


def add_std_definitions(model):
    int_type = PCM.PrimitiveDatatype(name="Integer", type=PCM.PrimitiveTypeEnum.INT)
    double_type = PCM.PrimitiveDatatype(
        name="Double", type=PCM.PrimitiveTypeEnum.DOUBLE
    )
    primitive_type_repository = PCM.Repository(
        name="PrimitiveTypes", contents=[int_type, double_type]
    )
    model.fragments.append(primitive_type_repository)


repository = PCM.Repository(name="MediaStore")


# int_collection = PCM.CollectionDatatype()
# int_collection.name = "IntCollection"
# int_collection.collectionType = type_1
# repository.contents += int_collection

# composed_data = PCM.ComposedDatatype()
# composed_data.name = "AudioCollectionRequest"
# composed_data.elements += PCM.ComposedDatatypeElement(name="Count", reference=type_1)
# repository.contents.append(composed_data)

model = PCM.Model()

add_std_definitions(model)
model.fragments += repository

model_resource = rset.create_resource(URI("model.xml"))
model_resource.append(model)
model_resource.save()

print("Model saved to model.xml")
