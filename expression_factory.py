from pyecore.resources import ResourceSet, URI
from pyecore.utils import DynamicEPackage

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
        
        # Ensure ProbabilityFunction and Units metamodels are loaded
        prob_resource = self.rset.get_resource(URI("ecores/ProbabilityFunction.ecore"))
        prob_metamodel = prob_resource.contents[0]
        self.rset.metamodel_registry[prob_metamodel.nsURI] = prob_metamodel
        self.prob = DynamicEPackage(prob_metamodel)
        
        units_resource = self.rset.get_resource(URI("ecores/Units.ecore"))
        units_metamodel = units_resource.contents[0]
        self.rset.metamodel_registry[units_metamodel.nsURI] = units_metamodel
        self.units = DynamicEPackage(units_metamodel)
    
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
    
    # === Probability Functions ===
    
    def create_exp_distribution(self, rate):
        """Create an exponential distribution.
        
        Args:
            rate: Rate parameter (lambda)
            
        Returns:
            A new ProbabilityFunctionLiteral containing an ExponentialDistribution
        """
        exp_dist = self.prob.ExponentialDistribution()
        exp_dist.rate = rate
        
        func = self.stoex.ProbabilityFunctionLiteral()
        func.function_ProbabilityFunctionLiteral = exp_dist
        return func
    
    def create_normal_distribution(self, mean, standard_deviation):
        """Create a normal distribution.
        
        Args:
            mean: Mean value
            standard_deviation: Standard deviation
            
        Returns:
            A new ProbabilityFunctionLiteral containing a NormalDistribution
        """
        normal_dist = self.prob.NormalDistribution()
        normal_dist.mu = mean
        normal_dist.sigma = standard_deviation
        
        func = self.stoex.ProbabilityFunctionLiteral()
        func.function_ProbabilityFunctionLiteral = normal_dist
        return func
    
    def create_uniform_distribution(self, lower, upper):
        """Create a uniform distribution.
        
        Args:
            lower: Lower bound
            upper: Upper bound
            
        Returns:
            A new ProbabilityFunctionLiteral containing a UniformDistribution
        """
        uniform_dist = self.prob.UniformDistribution()
        uniform_dist.lowerBound = lower
        uniform_dist.upperBound = upper
        
        func = self.stoex.ProbabilityFunctionLiteral()
        func.function_ProbabilityFunctionLiteral = uniform_dist
        return func