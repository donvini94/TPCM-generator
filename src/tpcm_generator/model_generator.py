import random
import string
from .model_factory import ModelFactory
from .expression_factory import ExpressionFactory
from .utils import setup_metamodel, save_model
from .std_definitions import get_std_definitions
from .resource_environment import get_resource_environment


class ModelGenerator:
    """Generator for PCM models, both minimal working examples and random models."""

    # TODO: add magic number definitions at the top so they can be globally configured easily for expirments (param_count, sig_count, provided_count... etc.)
    def __init__(self, seed=None):
        """Initialize the model generator.

        Args:
            seed: Optional random seed for reproducibility
        """
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)

        # Initialize factories
        self.model_factory = ModelFactory()
        self.expr_factory = ExpressionFactory(self.model_factory.rset)
        self.std_defs = get_std_definitions(self.model_factory.rset)
        self.resource_env = get_resource_environment(self.model_factory.rset)

        # Store created elements for reference
        self.primitive_types = {}
        self.interfaces = []
        self.components = []
        self.signatures = []
        self.assembly_contexts = []
        self.resource_containers = []

    def _random_name(self, prefix):
        """Generate a random name with a given prefix.

        Args:
            prefix: Prefix for the name

        Returns:
            A random name string
        """
        suffix = "".join(random.choices(string.ascii_uppercase, k=5))
        return f"{prefix}_{suffix}"

    def _create_primitive_types(self, repository):
        """Create primitive datatypes and add them to a repository.

        Args:
            repository: Repository to add types to

        Returns:
            Dictionary of created types
        """
        # Use the same names as in std_definitions.py
        type_enums = {
            "Integer": self.model_factory.PCM.PrimitiveTypeEnum.INT,
            "String": self.model_factory.PCM.PrimitiveTypeEnum.STRING,
            "Boolean": self.model_factory.PCM.PrimitiveTypeEnum.BOOL,
            "Double": self.model_factory.PCM.PrimitiveTypeEnum.DOUBLE,
        }

        for name, enum_val in type_enums.items():
            datatype = self.model_factory.create_primitive_datatype(name, enum_val)
            repository.contents.append(datatype)
            self.primitive_types[name] = datatype

        return self.primitive_types

    def _create_random_signature(self, interface, return_type=None):
        """Create a random operation signature.

        Args:
            interface: Interface to add the signature to
            return_type: Optional return type

        Returns:
            Created signature
        """
        # Choose random name and return type
        name = self._random_name("operation")
        if return_type is None:
            return_type = random.choice(list(self.primitive_types.values()))

        # Create signature
        signature = self.model_factory.create_operation_signature(name, return_type)

        # Add random parameters (0-3)
        param_count = random.randint(0, 3)
        for i in range(param_count):
            param_type = random.choice(list(self.primitive_types.values()))
            param = self.model_factory.create_parameter(f"param{i}", param_type)
            signature.parameters.append(param)

        # Add to interface
        interface.contents.append(signature)
        self.signatures.append(signature)

        return signature

    def generate_repository(self, num_interfaces=5, num_components=10):
        """Generate a random repository with interfaces and components.

        Args:
            num_interfaces: Number of interfaces to generate
            num_components: Number of components to generate

        Returns:
            Generated repository
        """
        # Create repository
        repository = self.model_factory.create_repository(
            self._random_name("repository")
        )

        # Create primitive types
        self._create_primitive_types(repository)

        # Create interfaces
        for i in range(num_interfaces):
            interface = self.model_factory.create_domain_interface(
                self._random_name("interface")
            )

            # Add 1-5 signatures to each interface
            sig_count = random.randint(1, 5)
            for j in range(sig_count):
                self._create_random_signature(interface)

            repository.contents.append(interface)
            self.interfaces.append(interface)

        # Create components
        for i in range(num_components):
            component = self.model_factory.create_component(
                self._random_name("component")
            )
            provided_roles = []
            required_roles = []

            # Each component provides 0-2 interfaces
            provided_count = random.randint(0, 2)
            for j in range(provided_count):
                if self.interfaces:
                    provided_role = random.choice(self.interfaces)
                    role = self.model_factory.create_provided_role(
                        self._random_name("provided"), provided_role
                    )
                    component.contents.append(role)
                    provided_roles.append(role)

            # Each component requires 0-3 interfaces
            required_count = random.randint(0, 3)
            for j in range(required_count):
                if self.interfaces:
                    # FIXME: Doesn't this mean we can have components that require and provide the same role?
                    required_role = random.choice(self.interfaces)
                    role = self.model_factory.create_required_role(
                        self._random_name("required"), required_role
                    )
                    component.contents.append(role)
                    required_roles.append(role)

            cpu_role = self.model_factory.create_required_role(
                "cpu", self.std_defs.get_cpu_interface()
            )
            hdd_role = self.model_factory.create_required_role(
                "hdd", self.std_defs.get_hdd_interface()
            )
            required_roles.extend([cpu_role, hdd_role])
            component.contents.extend([cpu_role, hdd_role])
            repository.contents.append(component)

            for provided_role in provided_roles:
                for signatur in provided_role.type.contents:
                    seff = self.model_factory.create_seff(provided_role, signatur)
                    # TODO: Random zwischen 1 und anzahl der rollen in required roles
                    # TODO: 2. Ebene: Anzahl signatures in interfaces von der required role die man gewählt hat
                    required_role = random.choice(required_roles)
                    required_interface = required_role.type
                    required_signature = random.choice(required_interface.contents)
                    parameters = required_signature.parameters

                    coa = self.model_factory.create_seff_call_action(
                        required_role, required_signature
                    )
                    # TODO: Refactor into function
                    for param in parameters:
                        #                        print(f"{param.name} : {param.type.name}")

                        if param.type == self.primitive_types["Integer"]:
                            result = self.model_factory.create_parameter_specification(
                                specification=self.expr_factory.create_int_literal(
                                    random.randint(0, 100)
                                )
                            )
                            coa.parameters.append(result)

                        elif param.type == self.primitive_types["String"]:
                            # Create random string result
                            length = random.randint(5, 15)
                            random_string = "".join(
                                random.choices(
                                    string.ascii_letters + string.digits, k=length
                                )
                            )
                            result = self.model_factory.create_parameter_specification(
                                specification=self.expr_factory.create_string_literal(
                                    random_string
                                )
                            )
                            coa.parameters.append(result)

                        elif param.type == self.primitive_types["Boolean"]:
                            # Create random boolean result
                            result = self.model_factory.create_parameter_specification(
                                specification=self.expr_factory.create_bool_literal(
                                    random.choice([True, False])
                                )
                            )
                            coa.parameters.append(result)
                        # FIXME: Current workaround because of type issue with CPU and HDD
                        else:
                            result = self.model_factory.create_parameter_specification(
                                specification=self.expr_factory.create_double_literal(
                                    round(random.uniform(0.0, 100.0), 2)
                                )
                            )
                            coa.parameters.append(result)
                    seff.contents.append(coa)
                    component.contents.append(seff)
            self.components.append(component)

        return repository

    def generate_system(self, repository):
        """Generate a random system with assembly contexts and connectors.

        Args:
            repository: Repository with components and interfaces

        Returns:
            Generated system
        """
        # Create system
        system = self.model_factory.create_system(self._random_name("system"))

        # Create assembly contexts for random components
        available_components = [c for c in self.components if c.contents]
        if not available_components:
            return system

        # Select random components to include in the system
        selected_components = []
        num_assemblies = min(random.randint(2, 5), len(available_components))
        selected_components = random.sample(available_components, num_assemblies)

        # Create assembly contexts for each selected component
        for component in selected_components:
            assembly = self.model_factory.create_assembly_context(
                self._random_name("assembly"), component
            )
            system.contents.append(assembly)
            self.assembly_contexts.append(assembly)

        # Find provided and required roles from the assemblies
        provided_roles = []
        required_roles = []
        for assembly in self.assembly_contexts:
            component = assembly.component
            for role in component.contents:
                if isinstance(role, self.model_factory.PCM.DomainInterfaceProvidedRole):
                    provided_roles.append((assembly, role))
                elif isinstance(role, self.model_factory.PCM.InterfaceRequiredRole):
                    required_roles.append((assembly, role))

        # Fix connector issues: For each component, create a connector for all its required roles
        # that connects to components providing the matching interface
        for req_assembly, req_role in required_roles:
            # Skip CPU and HDD roles as they're handled separately
            if req_role.name in ["cpu", "hdd"]:
                continue
                
            # Find matching provided roles
            matching_provided = [
                (prov_assembly, prov_role)
                for prov_assembly, prov_role in provided_roles
                if prov_role.type == req_role.type and prov_assembly != req_assembly
            ]
            
            if matching_provided:
                # Randomly select a provider
                prov_assembly, prov_role = random.choice(matching_provided)

                # Create connector with explicit from and to values
                connector = self.model_factory.create_connector(
                    self._random_name("connector"),
                    from_context=req_assembly,
                    to_context=prov_assembly,
                    requiring_role=req_role,
                )
                
                # Explicitly verify that the connector has from and to values set
                if not hasattr(connector, '_from') or not connector._from:
                    connector._from = req_assembly
                if not hasattr(connector, 'to') or not connector.to:
                    connector.to = prov_assembly
                
                system.contents.append(connector)

        # Create system provided roles for some of the provided interfaces
        # (exposing some component interfaces to the outside world)
        exposed_count = min(random.randint(1, 3), len(provided_roles))
        if provided_roles:
            exposed_provided = random.sample(provided_roles, exposed_count)

            for assembly, role in exposed_provided:
                system_role = self.model_factory.create_system_provided_role(
                    self._random_name("system_provided"), role.type, assembly
                )
                system.contents.append(system_role)

        return system

    def generate_allocation(self, system):
        """Generate an allocation of a system to resource containers.

        Args:
            system: System to allocate

        Returns:
            Generated allocation
        """
        # Create allocation
        allocation = self.model_factory.create_allocation(
            self._random_name("allocation")
        )

        # Get the resource containers from the resource environment
        containers = self.resource_env.get_resource_containers()

        if not containers or not system:
            return allocation

        # Group assemblies for allocation to containers
        assemblies = [
            content
            for content in system.contents
            if hasattr(content, "eClass") and content.eClass.name == "AssemblyContext"
        ]

        if not assemblies:
            return allocation

        # Distribute assemblies across resource containers randomly
        num_groups = min(len(containers), len(assemblies))
        # Create at least one group, but not more than we have containers or assemblies
        num_groups = max(1, random.randint(1, num_groups))

        # Split assemblies into groups
        assembly_groups = []
        assemblies_copy = assemblies.copy()
        random.shuffle(assemblies_copy)

        # Distribute assemblies evenly across groups
        group_size = len(assemblies_copy) // num_groups
        remainder = len(assemblies_copy) % num_groups

        start = 0
        for i in range(num_groups):
            size = group_size + (1 if i < remainder else 0)
            end = start + size
            if size > 0:
                assembly_groups.append(assemblies_copy[start:end])
            start = end

        # Create allocation contexts
        for i, group in enumerate(assembly_groups):
            if i < len(containers) and group:
                container = containers[i]
                alloc_ctx = self.model_factory.create_allocation_context(
                    self._random_name("alloc"), group, container
                )
                allocation.contents.append(alloc_ctx)

        return allocation

    def generate_usage_model(self, system):
        """Generate a usage model for a system.

        Args:
            system: System the usage model is for

        Returns:
            Generated usage model
        """
        # Create usage model
        usage = self.model_factory.create_usage_model(self._random_name("usage"))

        # Find system provided roles that can be called
        system_provided_roles = [
            content
            for content in system.contents
            if hasattr(content, "eClass")
            and content.eClass.name == "SystemProvidedRole"
        ]

        if not system_provided_roles:
            return usage

        # Create a usage scenario
        scenario = self.model_factory.create_usage_scenario(
            self._random_name("scenario")
        )

        # Create workload (randomly choose between open and closed workload)
        if random.choice([True, False]):
            # Open workload with exponential distribution
            inter_arrival_time = f"Exp({random.uniform(0.01, 0.1):.2f})"
            workload = self.model_factory.create_open_workload(inter_arrival_time)
        else:
            # Closed workload
            num_users = random.randint(1, 20)
            think_time = f"Exp({random.uniform(0.5, 5.0):.2f})"
            workload = self.model_factory.create_closed_workload(num_users, think_time)

        scenario.workload = workload

        # Create entry level system calls to random system provided roles
        call_count = random.randint(1, 3)
        for _ in range(call_count):
            # Choose random role
            role = random.choice(system_provided_roles)

            # Find a signature from the interface
            if role.type and role.type.contents:
                signatures = [
                    sig
                    for sig in role.type.contents
                    if hasattr(sig, "eClass") and sig.eClass.name == "Signature"
                ]

                if signatures:
                    signature = random.choice(signatures)

                    # Create parameter specifications for parameters if needed
                    params = []
                    for param in signature.parameters:
                        # Create random parameter values based on parameter type
                        if param.type.eClass.name == "PrimitiveDatatype":
                            if param.type.type.name == "INT":
                                value = random.randint(1, 100)
                                params.append(
                                    self.model_factory.create_parameter_specification(
                                        str(value)
                                    )
                                )
                            elif param.type.type.name == "DOUBLE":
                                value = random.uniform(1.0, 100.0)
                                params.append(
                                    self.model_factory.create_parameter_specification(
                                        str(value)
                                    )
                                )
                            else:
                                # Default for other types
                                params.append(
                                    self.model_factory.create_parameter_specification(
                                        "1"
                                    )
                                )

                    # Create entry level system call
                    call = self.model_factory.create_entry_level_system_call(
                        role, signature, params
                    )
                    scenario.contents.append(call)

        # Add scenario to usage model
        usage.contents.append(scenario)

        return usage

    def generate_complete_model(self, model_name="generated"):
        """Generate a complete PCM model with all elements.

        Args:
            model_name: Base name for the model and output files

        Returns:
            Tuple of (model, model_resource)
        """
        # Create model
        model = self.model_factory.create_model()

        # Add standard definitions and resource environment
        self.std_defs.add_to_model(model)
        # Get resource environment from the singleton pattern
        self.resource_env.add_to_model(model)
        # Generate all model elements
        repository = self.generate_repository()
        system = self.generate_system(repository)
        allocation = self.generate_allocation(system)
        # usage = self.generate_usage_model(system)

        # Add elements to model
        model.fragments.extend([repository, system, allocation])

        # Save model
        xml_filename = f"{model_name}.xml"
        model_resource = save_model(model, xml_filename, self.model_factory.rset)

        return model, model_resource
