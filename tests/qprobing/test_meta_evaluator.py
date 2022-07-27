import pytest
import numpy as np
from numpy import NaN, isclose
from qprobing.meta_evaluator import MetaEvaluator, VisualizationError
from qprobing.filter_parameters_manager import FilterParametersManager


def test_plot_quantity_means_single_filter(pickle_path):
    _plot_quantity_means(
        pickle_path,
        filter_params_dict={
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
        },
    )


def test_plot_quantity_means_two_filters(pickle_path):
    _plot_quantity_means(
        pickle_path,
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
        },
    )


def test_plot_quantity_means_too_many_filters(pickle_path):
    with pytest.raises(VisualizationError):
        _plot_quantity_means(
            pickle_path,
            filter_params_dict={
                'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
                'true_n_connected_components': {'lower_bound': 0, 'upper_bound': 5, 'n_bins': 5},
                'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
            },
        )


def _plot_quantity_means(pickle_path, filter_params_dict):
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    quantity_names = ['relative_effect_differences', 'n_edge_differences']
    meta_evaluator.plot_quantity_means(quantity_names, filter_params_dict)


@pytest.mark.skip(reason="weird ValueError in scatter, made function private")
def test_plot_single_quantity_means_single_filter(pickle_path):
    quantity_name = 'n_edge_differences'
    filter_params_dict = {
        'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
    }
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    meta_evaluator.get_quantity_means([quantity_name], filter_params_dict)
    meta_evaluator._plot_single_quantity_means(quantity_name, filter_params_dict)


def test_get_quantity_means_single_filter(pickle_path):
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    meta_evaluator.get_quantity_means(
        quantity_names=['relative_effect_differences', 'n_edge_differences'],
        filter_params_dict={
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
        },
    )
    calculated_relative_effect_differences = meta_evaluator.quantity_means['relative_effect_differences']
    calculated_n_edge_differences = meta_evaluator.quantity_means['n_edge_differences']
    relative_effect_differences = np.array([NaN, NaN, NaN, NaN, NaN, NaN, NaN, 1.0, 0.69, 0.55])
    n_edge_differences = np.array([NaN, NaN, NaN, NaN, NaN, NaN, NaN, 7.0, 5.7, 5.3])
    _compare_arrays_with_nans(calculated_relative_effect_differences, relative_effect_differences)
    _compare_arrays_with_nans(calculated_n_edge_differences, n_edge_differences)


def _compare_arrays_with_nans(arr1, arr2, tolerance=0.1):
    assert isclose(arr1, arr2, atol=0.1, equal_nan=True).all()


def test_get_quantity_means_multiple_filters(pickle_path):
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    meta_evaluator.get_quantity_means(
        quantity_names=['relative_effect_differences', 'n_edge_differences'],
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
        },
    )
    calculated_n_edge_differences = meta_evaluator.quantity_means['n_edge_differences']
    expected_values = {7, 4}
    assert all(val in calculated_n_edge_differences for val in expected_values)
    assert calculated_n_edge_differences.shape == (3, 10)


def test_get_quantity_means_multiple_filters_with_static_filter(pickle_path):
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    meta_evaluator.get_quantity_means(
        quantity_names=['relative_effect_differences', 'n_edge_differences'],
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
            'correct_graph_found': {'lower_bound': 0, 'upper_bound': 1},
        },
    )
    calculated_n_edge_differences = meta_evaluator.quantity_means['n_edge_differences']
    assert calculated_n_edge_differences.shape == (3, 10)


def test_get_output_dimensions(pickle_path):
    _check_dims(
        pickle_path,
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
        },
        expected_dims=(3, 10),
    )


def test_get_output_dimensions_with_static_filter(pickle_path):
    _check_dims(
        pickle_path,
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
            'correct_graph_found': {'lower_bound': 0, 'upper_bound': 1},
        },
        expected_dims=(3, 10),
    )


def _check_dims(pickle_path, filter_params_dict, expected_dims):
    meta_evaluator = MetaEvaluator.from_pkl(pickle_path)
    filter_param_mgr = FilterParametersManager(filter_params_dict)
    meta_evaluator._get_output_dimensions(filter_param_mgr)
    assert meta_evaluator._output_dimensions == expected_dims
