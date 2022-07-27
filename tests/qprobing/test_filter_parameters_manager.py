import pytest
import numpy as np
from qprobing.filter_parameters_manager import FilterParametersManager


@pytest.fixture
def filter_param_mgr():
    return FilterParametersManager(
        filter_params_dict={
            'n_nontrivial_probes': {'lower_bound': 1, 'upper_bound': 8, 'n_bins': 3},
            'hit_rate': {'lower_bound': 0, 'upper_bound': 1, 'n_bins': 10},
            'correct_graph_found': {'lower_bound': 0, 'upper_bound': 1},
        },
    )


def test_get_lower_bounds_meshgrid(filter_param_mgr):
    lower_bounds_nontrivial = np.linspace(start=1, stop=8, num=4)[:-1]
    lower_bounds_hit_rate = np.linspace(start=0, stop=1, num=11)[:-1]
    expected_grid = np.meshgrid(lower_bounds_nontrivial, lower_bounds_hit_rate)
    calculated_grid = filter_param_mgr._get_lower_bounds_meshgrid()
    print(calculated_grid, expected_grid)
    for calculated_el, expected_el in zip(calculated_grid, expected_grid):
        print(calculated_el, expected_el)
        print(type(calculated_el), type(expected_el))
        assert (calculated_el == expected_el).all()


def test_get_lower_bounds_1d_multiple_filters(filter_param_mgr):
    all_calculated_bounds = filter_param_mgr._get_lower_bounds_1d_multiple_filters()
    calculated_bounds = all_calculated_bounds['hit_rate']
    expected_bounds = np.linspace(start=0, stop=0.9, num=10)
    assert (calculated_bounds == expected_bounds).all()
    assert all_calculated_bounds.keys() == {'n_nontrivial_probes', 'hit_rate'}


def test_get_lower_bounds_1d(filter_param_mgr):
    calculated_bounds = filter_param_mgr._get_lower_bounds_1d('hit_rate')
    expected_bounds = np.linspace(start=0, stop=0.9, num=10)
    assert (calculated_bounds == expected_bounds).all()


def test_get_variable_filter_names(filter_param_mgr):
    assert filter_param_mgr.variable_filter_names == ['n_nontrivial_probes', 'hit_rate']
    assert filter_param_mgr.static_filter_names == ['correct_graph_found']
