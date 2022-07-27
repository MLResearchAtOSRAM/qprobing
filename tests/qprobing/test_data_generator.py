import pytest
import networkx as nx
from qprobing.data_generator import DataGenerator, MissingModelError


def test_constructor_equivalence(example_generator):
    from_scratch = example_generator
    from_nx_graph = DataGenerator.from_nx_graph(from_scratch.nx_graph)
    from_edges = DataGenerator(from_scratch.edges)
    generators = [from_scratch, from_nx_graph, from_edges]
    _check_generator_equality(generators)


def _check_generator_equality(generators):
    attribute_names = ['edges', 'nodes', 'nx_graph']
    for name in attribute_names:
        attributes = _get_all_attributes(generators, name)
        if name == 'nx_graph':
            assert nx.is_isomorphic(attributes[0], attributes[1]) and nx.is_isomorphic(attributes[1], attributes[2])
        else:
            assert attributes[0] == attributes[1] == attributes[2]


def _get_all_attributes(generators, attribute_name):
    return [getattr(gen, attribute_name) for gen in generators]


def test_create_random_model(example_generator):
    example_generator.create_random_model(seed=1)
    model = example_generator.model
    assert set(model.nodes) == example_generator.nodes
    assert set(model.edges) == example_generator.edges


def test_cpd_seed(example_generator):
    models = [_get_random_model(example_generator, seed) for seed in [0, 1, 0]]
    assert models[0].cpds == models[2].cpds
    assert models[0].cpds != models[1].cpds


def _get_random_model(example_generator, seed):
    example_generator.create_random_model(seed=seed)
    return example_generator.model


def test_generate_data(example_generator):
    n_samples = 1000
    example_generator.create_random_model(seed=1)
    example_generator.generate_data(
        n_samples=n_samples,
        seed=1,
        save_to_file=None,
    )
    data = example_generator.data
    assert len(data) == n_samples
    assert len(data.columns) == len(example_generator.model.cpds)


def test_generate_data_without_model(example_generator):
    n_samples = 1000
    with pytest.raises(MissingModelError):
        example_generator.generate_data(
            n_samples=n_samples,
            seed=1,
            save_to_file=None,
        )


def test_simulation_seed(example_generator):
    simulation_seeds = [1, 2, 1]
    datasets = [_generate_data_with_seed(example_generator, seed) for seed in simulation_seeds]
    assert datasets[0].equals(datasets[2])
    assert not datasets[0].equals(datasets[1])


def _generate_data_with_seed(example_generator, seed):
    example_generator.create_random_model(seed=1)
    example_generator.generate_data(
        n_samples=1000,
        seed=seed,
        save_to_file=None,
    )
    return example_generator.data.copy()
