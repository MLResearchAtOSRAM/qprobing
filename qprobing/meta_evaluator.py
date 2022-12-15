"""This module provides the main functionality for aggregating the results of multiple quantitative
probing runs.

The aggregation method is taking the mean over interesting quantities within a group defined by a
filter criterion (e.g. calculating the mean probabilty of finding the correct causal graph for
quantitative probing hit rates between 0.1 and 0.2, 0.2 and 0.3 and so forth). The tendencies in the
means will then be used as evidence that a certain criterion is helpful for validating the results of
and end-to-end causal analysis. In addition to the variable filters (hit rate in the above example),
it is also possible to use static filters to exclude outliers (e.g. use only probing runs where at
least 80% of the probes were located in the same component of the causal graph as the target
effect.). The means can be plotted to illustrate the discovered tendencies.
"""

import pickle
import numpy as np
from numpy import NaN
import matplotlib.pyplot as plt
from qprobing.experiment_evaluator import ExperimentEvaluator
from qprobing.filter_parameters_manager import FilterParametersManager


class MetaEvaluator:
    """Main class for aggregating the results of quantitative probing runs.

    Attributes:
        quantity_means: A dict of numpy arrays (one for each quantity) holding the mean of the last
            calculated quantities for each of the specified filter binnings.
    """
    def __init__(self, results_list):
        self._results_list = results_list

    @classmethod
    # TODO: Duplicate from experiment evaluator alternative constructor
    def from_pkl(cls, filename):
        with open(filename, 'rb') as f:
            results_list = pickle.load(f)
        return cls(results_list)

    @classmethod
    # TODO: Duplicate from experiment evaluator alternative constructor
    def from_multiple_pkls(cls, filenames, filter_params={}):
        results_list = []
        for filename in filenames:
            with open(filename, 'rb') as f:
                results_list += pickle.load(f)
        return cls(results_list)

    def boxplot_quantity_data(self, quantity_names, filter_params_dict, calculate_data=True, plotting_options=[]):
        """Boxplots the data of multiple quantities against the filter criteria.

        Args:
            quantity_names: A list of strings indicating the names of the quantities.
            filter_params_dict: A dict containing entries of the form
                {filter_name: {'lower_bound': x, 'upper_bound': y, 'n_bins': z}}
                The 'n_bins' entry can be omitted to create a static filter.
            calculate_data: A boolean indicating if the data have to be calculated before the
                plotting. If the data and filters have not changed, skipping this calculation can
                save time.
            plotting_options: A list of dicts containing plotting options for
                each of the quantities.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        if calculate_data:
            self.get_quantity_data(quantity_names, filter_params_dict)
        if not plotting_options:
            plotting_options = [{} for name in quantity_names]
        for name, options in zip(quantity_names, plotting_options):
            self._boxplot_single_quantity_data(name, filter_params_dict, options)

    def _boxplot_single_quantity_data(self, quantity_name, filter_params_dict, plotting_options={}):
        if len(self._lower_bounds) == 1:
            self._boxplot_single_quantity_data_one_filter(quantity_name, plotting_options)
        else:
            raise VisualizationError("Boxplot not implemented for more than one filter")

    def _boxplot_single_quantity_data_one_filter(self, quantity_name, plotting_options={}):
        self._preprocess_data_for_boxplot
        relevant_data_batches, relevant_lower_bounds = self._preprocess_data_for_boxplot(
            quantity_name,
            plotting_options,
        )
        fig, ax = plt.subplots()
        ax.boxplot(relevant_data_batches, showmeans=True)
        ax.set_xticklabels([str(round(lb, 2)) for lb in relevant_lower_bounds])
        self._postprocess_single_filter_plot(quantity_name, plotting_options)

    def _preprocess_data_for_boxplot(self, quantity_name, plotting_options):
        filter_name = list(self._lower_bounds)[0]
        lower_bounds = self._lower_bounds[filter_name]
        data_batches = self.quantity_data[quantity_name]
        min_data_points = plotting_options.get('min_data_points', 1)
        lb_offset = plotting_options.get('lb_offset', 0)
        return self._filter_data_for_boxplot(lower_bounds, data_batches, min_data_points, lb_offset)

    def _filter_data_for_boxplot(self, lower_bounds, data_batches, min_data_points, lb_offset):
        nonempty_data_batches = [batch for batch in data_batches if not (type(batch) == float and np.isnan(batch))]
        relevant_data_batches = [batch for batch in nonempty_data_batches if len(batch) >= min_data_points]
        relevant_lower_bounds = [lb + lb_offset for lb, batch in zip(lower_bounds, data_batches)
                                 if batch in relevant_data_batches]
        return relevant_data_batches, relevant_lower_bounds

    def _postprocess_single_filter_plot(self, quantity_name, plotting_options):
        filter_name = list(self._lower_bounds)[0]
        x_default = f"{filter_name} lower bound"
        x_label = plotting_options.get('x_label', x_default)
        plt.xlabel(x_label)
        y_default = quantity_name
        y_label = plotting_options.get('y_label', y_default)
        plt.ylabel(y_label)
        title_default = f"{quantity_name} aggregated by {filter_name}"
        title = plotting_options.get('title', title_default)
        plt.title(title)
        if 'y_lims' in plotting_options:
            plt.ylim(*plotting_options['y_lims'])
        if 'png_name' in plotting_options:
            fig = plt.gcf()
            path = plotting_options['png_name']
            fig.savefig(path)
            print(f'Saving to {path}')
        plt.show(block=False)

    def plot_quantity_means(self, quantity_names, filter_params_dict, calculate_means=True, plotting_options=[]):
        """Plots the means of multiple quantities against the filter criteria.

        Args:
            quantity_names: A list of strings indicating the names of the quantities.
            filter_params_dict: A dict containing entries of the form
                {filter_name: {'lower_bound': x, 'upper_bound': y, 'n_bins': z}}
                The 'n_bins' entry can be omitted to create a static filter.
            calculate_means: A boolean indicating if the means have to be calculated before the
                plotting. If the data and filters have not changed, skipping this calculation can
                save time.
            plotting_options: A list of dicts containing plotting options for
                each of the quantities.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        if calculate_means:
            self.get_quantity_means(quantity_names, filter_params_dict)
        if not plotting_options:
            plotting_options = [{} for name in quantity_names]
        for name, options in zip(quantity_names, plotting_options):
            self._plot_single_quantity_means(name, filter_params_dict, options)

    def _plot_single_quantity_means(self, quantity_name, filter_params_dict, plotting_options={}):
        if len(self._lower_bounds) == 1:
            self._plot_single_quantity_means_one_filter(quantity_name, plotting_options)
        elif len(self._lower_bounds) == 2:
            self._plot_single_quantity_means_two_filters(quantity_name)
        else:  # TODO two float filters and one binary would work if we use color
            raise VisualizationError("Plot not implemented for more than two filters")

    def _plot_single_quantity_means_one_filter(self, quantity_name, plotting_options={}):
        filter_name = list(self._lower_bounds)[0]
        plt.scatter(self._lower_bounds[filter_name], self.quantity_means[quantity_name])
        self._postprocess_single_filter_plot(quantity_name, plotting_options)

    def _plot_single_quantity_means_two_filters(self, quantity_name):
        filter_names = list(self._lower_bounds.keys())
        mesh_vals = self._lower_bounds_meshgrid
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(*mesh_vals, self.quantity_means[quantity_name])
        plt.xlabel(f"{filter_names[0]} lower bound")
        plt.ylabel(f"{filter_names[1]} lower bound")
        ax.set_zlabel(quantity_name)
        plt.title(f"mean {quantity_name} grouped by {filter_names[0]} and {filter_names[1]}")
        plt.show(block=False)

    def get_quantity_means(self, quantity_names, filter_params_dict):
        """Calculates the means of multiple quantities with respect to the given filter criteria.

        Args:
            quantity_names: A list of strings indicating the names of the quantities.
            filter_params_dict: A dict containing entries of the form
                {filter_name: {'lower_bound': x, 'upper_bound': y, 'n_bins': z}}
                The 'n_bins' entry can be omitted to create a static filter.
        """
        params_arr = self._prepare_params_arr(quantity_names, filter_params_dict, set_bounds=True)
        evaluators = self._get_evaluators(params_arr)
        self.quantity_means = {quantity: self._get_quantity_means(quantity, evaluators) for quantity in quantity_names}

    def _prepare_params_arr(self, quantity_names, filter_params_dict, set_bounds=True):
        filter_param_mgr = FilterParametersManager(filter_params_dict)
        self._get_output_dimensions(filter_param_mgr)
        if set_bounds:
            self._set_bounds(filter_param_mgr)
        return filter_param_mgr.params_arr

    def _set_bounds(self, filter_param_mgr):
        self._lower_bounds = filter_param_mgr.lower_bounds
        self._lower_bounds_meshgrid = filter_param_mgr.lower_bounds_meshgrid

    def _get_output_dimensions(self, filter_param_mgr):
        self._output_dimensions = filter_param_mgr.output_dimensions

    def _get_evaluators(self, params_arr):
        return np.vectorize(self._get_evaluator)(params_arr)

    def _get_evaluator(self, params):
        try:
            return ExperimentEvaluator(self._results_list, params)
        except IndexError:
            return None

    def _get_quantity_means(self, quantity, evaluators):
        def wrapped_fun(evaluator):
            return self._get_quantity_mean(quantity, evaluator)
        return np.vectorize(wrapped_fun)(evaluators)

    def _get_quantity_mean(self, quantity, evaluator):
        if evaluator:
            return evaluator.get_mean(quantity)
        else:
            return NaN

    def get_quantity_data(self, quantity_names, filter_params_dict):
        """Gets the data of multiple quantities with respect to the given filter criteria.
        Used for any plots that go beyond showing only the mean.

        Args:
            quantity_names: A list of strings indicating the names of the quantities.
            filter_params_dict: A dict containing entries of the form
                {filter_name: {'lower_bound': x, 'upper_bound': y, 'n_bins': z}}
                The 'n_bins' entry can be omitted to create a static filter.
        """
        params_arr = self._prepare_params_arr(quantity_names, filter_params_dict, set_bounds=True)
        if len(self._lower_bounds) > 1:
            msg = 'Multiple multi-bin filters are not supported yet for full aggregation analysis.'\
                  'Please restrict the aggregation analysis to means only.'
            raise BinningError(msg)
        else:
            evaluators = self._get_evaluators(params_arr)
        self.quantity_data = {quantity: self._get_quantity_data(quantity, evaluators) for quantity in quantity_names}

    def _get_quantity_data(self, quantity, evaluators):
        return [self._get_quantity_data_single(quantity, evaluator) for evaluator in evaluators]

    def _get_quantity_data_single(self, quantity, evaluator):
        if evaluator:
            return evaluator.get_data(quantity)
        else:
            return NaN


class VisualizationError(Exception):
    pass


class BinningError(Exception):
    pass
