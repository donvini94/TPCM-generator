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


def create_mediastore_model(output_file="mediastore_model.xml"):
    """Create a MediaStore model based on the MediaStore.tpcm example.

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
    repository = model_factory.create_repository("MediaStore")

    # Create datatypes
    file_content_type = model_factory.create_composed_datatype("FileContent", [])
    repository.contents.append(file_content_type)

    # Get primitive types from standard definitions
    int_type = std_defs.get_element("int_type")  # Integer type

    # Create AudioCollectionRequest datatype
    audio_collection_request_type = model_factory.create_composed_datatype(
        "AudioCollectionRequest", [("Count", int_type), ("Size", int_type)]
    )
    repository.contents.append(audio_collection_request_type)

    # Create interfaces
    # 1. IFileStorage interface
    ifile_storage = model_factory.create_domain_interface("IFileStorage")
    
    get_files_op = model_factory.create_operation_signature("getFiles")
    get_files_param = model_factory.create_parameter("audioRequest", audio_collection_request_type)
    get_files_op.parameters.append(get_files_param)
    get_files_op._return = file_content_type  # Set return type to FileContent
    ifile_storage.contents.append(get_files_op)
    
    store_file_op = model_factory.create_operation_signature("storeFile")
    store_file_param = model_factory.create_parameter("file", file_content_type)
    store_file_op.parameters.append(store_file_param)
    ifile_storage.contents.append(store_file_op)
    
    repository.contents.append(ifile_storage)
    
    # 2. IDownload interface
    idownload = model_factory.create_domain_interface("IDownload")
    
    download_op = model_factory.create_operation_signature("download")
    download_param = model_factory.create_parameter("audioRequest", audio_collection_request_type)
    download_op.parameters.append(download_param)
    download_op._return = audio_collection_request_type
    idownload.contents.append(download_op)
    
    repository.contents.append(idownload)
    
    # 3. IMediaAccess interface
    imedia_access = model_factory.create_domain_interface("IMediaAccess")
    
    upload_op = model_factory.create_operation_signature("upload")
    upload_param = model_factory.create_parameter("file", file_content_type)
    upload_op.parameters.append(upload_param)
    imedia_access.contents.append(upload_op)
    
    get_file_list_op = model_factory.create_operation_signature("getFileList")
    imedia_access.contents.append(get_file_list_op)
    
    repository.contents.append(imedia_access)
    
    # 4. IPackaging interface
    ipackaging = model_factory.create_domain_interface("IPackaging")
    
    zip_op = model_factory.create_operation_signature("zip")
    zip_param = model_factory.create_parameter("audios", audio_collection_request_type)
    zip_op.parameters.append(zip_param)
    zip_op._return = file_content_type
    ipackaging.contents.append(zip_op)
    
    repository.contents.append(ipackaging)
    
    # 5. IMediaManagement interface
    imedia_management = model_factory.create_domain_interface("IMediaManagement")
    
    mgmt_upload_op = model_factory.create_operation_signature("upload")
    mgmt_upload_param = model_factory.create_parameter("file", file_content_type)
    mgmt_upload_op.parameters.append(mgmt_upload_param)
    imedia_management.contents.append(mgmt_upload_op)
    
    mgmt_download_op = model_factory.create_operation_signature("download")
    mgmt_download_param = model_factory.create_parameter("audioRequest", audio_collection_request_type)
    mgmt_download_op.parameters.append(mgmt_download_param)
    imedia_management.contents.append(mgmt_download_op)
    
    mgmt_get_file_list_op = model_factory.create_operation_signature("getFileList")
    imedia_management.contents.append(mgmt_get_file_list_op)
    
    repository.contents.append(imedia_management)
    
    # Get standard resource interfaces
    icpu = std_defs.get_element("icpu")
    ihdd = std_defs.get_element("ihdd")
    
    # Get standard operations for resources
    process_op = std_defs.get_element("process_op")
    read_op = std_defs.get_element("read_op")
    
    # Components
    # 1. FileStorage component
    file_storage = model_factory.create_component("FileStorage")
    
    # Roles
    fs_provided_role = model_factory.create_provided_role("store", ifile_storage)
    file_storage.contents.append(fs_provided_role)
    
    fs_cpu_role = model_factory.create_required_role("cpu", icpu)
    file_storage.contents.append(fs_cpu_role)
    
    fs_hdd_role = model_factory.create_required_role("hdd", ihdd)
    file_storage.contents.append(fs_hdd_role)
    
    # SEFFs
    # getFiles SEFF
    get_files_seff = model_factory.create_seff(fs_provided_role, get_files_op)
    
    # CPU processing with parameter reference - using actual expression string
    get_files_cpu_param = model_factory.create_parameter_specification("audioRequest.Count.VALUE*75182981.91")
    get_files_cpu_action = model_factory.create_seff_call_action(
        fs_cpu_role, process_op, [get_files_cpu_param]
    )
    get_files_seff.contents.append(get_files_cpu_action)
    
    # HDD read action with parameter reference
    get_files_hdd_param = model_factory.create_parameter_specification("audioRequest.Size.VALUE * audioRequest.Count.VALUE")
    get_files_hdd_action = model_factory.create_seff_call_action(
        fs_hdd_role, read_op, [get_files_hdd_param]
    )
    get_files_seff.contents.append(get_files_hdd_action)
    
    file_storage.contents.append(get_files_seff)
    
    # storeFile SEFF
    store_file_seff = model_factory.create_seff(fs_provided_role, store_file_op)
    
    # Use a double literal with the exact value from MediaStore.tpcm
    store_file_cpu_expr = expr_factory.create_double_literal(75182981.91)
    store_file_cpu_param = model_factory.create_parameter_specification(store_file_cpu_expr)
    store_file_cpu_action = model_factory.create_seff_call_action(
        fs_cpu_role, process_op, [store_file_cpu_param]
    )
    store_file_seff.contents.append(store_file_cpu_action)
    
    file_storage.contents.append(store_file_seff)
    repository.contents.append(file_storage)
    
    # 2. Packaging component
    packaging = model_factory.create_component("Packaging")
    
    # Roles
    pkg_provided_role = model_factory.create_provided_role("packaging", ipackaging)
    packaging.contents.append(pkg_provided_role)
    
    pkg_cpu_role = model_factory.create_required_role("cpu", icpu)
    packaging.contents.append(pkg_cpu_role)
    
    # SEFFs
    # zip SEFF
    zip_seff = model_factory.create_seff(pkg_provided_role, zip_op)
    
    # First CPU processing with PDF - using string directly
    zip_cpu_pdf_param = model_factory.create_parameter_specification("DoublePDF[(21;0.1)(13;0.9)]")
    zip_cpu_pdf_action = model_factory.create_seff_call_action(
        pkg_cpu_role, process_op, [zip_cpu_pdf_param]
    )
    zip_seff.contents.append(zip_cpu_pdf_action)
    
    # Second CPU processing with bytesize
    zip_cpu_bytesize_param = model_factory.create_parameter_specification("1.0512 * audios.BYTESIZE")
    zip_cpu_bytesize_action = model_factory.create_seff_call_action(
        pkg_cpu_role, process_op, [zip_cpu_bytesize_param]
    )
    zip_seff.contents.append(zip_cpu_bytesize_action)
    
    packaging.contents.append(zip_seff)
    repository.contents.append(packaging)
    
    # 3. MediaAccess component
    media_access = model_factory.create_component("MediaAccess")
    
    # Roles
    ma_access_role = model_factory.create_provided_role("access", imedia_access)
    media_access.contents.append(ma_access_role)
    
    ma_download_role = model_factory.create_provided_role("download", idownload)
    media_access.contents.append(ma_download_role)
    
    ma_storage_role = model_factory.create_required_role("storage", ifile_storage)
    media_access.contents.append(ma_storage_role)
    
    ma_cpu_role = model_factory.create_required_role("cpu", icpu)
    media_access.contents.append(ma_cpu_role)
    
    # SEFFs
    # upload SEFF
    upload_seff = model_factory.create_seff(ma_access_role, upload_op)
    
    # CPU processing with PDF
    upload_cpu_param = model_factory.create_parameter_specification("DoublePDF[(15;0.2)(33;0.8)]")
    upload_cpu_action = model_factory.create_seff_call_action(
        ma_cpu_role, process_op, [upload_cpu_param]
    )
    upload_seff.contents.append(upload_cpu_action)
    
    # External call to storeFile
    upload_store_param = model_factory.create_parameter_specification("file.BYTESIZE")
    upload_store_action = model_factory.create_external_call_action(
        ma_storage_role, store_file_op, [upload_store_param]
    )
    upload_seff.contents.append(upload_store_action)
    
    media_access.contents.append(upload_seff)
    
    # getFileList SEFF
    get_file_list_seff = model_factory.create_seff(ma_access_role, get_file_list_op)
    
    # CPU processing with PDF
    get_file_list_cpu_param = model_factory.create_parameter_specification("DoublePDF[(28;0.3)(19;0.7)]")
    get_file_list_cpu_action = model_factory.create_seff_call_action(
        ma_cpu_role, process_op, [get_file_list_cpu_param]
    )
    get_file_list_seff.contents.append(get_file_list_cpu_action)
    
    media_access.contents.append(get_file_list_seff)
    
    # download.download SEFF
    download_seff = model_factory.create_seff(ma_download_role, download_op)
    
    # CPU processing with PDF
    download_cpu_param = model_factory.create_parameter_specification("DoublePDF[(55;0.5)(30;0.5)]")
    download_cpu_action = model_factory.create_seff_call_action(
        ma_cpu_role, process_op, [download_cpu_param]
    )
    download_seff.contents.append(download_cpu_action)
    
    # External call to getFiles
    download_get_files_param = model_factory.create_parameter_specification("audioRequest.Count.VALUE")
    download_get_files_size_param = model_factory.create_parameter_specification("audioRequest.Size.VALUE")
    
    download_get_files_action = model_factory.create_external_call_action(
        ma_storage_role, get_files_op, [download_get_files_param, download_get_files_size_param]
    )
    download_seff.contents.append(download_get_files_action)
    
    media_access.contents.append(download_seff)
    repository.contents.append(media_access)
    
    # 4. MediaManagement component
    media_management = model_factory.create_component("MediaManagement")
    
    # Roles
    mm_cpu_role = model_factory.create_required_role("cpu", icpu)
    media_management.contents.append(mm_cpu_role)
    
    mm_management_role = model_factory.create_provided_role("management", imedia_management)
    media_management.contents.append(mm_management_role)
    
    mm_download_role = model_factory.create_required_role("download", idownload)
    media_management.contents.append(mm_download_role)
    
    mm_packaging_role = model_factory.create_required_role("packaging", ipackaging)
    media_management.contents.append(mm_packaging_role)
    
    mm_access_role = model_factory.create_required_role("access", imedia_access)
    media_management.contents.append(mm_access_role)
    
    # SEFFs
    # upload SEFF
    mm_upload_seff = model_factory.create_seff(mm_management_role, mgmt_upload_op)
    
    # CPU processing with PDF
    mm_upload_cpu_param = model_factory.create_parameter_specification("DoublePDF[(10;0.7)(30;0.3)]")
    mm_upload_cpu_action = model_factory.create_seff_call_action(
        mm_cpu_role, process_op, [mm_upload_cpu_param]
    )
    mm_upload_seff.contents.append(mm_upload_cpu_action)
    
    # External call to access.upload
    mm_upload_access_param = model_factory.create_parameter_specification("file.BYTESIZE")
    mm_upload_access_action = model_factory.create_external_call_action(
        mm_access_role, upload_op, [mm_upload_access_param]
    )
    mm_upload_seff.contents.append(mm_upload_access_action)
    
    media_management.contents.append(mm_upload_seff)
    
    # download SEFF
    mm_download_seff = model_factory.create_seff(mm_management_role, mgmt_download_op)
    
    # CPU processing with PDF
    mm_download_cpu_param = model_factory.create_parameter_specification("DoublePDF[(90;0.2)(89;0.8)]")
    mm_download_cpu_action = model_factory.create_seff_call_action(
        mm_cpu_role, process_op, [mm_download_cpu_param]
    )
    mm_download_seff.contents.append(mm_download_cpu_action)
    
    # External call to download.download
    mm_download_down_count_param = model_factory.create_parameter_specification("audioRequest.Count.VALUE")
    mm_download_down_size_param = model_factory.create_parameter_specification("audioRequest.Size.VALUE")
    
    mm_download_down_action = model_factory.create_external_call_action(
        mm_download_role, download_op, [mm_download_down_count_param, mm_download_down_size_param]
    )
    mm_download_seff.contents.append(mm_download_down_action)
    
    media_management.contents.append(mm_download_seff)
    
    # getFileList SEFF
    mm_get_file_list_seff = model_factory.create_seff(mm_management_role, mgmt_get_file_list_op)
    
    # CPU processing with PDF
    mm_get_file_list_cpu_param = model_factory.create_parameter_specification("DoublePDF[(59;0.3)(13;0.7)]")
    mm_get_file_list_cpu_action = model_factory.create_seff_call_action(
        mm_cpu_role, process_op, [mm_get_file_list_cpu_param]
    )
    mm_get_file_list_seff.contents.append(mm_get_file_list_cpu_action)
    
    # External call to access.getFileList
    mm_get_file_list_access_action = model_factory.create_external_call_action(
        mm_access_role, get_file_list_op, []
    )
    mm_get_file_list_seff.contents.append(mm_get_file_list_access_action)
    
    media_management.contents.append(mm_get_file_list_seff)
    repository.contents.append(media_management)
    
    # Add repository to model
    model.fragments.append(repository)
    
    # Save the model
    save_model(model, output_file, rset)
    
    print(f"MediaStore model created successfully: {output_file}")
    return model


# Main functionality moved to main.py