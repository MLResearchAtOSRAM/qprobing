import numpy as np
from numpy import NaN
from qprobing.experiment_evaluator import ExperimentEvaluator


def test_show_full_info(evaluator):
    evaluator.show_full_info()


def test_show_invalid_results(evaluator):
    evaluator.show_invalid_results()


def test_show_all_plots(evaluator):
    evaluator.show_all_plots()


def test_get_mean(evaluator):
    input_list = [1, NaN, 1]
    evaluator._dummy_attribute = input_list
    assert np.isnan(sum(input_list) / len(input_list))
    assert evaluator.get_mean('dummy_attribute') == 1


def test_init_with_filter_params(pickle_path):
    filter_params = {
        'connected_probes_ratio': {'lower_bound': 0.3},
    }
    _check_evaluator_init(pickle_path, filter_params)


def test_init_with_multiple_filter_params(pickle_path):
    filter_params = {
        'connected_probes_ratio': {'lower_bound': 0.1},
        'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8},
        'correct_graph_found': {'upper_bound': 0},  # Boolean attributes should be queried more naturally
        'n_edge_differences': {'lower_bound': 3, 'upper_bound': 8},
        'effect_difference': {'lower_bound': -0.5, 'upper_bound': 0.2},
        'hit_rate': {'upper_bound': 0.9},
    }
    _check_evaluator_init(pickle_path, filter_params)


def test_init_from_multiple_pkls_with_filter_params(pickle_path):
    filter_params = {
        'connected_probes_ratio': {'lower_bound': 0.3},
    }
    _check_evaluator_init(pickle_path, filter_params, from_multiple_pkls=True)


def test_init_from_multiple_pkls_with_multiple_filter_params(pickle_path):
    filter_params = {
        'connected_probes_ratio': {'lower_bound': 0.1},
        'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8},
        'correct_graph_found': {'upper_bound': 0},  # Boolean attributes should be queried more naturally
        'n_edge_differences': {'lower_bound': 3, 'upper_bound': 8},
        'effect_difference': {'lower_bound': -0.5, 'upper_bound': 0.2},
        'hit_rate': {'upper_bound': 0.9},
    }
    _check_evaluator_init(pickle_path, filter_params, from_multiple_pkls=True)


def _check_evaluator_init(pickle_path, filter_params, from_multiple_pkls=False):
    if from_multiple_pkls:
        full_evaluator = ExperimentEvaluator.from_multiple_pkls([pickle_path, pickle_path])
    else:
        full_evaluator = ExperimentEvaluator.from_pkl(pickle_path)
    full_results = full_evaluator._valid_results
    reduced_evaluator = ExperimentEvaluator.from_pkl(pickle_path, filter_params)
    reduced_results = reduced_evaluator._valid_results
    assert 0 < len(reduced_results) < len(full_results)
    assert reduced_results
