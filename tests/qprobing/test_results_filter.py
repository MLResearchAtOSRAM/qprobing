import pytest
from qprobing.results_filter import ResultsFilter, NoBoundsError


@pytest.fixture
def test_vals():
    return [-1, 0, 1]


def test_comparison_with_none(test_vals):
    for val in test_vals:
        with pytest.raises(TypeError):
            None < val
        with pytest.raises(TypeError):
            None > val


def test_bool_evals(test_vals):
    for val in test_vals:
        assert val is not None
    assert not 0


def test_compare_attribute_val_to_invalid_bounds():
    with pytest.raises(NoBoundsError):
        _compare_attribute_val_to_bounds(None, None)


@pytest.mark.parametrize("lower_bound, upper_bound", [(None, 1), (-1, None), (-1, 1)])
def test_successfully_compare_attribute_val_to_valid_bounds(lower_bound, upper_bound):
    assert _compare_attribute_val_to_bounds(lower_bound, upper_bound)


@pytest.mark.parametrize("lower_bound, upper_bound", [(None, -1), (1, None), (1, -1)])
def test_unsuccessfully_compare_attribute_val_to_valid_bounds(lower_bound, upper_bound):
    assert not _compare_attribute_val_to_bounds(lower_bound, upper_bound)


def _compare_attribute_val_to_bounds(lower_bound, upper_bound):
    results_filter = ResultsFilter(results=[], attribute_name='', lower_bound=lower_bound, upper_bound=upper_bound)
    results_filter._attribute_val = 0
    return results_filter._compare_attribute_val_to_bounds()
