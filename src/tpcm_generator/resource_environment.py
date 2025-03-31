from pyecore.ecore import EObject
from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage


def get_resource_environment(resource_set=None, ecore_path="ecores/TPCM.ecore"):
    """Get or create the resource environment model fragment.

    Args:
        resource_set: Optional existing ResourceSet to use
        ecore_path: Path to the TPCM.ecore file

    Returns:
        The ResourceEnvironmentGenerator instance
    """
    return _ResourceEnvironmentGenerator(resource_set, ecore_path)


class _ResourceEnvironmentGenerator:
    """Class for generating the resource environment model fragment."""

    def __init__(self, resource_set=None, ecore_path="ecores/TPCM.ecore"):
        """Initialize with the metamodel and prepare resource environment.

        Args:
            resource_set: Optional existing ResourceSet to use
            ecore_path: Path to the TPCM.ecore file
        """
        # Use provided ResourceSet or create new one
        self.rset = resource_set if resource_set is not None else ResourceSet()

        # Load metamodel if needed
        if ecore_path not in self.rset.resources:
            tpcm_resource = self.rset.get_resource(URI(ecore_path))
            tpcm_metamodel = tpcm_resource.contents[0]
            self.rset.metamodel_registry[tpcm_metamodel.nsURI] = tpcm_metamodel
            self._PCM = DynamicEPackage(tpcm_metamodel)
        else:
            # Use existing metamodel from the resource set
            tpcm_resource = self.rset.get_resource(URI(ecore_path))
            tpcm_metamodel = tpcm_resource.contents[0]
            self._PCM = DynamicEPackage(tpcm_metamodel)

        # Load stoex metamodel if needed
        stoex_uri = URI("ecores/stoex.ecore")
        stoex_resource = self.rset.get_resource(stoex_uri)
        stoex_metamodel = stoex_resource.contents[0]
        self.rset.metamodel_registry[stoex_metamodel.nsURI] = stoex_metamodel
        self._STOEX = DynamicEPackage(stoex_metamodel)

        # Resource environment instance
        self._resource_env = None

        # Initialize resource environment
        self._initialize_resource_environment()

    def _create_double_literal(self, value):
        """Create a DoubleLiteral expression.

        Args:
            value: The numeric value (will be converted to float)

        Returns:
            A DoubleLiteral expression
        """
        double_literal = self._STOEX.DoubleLiteral()
        # Explicitly convert to float to satisfy PyEcore type checking
        double_literal.value = float(value)
        return double_literal

    def _create_normal_distribution(self, mean, stddev):
        """Create a RandomVariable with a normal distribution specification.

        Since we don't have direct access to the ProbabilityFunction.ecore model,
        we'll create a RandomVariable with the appropriate string specification.

        Args:
            mean: Mean value of the distribution
            stddev: Standard deviation of the distribution

        Returns:
            A RandomVariable with normal distribution specification
        """
        # Create a RandomVariable with the normal distribution as a string specification
        random_var = self._STOEX.RandomVariable()
        random_var.specification = f"Norm({mean},{stddev})"

        return random_var

    def _initialize_resource_environment(self):
        """Initialize the resource environment based on the specification."""
        # Import standard definitions
        from .std_definitions import get_std_definitions

        std_defs = get_std_definitions(self.rset)

        # Create resource environment fragment
        self._resource_env = self._PCM.ResourceEnvironment(name="Environment")

        # Get required element references
        cpu_resource = std_defs.get_element("cpu_resource")
        hdd_resource = std_defs.get_element("hdd_resource")
        ps_entity = std_defs.get_element("ps_entity")
        fcfs_entity = std_defs.get_element("fcfs_entity")
        ethernet = std_defs.get_element("ethernet")

        # === Create ApplicationServer container ===
        app_server = self._PCM.ResourceContainer(name="ApplicationServer")

        # Create ApplicationServer CPU
        app_cpu = self._PCM.ProcessingResource(name="CPU")
        app_cpu.type = cpu_resource

        # Initialize CPU properties
        app_cpu_init = self._PCM.Initialization()

        # Processing rate initializer
        app_cpu_rate = self._PCM.PropertyInitializer()
        app_cpu_rate.property = cpu_resource.definitions[0]  # processingRate
        app_cpu_rate.specification = self._create_double_literal(1000 * 1000 * 1000)
        app_cpu_init.contents.append(app_cpu_rate)

        # Scheduling policy initializer
        app_cpu_sched = self._PCM.PropertyInitializer()
        app_cpu_sched.property = cpu_resource.definitions[1]  # schedulingPolicy
        app_cpu_sched.referencedElement = ps_entity
        app_cpu_init.contents.append(app_cpu_sched)

        app_cpu.initialization = app_cpu_init

        #        # Create ApplicationServer HDD
        #        app_hdd = self._PCM.ProcessingResource(name="HDD")
        #        app_hdd.type = hdd_resource
        #
        #        # Initialize HDD properties
        #        app_hdd_init = self._PCM.Initialization()
        #
        #        # Processing rate initializer
        #        app_hdd_rate = self._PCM.PropertyInitializer()
        #        app_hdd_rate.property = hdd_resource.definitions[0]  # processingRate
        #        app_hdd_rate.specification = self._create_double_literal(50 * 1000 * 1000)
        #        app_hdd_init.contents.append(app_hdd_rate)
        #
        #        # Scheduling policy initializer
        #        app_hdd_sched = self._PCM.PropertyInitializer()
        #        app_hdd_sched.property = hdd_resource.definitions[1]  # schedulingPolicy
        #        app_hdd_sched.referencedElement = fcfs_entity
        #        app_hdd_init.contents.append(app_hdd_sched)
        #
        #        app_hdd.initialization = app_hdd_init

        # Add resources to ApplicationServer
        app_server.contents.extend([app_cpu])

        #        # === Create DatabaseServer container ===
        #        db_server = self._PCM.ResourceContainer(name="DatabaseServer")
        #
        #        # Create DatabaseServer CPU
        #        db_cpu = self._PCM.ProcessingResource(name="CPU")
        #        db_cpu.type = cpu_resource
        #
        #        # Initialize CPU properties
        #        db_cpu_init = self._PCM.Initialization()
        #
        #        # Processing rate initializer
        #        db_cpu_rate = self._PCM.PropertyInitializer()
        #        db_cpu_rate.property = cpu_resource.definitions[0]  # processingRate
        #        db_cpu_rate.specification = self._create_double_literal(1000 * 1000 * 1000)
        #        db_cpu_init.contents.append(db_cpu_rate)
        #
        #        # Scheduling policy initializer
        #        db_cpu_sched = self._PCM.PropertyInitializer()
        #        db_cpu_sched.property = cpu_resource.definitions[1]  # schedulingPolicy
        #        db_cpu_sched.referencedElement = ps_entity
        #        db_cpu_init.contents.append(db_cpu_sched)
        #
        #        db_cpu.initialization = db_cpu_init
        #
        #        # Create DatabaseServer HDD
        #        db_hdd = self._PCM.ProcessingResource(name="HDD")
        #        db_hdd.type = hdd_resource
        #
        #        # Initialize HDD properties
        #        db_hdd_init = self._PCM.Initialization()
        #
        #        # Processing rate initializer
        #        db_hdd_rate = self._PCM.PropertyInitializer()
        #        db_hdd_rate.property = hdd_resource.definitions[0]  # processingRate
        #        db_hdd_rate.specification = self._create_double_literal(600 * 1000 * 1000)
        #        db_hdd_init.contents.append(db_hdd_rate)
        #
        #        # Scheduling policy initializer
        #        db_hdd_sched = self._PCM.PropertyInitializer()
        #        db_hdd_sched.property = hdd_resource.definitions[1]  # schedulingPolicy
        #        db_hdd_sched.referencedElement = fcfs_entity
        #        db_hdd_init.contents.append(db_hdd_sched)
        #
        #        db_hdd.initialization = db_hdd_init
        #
        #        # Add resources to DatabaseServer
        #        db_server.contents.extend([db_cpu, db_hdd])
        #
        #        # === Create LAN link ===
        #        lan = self._PCM.LinkingResource(name="LAN")
        #        lan.type = ethernet
        #
        #        # Initialize LAN properties
        #        lan_init = self._PCM.Initialization()
        #
        #        # Latency initializer - using normal distribution Norm(0.07, 0.03)
        #        lan_latency = self._PCM.PropertyInitializer()
        #        lan_latency.property = ethernet.definitions[1]  # latency
        #        # For simplicity in this iteration, use a double literal with the mean value
        #        # since the normal distribution requires more complex setup
        #        lan_latency.specification = self._create_double_literal(0.07)
        #        lan_init.contents.append(lan_latency)
        #
        #        # Throughput initializer
        #        lan_throughput = self._PCM.PropertyInitializer()
        #        lan_throughput.property = ethernet.definitions[0]  # throughput
        #        lan_throughput.specification = self._create_double_literal(6.25 * 1000 * 1000)
        #        lan_init.contents.append(lan_throughput)
        #
        #        lan.initialization = lan_init
        #
        #        # Connect the containers
        #        lan.connected.extend([app_server, db_server])

        # Add all elements to the resource environment
        self._resource_env.contents.extend([app_server])

    def add_to_model(self, model):
        """Add the resource environment to an existing model.

        Args:
            model: The PCM model to add the resource environment to

        Returns:
            The model with resource environment added
        """
        model.fragments.append(self._resource_env)
        return model

    def get_resource_containers(self):
        """Get the resource containers from the resource environment.

        Returns:
            List of resource containers
        """
        # Return the resource containers present in the resource environment
        return [
            content
            for content in self._resource_env.contents
            if hasattr(content, "eClass") and content.eClass.name == "ResourceContainer"
        ]
