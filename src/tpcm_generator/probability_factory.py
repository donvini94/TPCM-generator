from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage

class ProbabilityFactory:
    """Factory class for creating probability functions."""
    
    def __init__(self, rset=None):
        """Initialize the factory with a resource set.
        
        Args:
            rset: Optional existing ResourceSet
        """
        self.rset = rset if rset is not None else ResourceSet()
        
        # Load the ProbabilityFunction metamodel
        prob_resource = self.rset.get_resource(URI("ecores/ProbabilityFunction.ecore"))
        prob_metamodel = prob_resource.contents[0]
        self.rset.metamodel_registry[prob_metamodel.nsURI] = prob_metamodel
        self.prob = DynamicEPackage(prob_metamodel)
        
        # Load the Units metamodel
        units_resource = self.rset.get_resource(URI("ecores/Units.ecore"))
        units_metamodel = units_resource.contents[0]
        self.rset.metamodel_registry[units_metamodel.nsURI] = units_metamodel
        self.units = DynamicEPackage(units_metamodel)
    
    def create_base_unit(self, name):
        """Create a base unit.
        
        Args:
            name: Unit name from UnitNames enum
            
        Returns:
            A new BaseUnit instance
        """
        return self.units.BaseUnit(name=name)
    
    # === Probability Mass Functions ===
    
    def create_int_pmf(self, samples):
        """Create an integer probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is an int
            
        Returns:
            A new ProbabilityMassFunction instance
        """
        pmf = self.prob.ProbabilityMassFunction()
        pmf.orderedDomain = True
        
        # Create and add samples
        for value, probability in samples:
            sample = self.prob.IntSample()
            sample.value = value
            sample.probability = probability
            pmf.samples.append(sample)
            
        return pmf
        
    def create_double_pmf(self, samples):
        """Create a double probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is a float
            
        Returns:
            A new ProbabilityMassFunction instance
        """
        pmf = self.prob.ProbabilityMassFunction()
        pmf.orderedDomain = True
        
        # Create and add samples
        for value, probability in samples:
            sample = self.prob.DoubleSample()
            sample.value = value
            sample.probability = probability
            pmf.samples.append(sample)
            
        return pmf
        
    def create_bool_pmf(self, samples):
        """Create a boolean probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is a boolean
            
        Returns:
            A new ProbabilityMassFunction instance
        """
        pmf = self.prob.ProbabilityMassFunction()
        pmf.orderedDomain = True
        
        # Create and add samples
        for value, probability in samples:
            sample = self.prob.BoolSample()
            sample.value = value
            sample.probability = probability
            pmf.samples.append(sample)
            
        return pmf
        
    def create_string_pmf(self, samples):
        """Create a string probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is a string
            
        Returns:
            A new ProbabilityMassFunction instance
        """
        pmf = self.prob.ProbabilityMassFunction()
        pmf.orderedDomain = False
        
        # Create and add samples
        for value, probability in samples:
            sample = self.prob.StringSample()
            sample.value = value
            sample.probability = probability
            pmf.samples.append(sample)
            
        return pmf
    
    # === Probability Density Functions ===
    
    def create_normal_distribution(self, mu, sigma, unit=None):
        """Create a normal distribution.
        
        Args:
            mu: Mean (mu parameter)
            sigma: Standard deviation (sigma parameter)
            unit: Optional unit for the distribution
            
        Returns:
            A new NormalDistribution instance
        """
        dist = self.prob.NormalDistribution(mu=mu, sigma=sigma)
        if unit:
            dist.unit = unit
        return dist
        
    def create_exponential_distribution(self, rate, unit=None):
        """Create an exponential distribution.
        
        Args:
            rate: Rate parameter (lambda)
            unit: Optional unit for the distribution
            
        Returns:
            A new ExponentialDistribution instance
        """
        dist = self.prob.ExponentialDistribution(rate=rate)
        if unit:
            dist.unit = unit
        return dist
        
    def create_lognormal_distribution(self, mu, sigma, unit=None):
        """Create a lognormal distribution.
        
        Args:
            mu: Scale parameter (mu)
            sigma: Shape parameter (sigma)
            unit: Optional unit for the distribution
            
        Returns:
            A new LognormalDistribution instance
        """
        dist = self.prob.LognormalDistribution(mu=mu, sigma=sigma)
        if unit:
            dist.unit = unit
        return dist
        
    def create_gamma_distribution(self, alpha, theta, unit=None):
        """Create a gamma distribution.
        
        Args:
            alpha: Shape parameter (alpha)
            theta: Scale parameter (theta)
            unit: Optional unit for the distribution
            
        Returns:
            A new GammaDistribution instance
        """
        dist = self.prob.GammaDistribution(alpha=alpha, theta=theta)
        if unit:
            dist.unit = unit
        return dist
    
    # === Boxed PDF (for custom probability density functions) ===
    
    def create_boxed_pdf(self, samples, unit=None):
        """Create a boxed probability density function.
        
        Args:
            samples: List of (value, probability) tuples
            unit: Optional unit for the distribution
            
        Returns:
            A new BoxedPDF instance
        """
        pdf = self.prob.BoxedPDF()
        
        # Create and add samples
        for value, probability in samples:
            sample = self.prob.ContinuousSample(value=value, probability=probability)
            pdf.samples.append(sample)
            
        if unit:
            pdf.unit = unit
        return pdf