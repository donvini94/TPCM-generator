from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage
from .probability_factory import ProbabilityFactory

class ExpressionFactory:
    """Factory class for creating stochastic expressions (stoex)."""
    
    def __init__(self, rset=None):
        """Initialize the factory with a resource set.
        
        Args:
            rset: Optional existing ResourceSet
        """
        self.rset = rset if rset is not None else ResourceSet()
        
        # Load the stoex metamodel
        stoex_resource = self.rset.get_resource(URI("ecores/stoex.ecore"))
        stoex_metamodel = stoex_resource.contents[0]
        self.rset.metamodel_registry[stoex_metamodel.nsURI] = stoex_metamodel
        self.stoex = DynamicEPackage(stoex_metamodel)
        
        # Initialize ProbabilityFactory and keep direct references to metamodels
        self.prob_factory = ProbabilityFactory(self.rset)
        self.prob = self.prob_factory.prob
        self.units = self.prob_factory.units
    
    # === Literals ===
    
    def create_int_literal(self, value):
        """Create an integer literal.
        
        Args:
            value: Integer value
            
        Returns:
            A new IntLiteral
        """
        return self.stoex.IntLiteral(value=value)
    
    def create_double_literal(self, value):
        """Create a double literal.
        
        Args:
            value: Double value
            
        Returns:
            A new DoubleLiteral
        """
        return self.stoex.DoubleLiteral(value=value)
    
    def create_bool_literal(self, value):
        """Create a boolean literal.
        
        Args:
            value: Boolean value
            
        Returns:
            A new BoolLiteral
        """
        return self.stoex.BoolLiteral(value=value)
    
    def create_string_literal(self, value):
        """Create a string literal.
        
        Args:
            value: String value
            
        Returns:
            A new StringLiteral
        """
        return self.stoex.StringLiteral(value=value)
    
    # === Variables and References ===
    
    def create_variable_reference(self, name):
        """Create a variable reference.
        
        Args:
            name: Name of the variable
            
        Returns:
            A new VariableReference
        """
        return self.stoex.VariableReference(referenceName=name)
    
    def create_variable(self, name):
        """Create a variable.
        
        Args:
            name: Name of the variable
            
        Returns:
            A new Variable
        """
        var = self.stoex.Variable()
        var.id_Variable = self.create_variable_reference(name)
        return var
    
    def create_namespace_reference(self, namespace, inner_reference):
        """Create a namespace reference.
        
        Args:
            namespace: Namespace name
            inner_reference: Inner reference (AbstractNamedReference)
            
        Returns:
            A new NamespaceReference
        """
        ref = self.stoex.NamespaceReference(referenceName=namespace)
        ref.innerReference_NamespaceReference = inner_reference
        return ref
    
    # === Expressions ===
    
    def create_parenthesis(self, inner_expression):
        """Create a parenthesis expression.
        
        Args:
            inner_expression: Expression inside parentheses
            
        Returns:
            A new Parenthesis
        """
        paren = self.stoex.Parenthesis()
        paren.innerExpression = inner_expression
        return paren
    
    def create_term_expression(self, left, right, operation):
        """Create a term expression (addition or subtraction).
        
        Args:
            left: Left side expression
            right: Right side expression
            operation: TermOperations value (ADD or SUB)
            
        Returns:
            A new TermExpression
        """
        expr = self.stoex.TermExpression()
        expr.left = left
        expr.right = right
        expr.operation = operation
        return expr
    
    def create_product_expression(self, left, right, operation):
        """Create a product expression (multiplication, division, or modulo).
        
        Args:
            left: Left side expression
            right: Right side expression
            operation: ProductOperations value (MULT, DIV, or MOD)
            
        Returns:
            A new ProductExpression
        """
        expr = self.stoex.ProductExpression()
        expr.left = left
        expr.right = right
        expr.operation = operation
        return expr
    
    def create_power_expression(self, base, exponent):
        """Create a power expression.
        
        Args:
            base: Base expression
            exponent: Exponent expression
            
        Returns:
            A new PowerExpression
        """
        expr = self.stoex.PowerExpression()
        expr.base = base
        expr.exponent = exponent
        return expr
    
    def create_compare_expression(self, left, right, operation):
        """Create a comparison expression.
        
        Args:
            left: Left side expression
            right: Right side expression
            operation: CompareOperations value
            
        Returns:
            A new CompareExpression
        """
        expr = self.stoex.CompareExpression()
        expr.left = left
        expr.right = right
        expr.operation = operation
        return expr
    
    def create_boolean_expression(self, left, right, operation):
        """Create a boolean expression.
        
        Args:
            left: Left side expression
            right: Right side expression
            operation: BooleanOperations value (AND, OR, XOR)
            
        Returns:
            A new BooleanOperatorExpression
        """
        expr = self.stoex.BooleanOperatorExpression()
        expr.left = left
        expr.right = right
        expr.operation = operation
        return expr
    
    def create_not_expression(self, inner):
        """Create a logical NOT expression.
        
        Args:
            inner: Expression to negate
            
        Returns:
            A new NotExpression
        """
        expr = self.stoex.NotExpression()
        expr.inner = inner
        return expr
    
    def create_negative_expression(self, inner):
        """Create a numeric negative expression.
        
        Args:
            inner: Expression to negate
            
        Returns:
            A new NegativeExpression
        """
        expr = self.stoex.NegativeExpression()
        expr.inner = inner
        return expr
    
    def create_if_else_expression(self, condition, if_expr, else_expr):
        """Create an if-else expression.
        
        Args:
            condition: Condition expression
            if_expr: Expression to evaluate if condition is true
            else_expr: Expression to evaluate if condition is false
            
        Returns:
            A new IfElseExpression
        """
        expr = self.stoex.IfElseExpression()
        expr.conditionExpression = condition
        expr.ifExpression = if_expr
        expr.elseExpression = else_expr
        return expr
        
    def create_random_variable(self, specification_string):
        """Create a random variable with a specification string.
        
        Args:
            specification_string: String representation of the stochastic expression
            
        Returns:
            A new RandomVariable instance
        """
        return self.stoex.RandomVariable(specification=specification_string)

    # === Probability Functions ===
    
    def create_probability_function_literal(self, function):
        """Create a probability function literal.
        
        Args:
            function: A probability function instance
            
        Returns:
            A new ProbabilityFunctionLiteral
        """
        func = self.stoex.ProbabilityFunctionLiteral()
        func.function_ProbabilityFunctionLiteral = function
        return func
    
    def create_exp_distribution(self, rate, unit=None):
        """Create an exponential distribution.
        
        Args:
            rate: Rate parameter (lambda)
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing an ExponentialDistribution
        """
        exp_dist = self.prob_factory.create_exponential_distribution(rate, unit)
        return self.create_probability_function_literal(exp_dist)
    
    def create_normal_distribution(self, mean, standard_deviation, unit=None):
        """Create a normal distribution.
        
        Args:
            mean: Mean value
            standard_deviation: Standard deviation
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a NormalDistribution
        """
        normal_dist = self.prob_factory.create_normal_distribution(mean, standard_deviation, unit)
        return self.create_probability_function_literal(normal_dist)
    
    def create_lognormal_distribution(self, mu, sigma, unit=None):
        """Create a lognormal distribution.
        
        Args:
            mu: Scale parameter (mu)
            sigma: Shape parameter (sigma)
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a LognormalDistribution
        """
        lognormal_dist = self.prob_factory.create_lognormal_distribution(mu, sigma, unit)
        return self.create_probability_function_literal(lognormal_dist)
    
    def create_gamma_distribution(self, alpha, theta, unit=None):
        """Create a gamma distribution.
        
        Args:
            alpha: Shape parameter (alpha)
            theta: Scale parameter (theta)
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a GammaDistribution
        """
        gamma_dist = self.prob_factory.create_gamma_distribution(alpha, theta, unit)
        return self.create_probability_function_literal(gamma_dist)
    
    def create_int_pmf_distribution(self, samples, unit=None):
        """Create an integer probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is an int
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a ProbabilityMassFunction
        """
        pmf = self.prob_factory.create_int_pmf(samples)
        if unit:
            pmf.unit = unit
        return self.create_probability_function_literal(pmf)
    
    def create_double_pmf_distribution(self, samples, unit=None):
        """Create a double probability mass function.
        
        Args:
            samples: List of (value, probability) tuples where value is a float
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a ProbabilityMassFunction
        """
        pmf = self.prob_factory.create_double_pmf(samples)
        if unit:
            pmf.unit = unit
        return self.create_probability_function_literal(pmf)
    
    def create_boxed_pdf_distribution(self, samples, unit=None):
        """Create a boxed probability density function.
        
        Args:
            samples: List of (value, probability) tuples
            unit: Optional unit for the distribution
            
        Returns:
            A new ProbabilityFunctionLiteral containing a BoxedPDF
        """
        pdf = self.prob_factory.create_boxed_pdf(samples, unit)
        return self.create_probability_function_literal(pdf)
        
    def create_function_literal(self, function_id, parameters=None):
        """Create a function literal expression.
        
        Args:
            function_id: The function identifier/name
            parameters: List of parameters (Expression objects)
            
        Returns:
            A new FunctionLiteral
        """
        func = self.stoex.FunctionLiteral(id=function_id)
        if parameters:
            for param in parameters:
                func.parameters_FunctionLiteral.append(param)
        return func
