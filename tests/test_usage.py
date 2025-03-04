#!/usr/bin/env python3
"""Test file for usage model creation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from tpcm_generator.utils import setup_metamodel, save_model
from tpcm_generator.model_factory import ModelFactory
from tpcm_generator.expression_factory import ExpressionFactory


def create_test_usage():
    """Create a minimal model with just a usage section for testing."""
    # Initialize metamodel
    rset, PCM = setup_metamodel()
    model_factory = ModelFactory(rset, PCM)
    expr_factory = ExpressionFactory(rset)

    # Create model
    model = model_factory.create_model()

    # Create usage model
    usage = model_factory.create_usage_model("TestUsage")

    # Create a scenario
    scenario = model_factory.create_usage_scenario("TestScenario")

    # Create workload - use a simple string for exponential distribution
    workload = PCM.OpenWorkload()

    # Create exponential distribution for interArrivalTime
    rate = expr_factory.create_double_literal(0.04)
    exp_dist = expr_factory.create_exp_distribution(0.4)
    workload.interArrivalTime = exp_dist

    # Add workload to scenario
    scenario.workload = workload

    # Add scenario to usage model
    usage.contents.append(scenario)

    # Add usage to model
    model.fragments.append(usage)

    # Save model
    save_model(model, "test_usage.xml", rset)

    print("Test usage model created")
    return model


if __name__ == "__main__":
    create_test_usage()
