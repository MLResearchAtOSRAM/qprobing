import itertools
import pytest
from pgmpy.models import BayesianNetwork
from qprobing.pgmpy_causality import (
    EffectCalculator,
    calculate_effect,
    simulate_effect,
    SimulationFallbackError,
)
from qprobing.data_generator import DataGenerator, create_binary_cpd


@pytest.fixture
def model_two_vars():
    edges = {
        ('x0', 'x1')
    }
    treatment = 'x0'
    outcome = 'x1'
    model = BayesianNetwork(edges)
    cpd_treatment = create_binary_cpd(
        node=treatment,
        vals=[0.5],
        parents=set(),
    )
    cpd_outcome = create_binary_cpd(
        node=outcome,
        vals=[0.3, 0.7],
        parents={treatment},
    )
    model.add_cpds(cpd_treatment, cpd_outcome)
    return model


@pytest.fixture
def causality_model():
    data_generator = DataGenerator.from_scratch(
        n_vars=5,
        p_edge=0.1,
        dag_seed=9,
        show=False,
    )
    data_generator.create_random_model(seed=1)
    return data_generator.model


def test_effect_is_trivial_zero(model_two_vars):
    treatment = 'x1'
    outcome = 'x0'
    calculator = EffectCalculator(model_two_vars, treatment, outcome)
    assert calculator._effect_is_trivial_zero()
    assert calculator.determine_effect() == 0


@pytest.mark.parametrize("treatment, outcome", [('x0', 'x1'), ('x0', 'x0'), ('x1', 'x1')])
def test_effect_is_not_trivial_zero(model_two_vars, treatment, outcome):
    calculator = EffectCalculator(model_two_vars, treatment, outcome)
    assert not calculator._effect_is_trivial_zero()


@pytest.mark.parametrize("treatment, outcome", [('x0', 'x0'), ('x1', 'x1')])
def test_effect_is_trivial_one(model_two_vars, treatment, outcome):
    calculator = EffectCalculator(model_two_vars, treatment, outcome)
    assert calculator._effect_is_trivial_one()
    assert calculator.determine_effect() == 1


@pytest.mark.parametrize("treatment, outcome", [('x1', 'x0'), ('x0', 'x1')])
def test_effect_is_not_trivial_one(model_two_vars, treatment, outcome):
    calculator = EffectCalculator(model_two_vars, treatment, outcome)
    assert not calculator._effect_is_trivial_one()


def test_effect_is_problematic(causality_model):
    nodes = set(causality_model.nodes)
    for treatment, outcome in itertools.product(nodes, nodes):
        calculator = EffectCalculator(causality_model, treatment, outcome)
        if treatment == 'x2' and outcome == 'x1':
            assert calculator._effect_is_problematic()
        else:
            assert not calculator._effect_is_problematic()


def test_use_simulation_fallback(causality_model):
    tolerance = 0.05
    calculated = _use_simulation_fallback(causality_model, pass_samples=True)
    simulated = simulate_effect(causality_model, 'x2', 'x1', n_samples=10000)
    assert abs(calculated - simulated) < tolerance


def test_use_failed_simulation_fallback(causality_model):
    with pytest.raises(SimulationFallbackError):
        _use_simulation_fallback(causality_model, pass_samples=False)


def _use_simulation_fallback(causality_model, pass_samples):
    if pass_samples:
        n_samples = 10000
    else:
        n_samples = None
    treatment = 'x2'
    outcome = 'x1'
    calculator = EffectCalculator(causality_model, treatment, outcome, n_samples)
    assert calculator._effect_is_problematic()
    return calculator.determine_effect()


def test_calculate_effect(causality_model):
    tolerance = 0.05
    n_samples = 10000
    nodes = set(causality_model.nodes)
    for treatment, outcome in itertools.product(nodes, nodes):
        assert _compare_calculation_and_simulation(causality_model, treatment, outcome, n_samples, tolerance)


def _compare_calculation_and_simulation(model, treatment, outcome, n_samples, tolerance):
    calculated = calculate_effect(model, treatment, outcome, n_samples)
    simulated = simulate_effect(model, treatment, outcome, n_samples)
    return abs(calculated - simulated) < tolerance
