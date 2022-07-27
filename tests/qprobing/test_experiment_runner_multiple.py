import pytest
from qprobing.experiment_runner import ExperimentRunner


@pytest.mark.uses_jvm
def test_run_experiments(example_data_path):
    n_experiments = 3
    seeds_list = [
        {
            'dag_seed': i + 10,
            'cpd_seed': i,
            'simulation_seed': i,
        }
        for i in range(n_experiments)
    ]
    data_generation_specs = {
        'n_vars': 5,
        'n_samples': 1000,
        'p_edge': 0.1,
        'seeds': None,
        'show': False,
    }
    task_specs = {
        'p_hint': 0.3,
        'p_probe': 0.5,
        'tolerance': 0.1,
    }
    runner = ExperimentRunner(example_data_path)
    runner.run_experiments(
        n_experiments,
        data_generation_specs,
        seeds_list,
        task_specs,
        verbose=True,
    )
