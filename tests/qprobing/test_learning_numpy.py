import numpy as np
from numpy import NaN, isnan


def test_nans_in_numpy():
    assert not NaN == NaN
    assert isnan(NaN) and isnan(NaN)
    assert not abs(NaN - NaN) < 0.1


def test_numpy_squeeze():
    arr = np.zeros((1, 3, 1, 4))
    squeezed_arr = arr.squeeze()
    assert squeezed_arr.shape == (3, 4)


def test_numpy_array_holding_dicts():
    arr = np.array([
        [{'foo': 'bar'}, {}],
        [{}, {'foo': 'baz'}],
    ])
    assert arr.shape == (2, 2)
    assert arr[0, 0] == {'foo': 'bar'}


def test_numpy_array_from_flat_list():
    desired_dims = (2, 3)
    li = list(range(6))
    arr = np.array(li)
    arr_new = np.reshape(arr, desired_dims)
    assert arr_new.shape == desired_dims
    assert (arr_new[0, :] == [0, 1, 2]).all()


def test_apply_function_elementwise_to_numpy_array():
    def _compute_square(x):
        return x ** 2
    arr = np.random.random_sample((2, 2))
    squared_arr = _compute_square(arr)
    assert all(a**2 == b for a, b in zip(np.nditer(arr), np.nditer(squared_arr)))
