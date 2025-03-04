from pyecore.ecore import EObject
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
import pyecore.ecore as ecore

# Single global instance of the standard definitions
_instance = None


def get_std_definitions(resource_set=None, ecore_path="ecores/TPCM.ecore"):
    """Get or create the singleton instance of PCMStandardDefinitions.

    Args:
        resource_set: Optional existing ResourceSet to use
        ecore_path: Path to the TPCM.ecore file (only used on first call)

    Returns:
        The singleton PCMStandardDefinitions instance
    """
    global _instance
    if _instance is None:
        _instance = _PCMStandardDefinitions(resource_set, ecore_path)
    return _instance


class _PCMStandardDefinitions:
    """Class for handling standard definitions that will be included in all models."""

    def __init__(self, resource_set=None, ecore_path="ecores/TPCM.ecore"):
        """Initialize with the metamodel and prepare standard definitions.

        Args:
            resource_set: Optional existing ResourceSet to use
            ecore_path: Path to the TPCM.ecore file
        """
        # Use provided ResourceSet or create new one
        self.rset = resource_set if resource_set is not None else ResourceSet()

        # Load metamodel
        tpcm_resource = self.rset.get_resource(URI(ecore_path))
        tpcm_metamodel = tpcm_resource.contents[0]
        self.rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel
        self._PCM = DynamicEPackage(tpcm_metamodel)

        # Container for standard elements that can be referenced during model generation
        self._elements = {}

        # Standard definition fragments
        self._primitive_types = None
        self._resource_types = None
        self._mapping_config = None

        # Initialize standard definitions
        self._initialize_std_definitions()

    def _create_primitives(self):
        """Create primitive types repository."""
        primitive_types = self._PCM.Repository(name="PrimitiveTypes")

        # Create primitive datatypes
        int_type = self._PCM.PrimitiveDatatype(
            name="Integer", type=self._PCM.PrimitiveTypeEnum.INT
        )
        double_type = self._PCM.PrimitiveDatatype(
            name="Double", type=self._PCM.PrimitiveTypeEnum.DOUBLE
        )

        # Create failure type
        cpu_failure = self._PCM.FailureType(name="CPUFailure")

        primitive_types.contents.extend([int_type, double_type])
        primitive_types.contents.append(cpu_failure)

        # Store references to primitive types
        self._elements["int_type"] = int_type
        self._elements["double_type"] = double_type
        self._elements["cpu_failure"] = cpu_failure

        return primitive_types

    def _create_resource_interfaces(self):
        """Create resource interfaces (CPU and HDD)."""
        int_type = self._elements["int_type"]
        double_type = self._elements["double_type"]

        # Create interfaces
        icpu = self._PCM.ResourceInterface(name="ICPU")
        ihdd = self._PCM.ResourceInterface(name="IHDD")

        # Create ICPU process operation
        process_op = self._PCM.OperationSignature(name="process")
        amount_param = self._PCM.Parameter(name="amount", type=double_type)
        process_op.parameters.append(amount_param)
        icpu.contents.append(process_op)

        # Create IHDD operations
        read_op = self._PCM.OperationSignature(name="read")
        read_param = self._PCM.Parameter(name="amount", type=double_type)
        read_op.parameters.append(read_param)

        write_op = self._PCM.OperationSignature(name="write")
        write_param = self._PCM.Parameter(name="amount", type=double_type)
        write_op.parameters.append(write_param)

        ihdd.contents.extend([read_op, write_op])

        # Store references
        self._elements["icpu"] = icpu
        self._elements["ihdd"] = ihdd
        self._elements["process_op"] = process_op
        self._elements["read_op"] = read_op
        self._elements["write_op"] = write_op

        return icpu, ihdd, process_op, read_op, write_op

    def _create_scheduling_policies(self):
        """Create scheduling policy types and entities."""
        scheduling_policy_type = self._PCM.ResourceEntityType(name="SchedulingPolicy")
        fcfs_entity = self._PCM.ResourceEntity(
            name="FirstComeFirstServe", type=scheduling_policy_type
        )
        ps_entity = self._PCM.ResourceEntity(
            name="ProcessorSharing", type=scheduling_policy_type
        )
        delay_entity = self._PCM.ResourceEntity(
            name="Delay", type=scheduling_policy_type
        )

        # Store references
        self._elements["scheduling_policy_type"] = scheduling_policy_type
        self._elements["fcfs_entity"] = fcfs_entity
        self._elements["ps_entity"] = ps_entity
        self._elements["delay_entity"] = delay_entity

        return scheduling_policy_type, fcfs_entity, ps_entity, delay_entity

    def _create_cpu_resource(self):
        """Create CPU resource type with properties."""
        icpu = self._elements["icpu"]
        double_type = self._elements["double_type"]
        scheduling_policy_type = self._elements["scheduling_policy_type"]
        cpu_failure = self._elements["cpu_failure"]

        cpu_resource = self._PCM.ProcessingResourceType(name="CPUResource")
        cpu_provided_role = self._PCM.ResourceInterfaceProvidedRole()
        cpu_provided_role.type = icpu
        cpu_resource.contents.append(cpu_provided_role)

        # Add failure specification to CPU
        cpu_failure_spec = self._PCM.ResourceFailureSpecification()
        cpu_failure_spec.failureType = cpu_failure
        cpu_resource.contents.append(cpu_failure_spec)

        # Add properties to CPU
        processing_rate_def = self._PCM.PropertyDefinition(name="processingRate")
        processing_rate_def.type = double_type
        scheduling_policy_def = self._PCM.PropertyDefinition(name="schedulingPolicy")
        scheduling_policy_def.type = scheduling_policy_type
        cpu_resource.definitions.extend([processing_rate_def, scheduling_policy_def])

        self._elements["cpu_resource"] = cpu_resource
        return cpu_resource

    def _create_hdd_resource(self):
        """Create HDD resource type with properties."""
        ihdd = self._elements["ihdd"]
        double_type = self._elements["double_type"]
        scheduling_policy_type = self._elements["scheduling_policy_type"]

        hdd_resource = self._PCM.ProcessingResourceType(name="HDDResource")
        hdd_provided_role = self._PCM.ResourceInterfaceProvidedRole()
        hdd_provided_role.type = ihdd
        hdd_resource.contents.append(hdd_provided_role)

        # Add properties to HDD
        hdd_processing_rate = self._PCM.PropertyDefinition(name="processingRate")
        hdd_processing_rate.type = double_type
        hdd_scheduling_policy = self._PCM.PropertyDefinition(name="schedulingPolicy")
        hdd_scheduling_policy.type = scheduling_policy_type
        hdd_resource.definitions.extend([hdd_processing_rate, hdd_scheduling_policy])

        self._elements["hdd_resource"] = hdd_resource
        return hdd_resource

    def _create_delay_resource(self):
        """Create Delay resource type with properties."""
        double_type = self._elements["double_type"]
        scheduling_policy_type = self._elements["scheduling_policy_type"]

        delay_resource = self._PCM.ProcessingResourceType(name="Delay")
        delay_processing_rate = self._PCM.PropertyDefinition(name="processingRate")
        delay_processing_rate.type = double_type
        delay_scheduling_policy = self._PCM.PropertyDefinition(name="schedulingPolicy")
        delay_scheduling_policy.type = scheduling_policy_type
        delay_resource.definitions.extend(
            [delay_processing_rate, delay_scheduling_policy]
        )

        self._elements["delay_resource"] = delay_resource
        return delay_resource

    def _create_ethernet_link(self):
        """Create Ethernet link type with properties."""
        double_type = self._elements["double_type"]
        scheduling_policy_type = self._elements["scheduling_policy_type"]

        ethernet = self._PCM.CommunicationLinkType(name="Ethernet")
        ethernet_throughput = self._PCM.PropertyDefinition(name="throughput")
        ethernet_throughput.type = double_type
        ethernet_latency = self._PCM.PropertyDefinition(name="latency")
        ethernet_latency.type = scheduling_policy_type
        ethernet.definitions.extend([ethernet_throughput, ethernet_latency])

        self._elements["ethernet"] = ethernet
        return ethernet

    def _create_passive_resource(self):
        """Create passive resource interface with properties."""
        int_type = self._elements["int_type"]

        passive_resource = self._PCM.InternalConfigurableInterface(
            name="PassiveResource"
        )
        capacity_def = self._PCM.PropertyDefinition(name="capacity")
        capacity_def.type = int_type
        passive_resource.definitions.append(capacity_def)

        # Add acquire and release operations
        acquire_op = self._PCM.OperationSignature(name="acquire")
        release_op = self._PCM.OperationSignature(name="release")
        passive_resource.contents.extend([acquire_op, release_op])

        self._elements["passive_resource"] = passive_resource
        self._elements["acquire_op"] = acquire_op
        self._elements["release_op"] = release_op

        return passive_resource

    def _create_mapping_config(self):
        """Create mapping configuration with entity mappings."""
        # Define mappings using stored references
        mappings = [
            (
                self._elements["fcfs_entity"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#FCFS",
            ),
            (
                self._elements["ps_entity"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#ProcessorSharing",
            ),
            (
                self._elements["delay_entity"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#Delay",
            ),
            (
                self._elements["icpu"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_tw_Q8E5CEeCUKeckjJ_n-w",
            ),
            (
                self._elements["process_op"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_wF22kE5CEeCUKeckjJ_n-w",
            ),
            (
                self._elements["read_op"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_ygMyEE5CEeCUKeckjJ_n-w",
            ),
            (
                self._elements["write_op"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_zUFtIE5CEeCUKeckjJ_n-w",
            ),
            (
                self._elements["ihdd"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_xXv8QE5CEeCUKeckjJ_n-w",
            ),
            (
                self._elements["ethernet"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_o3sScH2AEdyH8uerKnHYug",
            ),
            (
                self._elements["cpu_resource"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_oro4gG3fEdy4YaaT-RYrLQ",
            ),
            (
                self._elements["hdd_resource"],
                "pathmap://PCM_MODELS/Palladio.resourcetype#_BIjHoQ3KEdyouMqirZIhzQ",
            ),
        ]

        mapping_config = self._PCM.MappingConfiguration()

        for source, target in mappings:
            mapping_content = self._PCM.MappingContent()
            mapping_content.imported = source
            mapping_content.absoluteUri = target
            mapping_config.contents.append(mapping_content)

        return mapping_config

    def _initialize_std_definitions(self):
        """Initialize standard definitions and make them accessible."""
        # Create primitive types
        self._primitive_types = self._create_primitives()

        # Create resource types repository
        self._resource_types = self._PCM.ResourceTypeRepository()

        # Create and add resource interfaces
        icpu, ihdd, process_op, read_op, write_op = self._create_resource_interfaces()
        self._resource_types.contents.extend([icpu, ihdd])

        # Create and add scheduling policies
        scheduling_policy_type, fcfs_entity, ps_entity, delay_entity = (
            self._create_scheduling_policies()
        )
        self._resource_types.contents.extend(
            [scheduling_policy_type, fcfs_entity, ps_entity, delay_entity]
        )

        # Create resource types
        cpu_resource = self._create_cpu_resource()
        hdd_resource = self._create_hdd_resource()
        delay_resource = self._create_delay_resource()
        ethernet = self._create_ethernet_link()
        passive_resource = self._create_passive_resource()

        # Add all resource types to repository
        self._resource_types.contents.extend(
            [cpu_resource, hdd_resource, delay_resource, ethernet, passive_resource]
        )

        # Create mapping configuration
        self._mapping_config = self._create_mapping_config()

    # === Public API ===

    def add_to_model(self, model):
        """Add standard definitions to an existing model.

        Args:
            model: The PCM model to add standard definitions to

        Returns:
            The model with standard definitions added
        """
        model.fragments.append(self._primitive_types)
        model.fragments.append(self._resource_types)
        model.fragments.append(self._mapping_config)
        return model

    def get_element(self, key):
        """Get a standard element by key.

        Args:
            key: The identifier of the standard element

        Returns:
            The requested element or None if not found
        """
        return self._elements.get(key)

    def get_all_elements(self):
        """Get all standard elements.

        Returns:
            Dictionary of all standard elements
        """
        return self._elements.copy()  # Return a copy to prevent modification
