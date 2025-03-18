from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage, alias
from .utils import setup_metamodel


class ModelFactory:
    """Factory class for creating TPCM model elements."""

    def __init__(self, rset=None, PCM=None):
        """Initialize the factory with a resource set and PCM package.

        Args:
            rset: Optional existing ResourceSet
            PCM: Optional existing PCM DynamicEPackage
        """
        if rset is None or PCM is None:
            self.rset, self.PCM = setup_metamodel()
        else:
            self.rset = rset
            self.PCM = PCM

    # === Model and Fragment Creators ===

    def create_model(self):
        """Create a new empty TPCM model.

        Returns:
            A new Model instance
        """
        return self.PCM.Model()

    def create_repository(self, name):
        """Create a new repository.

        Args:
            name: Name of the repository

        Returns:
            A new Repository instance
        """
        return self.PCM.Repository(name=name)

    def create_system(self, name):
        """Create a new system.

        Args:
            name: Name of the system

        Returns:
            A new System instance
        """
        return self.PCM.System(name=name)

    def create_allocation(self, name):
        """Create a new allocation.

        Args:
            name: Name of the allocation

        Returns:
            A new Allocation instance
        """
        return self.PCM.Allocation(name=name)

    def create_usage(self, name):
        """Create a new usage model.

        Args:
            name: Name of the usage model

        Returns:
            A new Usage instance
        """
        return self.PCM.Usage(name=name)

    # === Components and Interfaces ===

    def create_interface(self, name):
        """Create a new interface.

        Args:
            name: Name of the interface

        Returns:
            A new Interface instance
        """
        return self.PCM.Interface(name=name)

    def create_domain_interface(self, name):
        """Create a new domain interface.

        Args:
            name: Name of the domain interface

        Returns:
            A new DomainInterface instance
        """
        return self.PCM.DomainInterface(name=name)

    def create_operation_signature(self, name, return_type=None):
        """Create a new operation signature.

        Args:
            name: Name of the operation
            return_type: Optional return type (Datatype)

        Returns:
            A new OperationSignature instance
        """
        sig = self.PCM.OperationSignature(name=name)
        if return_type:
            # For Python keywords, PyEcore uses _keyword naming convention
            sig._return = return_type
        return sig

    def create_parameter(self, name, param_type):
        """Create a new parameter.

        Args:
            name: Name of the parameter
            param_type: Type of the parameter (Datatype)

        Returns:
            A new Parameter instance
        """
        return self.PCM.Parameter(name=name, type=param_type)

    def create_component(self, name):
        """Create a new component.

        Args:
            name: Name of the component

        Returns:
            A new Component instance
        """
        return self.PCM.Component(name=name)

    def create_provided_role(self, name, interface):
        """Create a new provided role.

        Args:
            name: Name of the role
            interface: The interface being provided

        Returns:
            A new DomainInterfaceProvidedRole instance
        """
        role = self.PCM.DomainInterfaceProvidedRole(name=name)
        role.type = interface
        return role

    def create_required_role(self, name, interface):
        """Create a new required role.

        Args:
            name: Name of the role
            interface: The interface being required

        Returns:
            A new InterfaceRequiredRole instance
        """
        role = self.PCM.InterfaceRequiredRole(name=name)
        role.type = interface
        return role

    # === Datatypes ===

    def create_primitive_datatype(self, name, type_enum):
        """Create a primitive datatype.

        Args:
            name: Name of the datatype
            type_enum: PrimitiveTypeEnum value

        Returns:
            A new PrimitiveDatatype instance
        """
        return self.PCM.PrimitiveDatatype(name=name, type=type_enum)

    def create_collection_datatype(self, name, collection_type):
        """Create a collection datatype.

        Args:
            name: Name of the collection
            collection_type: Type of elements in the collection

        Returns:
            A new CollectionDatatype instance
        """
        coll = self.PCM.CollectionDatatype(name=name)
        coll.collectionType = collection_type
        return coll

    def create_composed_datatype(self, name, elements=None):
        """Create a composed datatype.

        Args:
            name: Name of the composed type
            elements: Optional list of (name, type) tuples for elements

        Returns:
            A new ComposedDatatype instance
        """
        composed = self.PCM.ComposedDatatype(name=name)
        if elements:
            for element_name, element_type in elements:
                element = self.PCM.ComposedDatatypeElement(name=element_name)
                element.reference = element_type
                composed.elements.append(element)
        return composed

    # === System Structure ===

    def create_assembly_context(self, name, component):
        """Create an assembly context.

        Args:
            name: Name of the assembly context
            component: Component being assembled

        Returns:
            A new AssemblyContext instance
        """
        assembly = self.PCM.AssemblyContext(name=name)
        assembly.component = component
        return assembly

    def create_connector(
        self, name=None, from_context=None, to_context=None, requiring_role=None
    ):
        """Create a connector between assembly contexts.
        Args:
            name: Name of the connector
            from_context: Source assembly context
            to_context: Target assembly context
            requiring_role: The required role being connected
        Returns:
            A new Connector instance
        """
        connector = self.PCM.Connector()
        if name:
            connector.name = name

        # For dynamic models, you need to establish the alias if it hasn't been done yet
        connector_class = connector.eClass

        # Find the 'from' feature (PyEcore should handle this internally as '_from')
        from_feature = next(
            (f for f in connector_class.eStructuralFeatures if f.name == "from"), None
        )

        if from_feature and not hasattr(connector_class, "alias_set"):
            # Create an alias 'from_context' for the 'from' feature
            alias("from_context", from_feature)
            connector_class.alias_set = True

        # Now use the alias to set the value
        connector.from_context = from_context
        connector.to = to_context

        if requiring_role:
            connector.requiringRole = requiring_role

        return connector

    def create_system_provided_role(self, name, interface, assembly_context):
        """Create a system provided role.

        Args:
            name: Name of the role
            interface: The interface being provided
            assembly_context: The assembly context that provides the interface

        Returns:
            A new SystemProvidedRole instance
        """
        role = self.PCM.SystemProvidedRole(name=name)
        role.type = interface
        role.to = assembly_context
        return role

    # === Resource Environment ===

    def create_resource_container(self, name):
        """Create a resource container.

        Args:
            name: Name of the resource container

        Returns:
            A new ResourceContainer instance
        """
        return self.PCM.ResourceContainer(name=name)

    def create_processing_resource(self, name, resource_type):
        """Create a processing resource.

        Args:
            name: Name of the processing resource
            resource_type: Type of resource (ProcessingResourceType)

        Returns:
            A new ProcessingResource instance
        """
        resource = self.PCM.ProcessingResource(name=name)
        resource.type = resource_type
        return resource

    def create_linking_resource(self, name, link_type, connected_containers):
        """Create a linking resource.

        Args:
            name: Name of the linking resource
            link_type: Communication link type
            connected_containers: List of connected ResourceContainers

        Returns:
            A new LinkingResource instance
        """
        link = self.PCM.LinkingResource(name=name)
        link.type = link_type
        for container in connected_containers:
            link.connected.append(container)
        return link

    # === Allocation ===

    def create_allocation_context(self, name, assembly_contexts, container):
        """Create an allocation context.

        Args:
            name: Name of the allocation context
            assembly_contexts: List of assembly contexts to allocate
            container: Resource container to allocate to

        Returns:
            A new AllocationContext instance
        """
        allocation = self.PCM.AllocationContext(name=name)
        spec = self.PCM.AllocationSpecification()
        spec.container = container
        for assembly in assembly_contexts:
            spec.assemblies.append(assembly)
        allocation.spec = spec
        return allocation

    # === Usage Model ===

    def create_usage_scenario(self, name):
        """Create a usage scenario.

        Args:
            name: Name of the usage scenario

        Returns:
            A new UsageScenario instance
        """
        return self.PCM.UsageScenario(name=name)

    def create_usage_model(self, name):
        """Create a usage model.

        Args:
            name: Name of the usage model

        Returns:
            A new Usage instance
        """
        return self.PCM.Usage(name=name)

    def create_open_workload(self, inter_arrival_time_expr):
        """Create an open workload.

        Args:
            inter_arrival_time_expr: Expression for inter-arrival time

        Returns:
            A new OpenWorkload instance
        """
        workload = self.PCM.OpenWorkload()
        workload.interArrivalTime = inter_arrival_time_expr
        return workload

    def create_closed_workload(self, num_users, think_time_expr):
        """Create a closed workload.

        Args:
            num_users: Number of users in the workload
            think_time_expr: Expression for think time

        Returns:
            A new ClosedWorkload instance
        """
        workload = self.PCM.ClosedWorkload(numberOfUsers=num_users)
        workload.thinkTime = think_time_expr
        return workload

    def create_entry_level_system_call(self, role, signature, parameters=None):
        """Create an entry level system call.

        Args:
            role: SystemProvidedRole to call
            signature: Signature to call
            parameters: Optional list of parameter specifications

        Returns:
            A new EntryLevelSystemCallAction instance
        """
        call = self.PCM.EntryLevelSystemCallAction()
        call.role = role
        call.signature = signature
        if parameters:
            for param in parameters:
                call.parameters.append(param)
        return call
    
    def create_absolute_reference(self, reference):
        """Create an absolute reference.
        
        Args:
            reference: Reference
            
        Returns:
            A new AbsoluteReference
        """
        ref = self.PCM.AbsoluteReference()
        ref.reference = reference
        return ref

    # === SEFF (Service Effect Specification) ===

    def create_seff(self, provided_role, signature):
        """Create a service effect specification.

        Args:
            provided_role: The provided role this SEFF belongs to
            signature: The operation signature this SEFF implements

        Returns:
            A new SEFF instance
        """
        seff = self.PCM.SEFF()
        seff.role = provided_role
        seff.signatur = signature
        return seff

    def create_seff_call_action(self, role, signature, parameters=None):
        """Create a SEFF call action.

        Args:
            role: Role to call
            signature: Signature to call
            parameters: Optional list of parameter specifications

        Returns:
            A new SEFFCallAction instance
        """
        call = self.PCM.SEFFCallAction()
        call.role = role
        call.signature = signature
        if parameters:
            for param in parameters:
                call.parameters.append(param)
        return call

    def create_parameter_specification(self, reference=None, specification=None):
        ps = self.PCM.ParameterSpecification()
        ps.reference = reference
        ps.specification = specification

        return ps
