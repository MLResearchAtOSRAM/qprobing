"""This module provides the main functionality for handling filter parameters.

The user can pass several static or variable filters for selecting quantitative probing runs, which
need to be combined to create an array of filter conditions.
"""

import itertools
import numpy as np


class FilterParametersManager():
    """Main class for handling filter parameters.

    Attributes:
        output_dimensions: A tuple indicating the number of bins in each filter.
        params_arr: The final numpy array of combined filtering conditions.
        variable_filter_names: A list containing all filters varying over several bins. These are
            used for checking if the filter criterion is useful for validating causal models.
        static_filter_names: A list containing all static filters. These are used to exclude
            outliers in the probing runs.
        lower_bounds: A dict of numpy arrays, each containing the lower bounds of the filtering bins
            for a given filter name.
        lower_bounds_meshgrid: A numpy array holding the meshgrid of lower bounds of the filtering
            bins for all filter names. It is later used for creating 3d scatter plots.
    """
    def __init__(self, filter_params_dict):
        self._filter_params_dict = filter_params_dict
        self.output_dimensions = self._get_output_dimensions()
        self._binned_params = self._get_binned_filter_params()
        self.params_arr = self._get_expanded_filter_combinations()
        self.variable_filter_names = self._get_variable_filter_names()
        self.static_filter_names = self._get_static_filter_names()
        self.lower_bounds = self._get_lower_bounds_1d_multiple_filters()
        self.lower_bounds_meshgrid = self._get_lower_bounds_meshgrid()

    def _get_output_dimensions(self):
        return tuple(v['n_bins'] for v in self._filter_params_dict.values() if 'n_bins' in v)

    def _get_binned_filter_params(self):
        return {k: self._get_filter_params_list(k, v) for k, v in self._filter_params_dict.items()}

    def _get_filter_params_list(self, filter_name, filter_params):
        n_bins = filter_params.get('n_bins', 1)
        # TODO: use np.linspace instead of custom calculation
        lower_bound = filter_params['lower_bound']
        upper_bound = filter_params['upper_bound']
        bin_size = (upper_bound - lower_bound) / n_bins
        return [{filter_name: self._get_regular_bounds(lower_bound, bin_size, i)} for i in range(n_bins)]

    @staticmethod
    def _get_regular_bounds(lower_bound, bin_size, i):
        return {'lower_bound': lower_bound + i * bin_size, 'upper_bound': lower_bound + (i + 1) * bin_size}

    def _get_expanded_filter_combinations(self):
        product = itertools.product(*self._binned_params.values())
        product_list = [self._combine_dicts_in_params(params) for params in product]
        product_flat_arr = np.array(product_list)
        product_arr = np.reshape(product_flat_arr, self.output_dimensions)
        return product_arr

    @staticmethod
    def _combine_dicts_in_params(params):
        return dict(i for d in params for i in d.items())

    def _get_variable_filter_names(self):
        # List instead of set is necessary because we need the ordering for the meshgrid
        return [k for k, v in self._filter_params_dict.items() if 'n_bins' in v]

    def _get_static_filter_names(self):
        return [k for k in self._filter_params_dict if k not in self.variable_filter_names]

    def _get_lower_bounds_meshgrid(self):
        lower_bounds_1d = self._get_lower_bounds_1d_multiple_filters().values()
        return np.meshgrid(*lower_bounds_1d)

    def _get_lower_bounds_1d_multiple_filters(self):
        return {filter_name: self._get_lower_bounds_1d(filter_name) for filter_name in self.variable_filter_names}

    def _get_lower_bounds_1d(self, filter_name):
        relevant_list = self._binned_params[filter_name]
        return np.array([self._get_lower_bound(dic) for dic in relevant_list])

    def _get_lower_bound(self, dic):
        return tuple(v['lower_bound'] for k, v in dic.items() if k in self.variable_filter_names)[0]
