from pyecore.ecore import EObject
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
import pyecore.ecore as ecore

rset = ResourceSet()
tpcm_resource = rset.get_resource(URI("ecores/TPCM.ecore"))
tpcm_metamodel = tpcm_resource.contents[0]
rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel
# rset.metamodel_registry["Ecore.ecore"] = ecore.eClass
PCM = DynamicEPackage(tpcm_metamodel)


def create_primitives():
    # Create primitive types repository
    primitive_types = PCM.Repository(name="PrimitiveTypes")

    # Create primitive datatypes
    int_type = PCM.PrimitiveDatatype(name="Integer", type=PCM.PrimitiveTypeEnum.INT)
    double_type = PCM.PrimitiveDatatype(
        name="Double", type=PCM.PrimitiveTypeEnum.DOUBLE
    )

    # Create failure type
    cpu_failure = PCM.FailureType(name="CPUFailure")

    primitive_types.contents.extend([int_type, double_type])
    primitive_types.contents.append(cpu_failure)
    return primitive_types


def create_std_definitions(primitive_types):
    int_type = primitive_types.contents[0]
    double_type = primitive_types.contents[1]
    cpu_failure = primitive_types.contents[2]

    # Create resource types repository
    resource_types = PCM.ResourceTypeRepository()

    # Create interfaces
    icpu = PCM.ResourceInterface(name="ICPU")
    ihdd = PCM.ResourceInterface(name="IHDD")

    # Create ICPU process operation
    process_op = PCM.OperationSignature(name="process")
    amount_param = PCM.Parameter(name="amount", type=double_type)
    process_op.parameters.append(amount_param)
    icpu.contents.append(process_op)

    # Create IHDD operations
    read_op = PCM.OperationSignature(name="read")
    read_param = PCM.Parameter(name="amount", type=double_type)
    read_op.parameters.append(read_param)

    write_op = PCM.OperationSignature(name="write")
    write_param = PCM.Parameter(name="amount", type=double_type)
    write_op.parameters.append(write_param)

    ihdd.contents.extend([read_op, write_op])

    # Add interfaces to resource types
    resource_types.contents.extend([icpu, ihdd])

    # Create scheduling policy type and entities
    scheduling_policy_type = PCM.ResourceEntityType(name="SchedulingPolicy")
    fcfs_entity = PCM.ResourceEntity(
        name="FirstComeFirstServe", type=scheduling_policy_type
    )
    ps_entity = PCM.ResourceEntity(name="ProcessorSharing", type=scheduling_policy_type)
    delay_entity = PCM.ResourceEntity(name="Delay", type=scheduling_policy_type)

    resource_types.contents.extend(
        [scheduling_policy_type, fcfs_entity, ps_entity, delay_entity]
    )

    # Create resource types
    cpu_resource = PCM.ProcessingResourceType(name="CPUResource")
    cpu_provided_role = PCM.ResourceInterfaceProvidedRole()
    cpu_provided_role.type = icpu
    cpu_resource.contents.append(cpu_provided_role)

    # Add failure specification to CPU
    cpu_failure_spec = PCM.ResourceFailureSpecification()
    cpu_failure_spec.failureType = cpu_failure
    cpu_resource.contents.append(cpu_failure_spec)

    # Add properties to CPU
    processing_rate_def = PCM.PropertyDefinition(name="processingRate")
    processing_rate_def.type = double_type
    scheduling_policy_def = PCM.PropertyDefinition(name="schedulingPolicy")
    scheduling_policy_def.type = scheduling_policy_type
    cpu_resource.definitions.extend([processing_rate_def, scheduling_policy_def])

    # Create HDD resource type
    hdd_resource = PCM.ProcessingResourceType(name="HDDResource")
    hdd_provided_role = PCM.ResourceInterfaceProvidedRole()
    hdd_provided_role.type = ihdd
    hdd_resource.contents.append(hdd_provided_role)

    # Add properties to HDD
    hdd_processing_rate = PCM.PropertyDefinition(name="processingRate")
    hdd_processing_rate.type = double_type
    hdd_scheduling_policy = PCM.PropertyDefinition(name="schedulingPolicy")
    hdd_scheduling_policy.type = scheduling_policy_type
    hdd_resource.definitions.extend([hdd_processing_rate, hdd_scheduling_policy])

    # Create Delay resource type
    delay_resource = PCM.ProcessingResourceType(name="Delay")
    delay_processing_rate = PCM.PropertyDefinition(name="processingRate")
    delay_processing_rate.type = double_type
    delay_scheduling_policy = PCM.PropertyDefinition(name="schedulingPolicy")
    delay_scheduling_policy.type = scheduling_policy_type
    delay_resource.definitions.extend([delay_processing_rate, delay_scheduling_policy])

    # Create Ethernet link type
    ethernet = PCM.CommunicationLinkType(name="Ethernet")
    ethernet_throughput = PCM.PropertyDefinition(name="throughput")
    ethernet_throughput.type = double_type
    ethernet_latency = PCM.PropertyDefinition(name="latency")
    ethernet_latency.type = scheduling_policy_type
    ethernet.definitions.extend([ethernet_throughput, ethernet_latency])

    # Create PassiveResource type
    passive_resource = PCM.InternalConfigurableInterface(name="PassiveResource")
    capacity_def = PCM.PropertyDefinition(name="capacity")
    capacity_def.type = int_type
    passive_resource.definitions.append(capacity_def)

    # Add acquire and release operations
    acquire_op = PCM.OperationSignature(name="acquire")
    release_op = PCM.OperationSignature(name="release")
    passive_resource.contents.extend([acquire_op, release_op])

    # Add all resource types to repository
    resource_types.contents.extend(
        [cpu_resource, hdd_resource, delay_resource, ethernet, passive_resource]
    )

    # Create mapping configuration
    mapping_config = PCM.MappingConfiguration()

    # Add mapping entries
    mappings = [
        (fcfs_entity, "pathmap://PCM_MODELS/Palladio.resourcetype#FCFS"),
        (
            ps_entity,
            "pathmap://PCM_MODELS/Palladio.resourcetype#ProcessorSharing",
        ),
        (delay_entity, "pathmap://PCM_MODELS/Palladio.resourcetype#Delay"),
        (icpu, "pathmap://PCM_MODELS/Palladio.resourcetype#_tw_Q8E5CEeCUKeckjJ_n-w"),
        (
            process_op,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_wF22kE5CEeCUKeckjJ_n-w",
        ),
        (
            read_op,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_ygMyEE5CEeCUKeckjJ_n-w",
        ),
        (
            write_op,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_zUFtIE5CEeCUKeckjJ_n-w",
        ),
        (ihdd, "pathmap://PCM_MODELS/Palladio.resourcetype#_xXv8QE5CEeCUKeckjJ_n-w"),
        (
            ethernet,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_o3sScH2AEdyH8uerKnHYug",
        ),
        (
            cpu_resource,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_oro4gG3fEdy4YaaT-RYrLQ",
        ),
        (
            hdd_resource,
            "pathmap://PCM_MODELS/Palladio.resourcetype#_BIjHoQ3KEdyouMqirZIhzQ",
        ),
    ]

    for source, target in mappings:
        mapping_content = PCM.MappingContent()
        mapping_content.imported = source
        mapping_content.absoluteUri = target
        mapping_config.contents.append(mapping_content)

    return [primitive_types, resource_types, mapping_config]


def main():
    # Create model and add fragments
    model = PCM.Model()
    primtive_types = create_primitives()
    model.fragments.append(primtive_types)

    std_definitions = create_std_definitions(primtive_types)
    model.fragments.extend(std_definitions)

    # Save model
    model_resource = rset.create_resource(URI("std_definitions.xml"))
    model_resource.append(model)
    model_resource.save()


if __name__ == "__main__":
    main()
