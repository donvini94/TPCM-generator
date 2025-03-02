import random
import string
from model_factory import ModelFactory
from expression_factory import ExpressionFactory
from utils import setup_metamodel, save_model
from std_definitions import get_std_definitions
from resource_environment import get_resource_environment


class ModelGenerator:
    """Generator for PCM models, both minimal working examples and random models."""

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
            interface = self.model_factory.create_interface(
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

            # Each component provides 0-2 interfaces
            provided_count = random.randint(0, 2)
            for j in range(provided_count):
                if self.interfaces:
                    interface = random.choice(self.interfaces)
                    role = self.model_factory.create_provided_role(
                        self._random_name("provided"), interface
                    )
                    component.contents.append(role)

            # Each component requires 0-3 interfaces
            required_count = random.randint(0, 3)
            for j in range(required_count):
                if self.interfaces:
                    interface = random.choice(self.interfaces)
                    role = self.model_factory.create_required_role(
                        self._random_name("required"), interface
                    )
                    component.contents.append(role)

            repository.contents.append(component)
            self.components.append(component)

        return repository

    def generate_system(self, repository=None):
        """Generate a random system based on a repository.

        Args:
            repository: Optional repository to use (if None, one will be generated)

        Returns:
            Generated system
        """
        # Create repository if not provided
        if repository is None:
            repository = self.generate_repository()

        # Create system
        system = self.model_factory.create_system(self._random_name("system"))

        # Create assembly contexts (1 per component)
        for component in self.components:
            assembly = self.model_factory.create_assembly_context(
                self._random_name("assembly"), component
            )
            system.contents.append(assembly)
            self.assembly_contexts.append(assembly)

        # Create connectors between assemblies
        for from_assembly in self.assembly_contexts:
            # Get required roles from the component
            from_component = from_assembly.component
            for content in from_component.contents:
                if content.eClass.name == "InterfaceRequiredRole":
                    # Find an assembly with a matching provided interface
                    interface = content.type
                    for to_assembly in self.assembly_contexts:
                        to_component = to_assembly.component
                        for to_content in to_component.contents:
                            if (
                                to_content.eClass.name == "DomainInterfaceProvidedRole"
                                and to_content.type == interface
                            ):
                                # Create connector
                                connector = self.model_factory.create_connector(
                                    self._random_name("connector"),
                                    from_assembly,
                                    to_assembly,
                                    content,
                                )
                                system.contents.append(connector)
                                break

        # Create system provided roles
        # Choose components that provide interfaces
        for assembly in self.assembly_contexts:
            component = assembly.component
            for content in component.contents:
                if content.eClass.name == "DomainInterfaceProvidedRole":
                    # With 50% probability, create a system provided role
                    if random.random() < 0.5:
                        system_role = self.model_factory.create_system_provided_role(
                            self._random_name("system_provided"), content.type, assembly
                        )
                        system.contents.append(system_role)

        return system

    def generate_resource_environment(self, num_containers=3):
        """Generate a random resource environment.

        Args:
            num_containers: Number of resource containers to generate

        Returns:
            Generated resource environment
        """
        # Create resource environment
        resource_env = self.model_factory.create_resource_environment(
            self._random_name("resource_environment")
        )

        # Get resource types from standard definitions
        cpu_resource = self.std_defs.get_element("cpu_resource")
        hdd_resource = self.std_defs.get_element("hdd_resource")

        # Create resource containers
        for i in range(num_containers):
            container = self.model_factory.create_resource_container(
                self._random_name("container")
            )

            # Add CPU and HDD resources to each container
            cpu = self.model_factory.create_processing_resource(
                self._random_name("cpu"), cpu_resource
            )
            container.contents.append(cpu)

            hdd = self.model_factory.create_processing_resource(
                self._random_name("hdd"), hdd_resource
            )
            container.contents.append(hdd)

            resource_env.contents.append(container)
            self.resource_containers.append(container)

        # Create linking resources between containers
        ethernet = self.std_defs.get_element("ethernet")
        for i in range(len(self.resource_containers) - 1):
            link = self.model_factory.create_linking_resource(
                self._random_name("link"),
                ethernet,
                [self.resource_containers[i], self.resource_containers[i + 1]],
            )
            resource_env.contents.append(link)

        return resource_env

    def generate_allocation(self, system=None, resource_env=None):
        """Generate a random allocation.

        Args:
            system: Optional system to use (if None, one will be generated)
            resource_env: Optional resource environment to use (if None, one will be generated)

        Returns:
            Generated allocation
        """
        # Create system and resource environment if not provided
        if system is None:
            system = self.generate_system()
        if resource_env is None:
            resource_env = self.generate_resource_environment()

        # Create allocation
        allocation = self.model_factory.create_allocation(
            self._random_name("allocation")
        )

        # Allocate assembly contexts to resource containers
        for assembly in self.assembly_contexts:
            # Choose a random resource container
            container = random.choice(self.resource_containers)

            # Create allocation context
            allocation_ctx = self.model_factory.create_allocation_context(
                self._random_name("allocation_ctx"), [assembly], container
            )
            allocation.contents.append(allocation_ctx)

        return allocation

    def generate_usage_model(self, system=None):
        """Generate a random usage model.

        Args:
            system: Optional system to use (if None, one will be generated)

        Returns:
            Generated usage model
        """
        # Create system if not provided
        if system is None:
            system = self.generate_system()

        # Create usage model
        usage = self.model_factory.create_usage(self._random_name("usage"))

        # Create usage scenario
        scenario = self.model_factory.create_usage_scenario(
            self._random_name("scenario")
        )

        # Choose between open and closed workload
        if random.random() < 0.5:
            # Create open workload
            arrival_rate = self.expr_factory.create_double_literal(
                random.uniform(0.1, 2.0)
            )
            workload = self.model_factory.create_open_workload(arrival_rate)
        else:
            # Create closed workload
            num_users = random.randint(1, 20)
            think_time = self.expr_factory.create_double_literal(
                random.uniform(1.0, 10.0)
            )
            workload = self.model_factory.create_closed_workload(num_users, think_time)

        scenario.workload = workload

        # Find system provided roles
        system_roles = []
        for content in system.contents:
            if content.eClass.name == "SystemProvidedRole":
                system_roles.append(content)

        # Create system calls
        if system_roles:
            for i in range(random.randint(1, 5)):
                role = random.choice(system_roles)
                # Find a signature from the role's interface
                interface = role.type
                signatures = []
                for content in interface.contents:
                    if (
                        content.eClass.name == "Signature"
                        or content.eClass.name == "OperationSignature"
                    ):
                        signatures.append(content)

                if signatures:
                    signature = random.choice(signatures)
                    call = self.model_factory.create_entry_level_system_call(
                        role, signature
                    )
                    scenario.contents.append(call)

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
        resource_env = get_resource_environment(self.model_factory.rset)
        resource_env.add_to_model(model)

        # Generate all model elements
        repository = self.generate_repository()
        system = self.generate_system(repository)
        resource_env = self.generate_resource_environment()
        allocation = self.generate_allocation(system, resource_env)
        usage = self.generate_usage_model(system)

        # Add elements to model
        model.fragments.extend([repository, system, resource_env, allocation, usage])

        # Save model
        xml_filename = f"{model_name}.xml"
        model_resource = save_model(model, xml_filename, self.model_factory.rset)

        return model, model_resource


def create_minimal_model(output_file="minimal_model.xml"):
    """Create a minimal working model with all required elements.

    Args:
        output_file: Name of the output XML file

    Returns:
        The created model
    """
    # Initialize the metamodel and factories
    rset, PCM = setup_metamodel()
    model_factory = ModelFactory(rset, PCM)
    expr_factory = ExpressionFactory(rset)

    # Get standard definitions and resource environment
    std_defs = get_std_definitions(rset)
    resource_env = get_resource_environment(rset)

    # Create the base model
    model = model_factory.create_model()

    # Add standard definitions and resource environment
    std_defs.add_to_model(model)
    resource_env.add_to_model(model)

    # Create repository
    repository = model_factory.create_repository("MinimalRepository")

    # Create a custom datatype
    file_content_type = model_factory.create_composed_datatype("FileContent", [])
    repository.contents.append(file_content_type)

    # Get primitive types from standard definitions
    int_type = std_defs.get_element("int_type")  # Integer type

    # Create a more complex composed datatype with elements
    audio_request_type = model_factory.create_composed_datatype(
        "AudioRequest", [("Count", int_type), ("Size", int_type)]
    )
    repository.contents.append(audio_request_type)

    # Create a domain interface (needed for TPCM conversion)
    interface = model_factory.create_domain_interface("IFileStorage")

    # Add operations to the interface
    get_files_op = model_factory.create_operation_signature("getFiles")
    get_files_param = model_factory.create_parameter("request", audio_request_type)
    get_files_op.parameters.append(get_files_param)
    get_files_op._return = file_content_type  # Use _keyword for Python keywords
    interface.contents.append(get_files_op)

    store_op = model_factory.create_operation_signature("storeFile")
    store_param = model_factory.create_parameter("file", file_content_type)
    store_op.parameters.append(store_param)
    interface.contents.append(store_op)

    #    # Add interface to repository
    repository.contents.append(interface)

    # Create a component
    component = model_factory.create_component("FileStorage")

    # Add provided role to component
    provided_role = model_factory.create_provided_role("storage", interface)
    component.contents.append(provided_role)

    # Get standard resource interfaces
    icpu = std_defs.get_element("icpu")
    ihdd = std_defs.get_element("ihdd")

    # Add required roles for resources
    cpu_role = model_factory.create_required_role("cpu", icpu)
    hdd_role = model_factory.create_required_role("hdd", ihdd)
    component.contents.append(cpu_role)
    component.contents.append(hdd_role)

    # Create SEFFs for the component
    # Get standard operations for resources
    process_op = std_defs.get_element("process_op")
    read_op = std_defs.get_element("read_op")

    # SEFF for getFiles operation
    get_files_seff = model_factory.create_seff(provided_role, get_files_op)

    # CPU processing action with constant value
    cpu_usage_expr = expr_factory.create_double_literal(75182981.91)
    cpu_param = model_factory.create_parameter_specification(cpu_usage_expr)
    cpu_process = model_factory.create_seff_call_action(
        cpu_role, process_op, [cpu_param]
    )

    # HDD read action with simple value
    hdd_read_expr = expr_factory.create_int_literal(1000)  # Simple value for test
    hdd_param = model_factory.create_parameter_specification(hdd_read_expr)
    hdd_read = model_factory.create_seff_call_action(hdd_role, read_op, [hdd_param])

    # Add actions to SEFF
    get_files_seff.contents.extend([cpu_process, hdd_read])

    # SEFF for storeFile operation
    store_file_seff = model_factory.create_seff(provided_role, store_op)

    # Simple CPU processing for store operation
    store_cpu_expr = expr_factory.create_double_literal(75182981.91)
    store_cpu_param = model_factory.create_parameter_specification(store_cpu_expr)
    store_cpu_process = model_factory.create_seff_call_action(
        cpu_role, process_op, [store_cpu_param]
    )

    # Add actions to SEFF
    store_file_seff.contents.append(store_cpu_process)

    # Add SEFFs to component
    component.contents.extend([get_files_seff, store_file_seff])

    # Add component to repository
    repository.contents.append(component)

    # Add repository to model
    model.fragments.append(repository)

    # Save the model
    save_model(model, output_file, rset)

    print(f"Minimal model created successfully: {output_file}")
    return model


def main():
    """Main function to generate models."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate PCM models")
    parser.add_argument(
        "--minimal", action="store_true", help="Generate a minimal working model"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="generated",
        help="Output file name (without extension)",
    )
    parser.add_argument(
        "--convert",
        "-c",
        action="store_true",
        help="Convert to TPCM format after generation",
    )

    args = parser.parse_args()

    # Generate the appropriate model
    output_file = f"{args.output}.xml"

    if args.minimal:
        model = create_minimal_model(output_file)
        print(f"Minimal model generated: {output_file}")
    else:
        # Create model generator for random models
        generator = ModelGenerator(seed=42)  # Set seed for reproducibility
        model, model_resource = generator.generate_complete_model(args.output)
        print(f"Random model generated: {output_file}")

    # Optionally convert to TPCM format
    if args.convert:
        import subprocess

        tpcm_path = f"{args.output}.tpcm"
        try:
            result = subprocess.run(
                ["java", "-jar", "SaveAs.jar", output_file, tpcm_path],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Model converted to TPCM format: {tpcm_path}")
            if result.stdout:
                print(f"Converter output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting to TPCM format: {e}")
            if e.stdout:
                print(f"Converter stdout: {e.stdout}")
            if e.stderr:
                print(f"Converter stderr: {e.stderr}")


if __name__ == "__main__":
    main()
