import os
from model_factory import ModelFactory
from expression_factory import ExpressionFactory
from utils import save_model
from std_definitions import get_std_definitions

def test_create_minimal_repository():
    """Test creating a minimal repository model."""
    # Initialize factories
    model_factory = ModelFactory()
    expr_factory = ExpressionFactory(model_factory.rset)
    
    # Get standard definitions
    std_defs = get_std_definitions(model_factory.rset)
    
    # Create model with repository
    model = model_factory.create_model()
    std_defs.add_to_model(model)
    
    # Create a simple repository with one component and interface
    repository = model_factory.create_repository("TestRepository")
    
    # Create a primitive datatype
    int_type = model_factory.create_primitive_datatype(
        "TestInt", model_factory.PCM.PrimitiveTypeEnum.INT
    )
    repository.contents.append(int_type)
    
    # Create an interface with one operation
    interface = model_factory.create_interface("TestInterface")
    operation = model_factory.create_operation_signature("doSomething")
    param = model_factory.create_parameter("input", int_type)
    operation.parameters.append(param)
    # Set return type (using attribute name that doesn't conflict with Python keyword)
    setattr(operation, "return", int_type)
    interface.contents.append(operation)
    repository.contents.append(interface)
    
    # Create a component that provides the interface
    component = model_factory.create_component("TestComponent")
    provided_role = model_factory.create_provided_role("TestProvided", interface)
    component.contents.append(provided_role)
    repository.contents.append(component)
    
    # Add repository to model
    model.fragments.append(repository)
    
    # Save model
    model_resource = save_model(model, "test_repository.xml", model_factory.rset)
    
    # Verify file exists
    assert os.path.exists("test_repository.xml")
    assert os.path.getsize("test_repository.xml") > 0
    
    # Clean up
    if os.path.exists("test_repository.xml"):
        os.remove("test_repository.xml")
    
    return model, repository

def test_create_minimal_system():
    """Test creating a minimal system model."""
    # Get model and repository from previous test
    model, repository = test_create_minimal_repository()
    model_factory = ModelFactory(model.eResource.resourceSet, model.eResource.resourceSet.metamodel_registry[
        "http://www.palladiosimulator.org/textual/tpcm/1.0"
    ])
    
    # Find component and interface from repository
    component = None
    interface = None
    for content in repository.contents:
        if content.eClass.name == "Component":
            component = content
        elif content.eClass.name == "Interface":
            interface = content
    
    assert component is not None
    assert interface is not None
    
    # Create system
    system = model_factory.create_system("TestSystem")
    
    # Create assembly context
    assembly = model_factory.create_assembly_context("TestAssembly", component)
    system.contents.append(assembly)
    
    # Create system provided role
    system_role = model_factory.create_system_provided_role("SystemInterface", interface, assembly)
    system.contents.append(system_role)
    
    # Add system to model
    model.fragments.append(system)
    
    # Save model
    model_resource = save_model(model, "test_system.xml", model_factory.rset)
    
    # Verify file exists
    assert os.path.exists("test_system.xml")
    assert os.path.getsize("test_system.xml") > 0
    
    # Clean up
    if os.path.exists("test_system.xml"):
        os.remove("test_system.xml")
    
    return model, system

def test_create_expression():
    """Test creating stochastic expressions."""
    # Initialize expression factory
    expr_factory = ExpressionFactory()
    
    # Create a simple expression: 2 * (3 + 4)
    int_2 = expr_factory.create_int_literal(2)
    int_3 = expr_factory.create_int_literal(3)
    int_4 = expr_factory.create_int_literal(4)
    
    # 3 + 4
    add_expr = expr_factory.create_term_expression(
        int_3, int_4, expr_factory.stoex.TermOperations.ADD
    )
    
    # (3 + 4)
    paren_expr = expr_factory.create_parenthesis(add_expr)
    
    # 2 * (3 + 4)
    mult_expr = expr_factory.create_product_expression(
        int_2, paren_expr, expr_factory.stoex.ProductOperations.MULT
    )
    
    # Verify the structure
    assert mult_expr.left.value == 2
    assert mult_expr.right.innerExpression.left.value == 3
    assert mult_expr.right.innerExpression.right.value == 4
    
    # Create a probability distribution
    exp_dist = expr_factory.create_exp_distribution(
        expr_factory.create_double_literal(0.5)
    )
    
    # Verify the distribution
    assert exp_dist.function_ProbabilityFunctionLiteral.eClass.name == "ExponentialDistribution"
    assert exp_dist.function_ProbabilityFunctionLiteral.rate.value == 0.5

if __name__ == "__main__":
    # Run tests
    test_create_minimal_repository()
    test_create_minimal_system()
    test_create_expression()
    print("All tests passed!")