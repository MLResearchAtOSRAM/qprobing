import pytest
from qprobing.experiment_runner import ExperimentRunner


@pytest.mark.uses_jvm
def test_run_experiment(example_data_path):
    seeds = {
        'dag_seed': 1,
        'cpd_seed': 2,
        'simulation_seed': 2,
    }

    data_generation_specs = {
        'n_vars': 5,
        'n_samples': 1000,
        'p_edge': 0.1,
        'seeds': seeds,
        'show': False,
    }

    task_specs = {
        'p_hint': 0,
        'p_probe': 0.5,
        'tolerance': 0.1,
    }

    runner = ExperimentRunner(example_data_path)
    runner.run_experiment(
        data_generation_specs,
        task_specs,
        verbose=True,
        keep_vm=False,
    )
