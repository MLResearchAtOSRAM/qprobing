import os
import site


# we set our site dir for testing to parent to have proper package names
MODULE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(MODULE_DIR_PATH, '..'))


import pytest
import pathlib
from qprobing.data_generator import DataGenerator
from qprobing.task_preparator import TaskPreparator
from qprobing.experiment_evaluator import ExperimentEvaluator


def pytest_collection_modifyitems(items):
    """Sets the time limit for each test to x seconds."""
    for item in items:
        if item.get_closest_marker('timeout') is None:
            item.add_marker(pytest.mark.timeout(30))


@pytest.fixture
def example_generator():
    return DataGenerator.from_scratch(
        n_vars=5,
        p_edge=0.1,
        dag_seed=1,
        show=False,
    )


@pytest.fixture
def example_model(example_generator):
    example_generator.create_random_model(seed=1)
    return example_generator.model


@pytest.fixture
def example_nx_graph(example_generator):
    example_generator.create_random_model(seed=1)
    return example_generator.nx_graph


@pytest.fixture
def example_data(example_generator):
    example_generator.create_random_model(seed=1)
    example_generator.generate_data(
        n_samples=1000,
        seed=1,
    )
    return example_generator.data


@pytest.fixture
def example_data_path(example_generator):
    path = pathlib.Path.cwd() / 'tests' / 'qprobing' / 'fixtures' / 'example_data.csv'
    example_generator.create_random_model(seed=1)
    example_generator.generate_data(
        n_samples=1000,
        seed=1,
        save_to_file=path,
    )
    return path


@pytest.fixture
def example_preparator(example_model, example_nx_graph):
    preparator = TaskPreparator(example_model, example_nx_graph)
    preparator.prepare_task(
        p_hint=0.8,
        p_probe=0.5,
        tolerance=0.1,
    )
    return preparator


@pytest.fixture
def evaluator(pickle_path):
    return ExperimentEvaluator.from_pkl(pickle_path)


@pytest.fixture
def pickle_path():
    return pathlib.Path.cwd() / 'tests' / 'qprobing' / 'fixtures' / '10_runs_06-04_16-32.pkl'
