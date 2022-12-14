"""This module provides the main functionality for evaluating quantitative probing experiments."""

import pickle
import numpy as np
import matplotlib.pyplot as plt
from qprobing.experiment_result import ExperimentResult
from qprobing.results_filter import ResultsFilter


class ExperimentEvaluator:
    """Main class for evaluating the results of several quantitative probing experiment runs."""
    def __init__(self, results_list, filter_params={}):
        unpacker = ResultUnpacker(results_list, filter_params)
        unpacker.unpack_results()
        for attribute_name in vars(unpacker):
            attribute = getattr(unpacker, attribute_name)
            setattr(self, attribute_name, attribute)

    @classmethod
    def from_experiment_runner(cls, runner, filter_params={}):
        return cls(runner.results_list, filter_params)

    @classmethod
    def from_pkl(cls, filename, filter_params={}):
        with open(filename, 'rb') as f:
            results_list = pickle.load(f)
        return cls(results_list, filter_params)

    @classmethod
    def from_multiple_pkls(cls, filenames, filter_params={}):
        results_list = []
        for filename in filenames:
            with open(filename, 'rb') as f:
                results_list += pickle.load(f)
        return cls(results_list, filter_params)

    def get_mean(self, attribute_name):
        attribute = self.get_data(attribute_name)
        return np.nanmean(attribute)

    def get_data(self, attribute_name):
        return getattr(self, f"_{attribute_name}")  # TODO: Decide if the attributes are public or not

    def show_full_info(self):
        """Calls all public info methods of the evaluator."""
        self.show_ordinary_results_info()
        self.show_valid_results_info()

    def show_ordinary_results_info(self):
        """Shows how many of the experiment runs were completed without exceptions."""
        print(f"{self._n_ordinary_results} ordinary results vs. {self._n_exceptional_results} exceptional results.")

    def show_valid_results_info(self):
        """Shows how many of the ordinary experiment runs met the filter criteria."""
        print(f"{self._n_valid_results} in-spec results vs. {self._n_invalid_results} out-of-spec results.")

    def show_exceptional_results(self):
        """Shows all exceptional results to help us analyze the problems with these runs."""
        print(self._exceptional_results)

    def show_invalid_results(self):
        """Shows all invalid results to help us analyze the problems with these runs."""
        print(self._invalid_results)

    def show_all_plots(self):
        """Calls all public plot methods of the evaluator."""
        self.plot_n_edge_differences_vs_hit_rates()
        self.plot_absolute_effect_differences_vs_hit_rates()
        self.plot_relative_effect_differences_vs_hit_rates()
        self.plot_effect_differences_vs_hit_rates()
        self.plot_correct_graph_founds_vs_hit_rates()

    def plot_correct_graph_founds_vs_hit_rates(self, plotting_options={}):
        """Plots the causal discovery results (successful or not) against the
        hit rates.

        Args:
            plotting_options: A dict containing plotting options.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        self._plot_metric_vs_hit_rates('_correct_graph_founds', plotting_options)

    def plot_n_edge_differences_vs_hit_rates(self, plotting_options={}):
        """Plots the number of edges that differ between discovery result and true graph against the
        hit rates.

        Args:
            plotting_options: A dict containing plotting options.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        self._plot_metric_vs_hit_rates('_n_edge_differences', plotting_options)

    def plot_absolute_effect_differences_vs_hit_rates(self, plotting_options={}):
        """Plots the absolute difference between the estimated and true target effect against the
        hit rates.

        Args:
            plotting_options: A dict containing plotting options.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        self._plot_metric_vs_hit_rates('_absolute_effect_differences', plotting_options)

    def plot_relative_effect_differences_vs_hit_rates(self, plotting_options={}):
        """Plots the absolute difference between the estimated and true target effect against the
        hit rates.

        Args:
            plotting_options: A dict containing plotting options.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        self._plot_metric_vs_hit_rates('_relative_effect_differences', plotting_options)

    def plot_effect_differences_vs_hit_rates(self, plotting_options={}):
        """Plots the  difference between the estimated and true target effect against the
        hit rates.

        Args:
            plotting_options: A dict containing plotting options.
                Currently available: x_label, y_label, title, png_name, y_lims.
        """
        self._plot_metric_vs_hit_rates('_effect_differences', plotting_options)

    def _plot_metric_vs_hit_rates(self, metric_name, plotting_options={}):
        self._plot('_hit_rates', metric_name, plotting_options)

    def _plot(self, x_name, y_name, plotting_options={}):
        x_data = getattr(self, x_name)
        y_data = getattr(self, y_name)
        if 'opacity' in plotting_options:
            alpha = plotting_options['opacity']
        else:
            alpha = 1
        plt.scatter(x_data, y_data, alpha=alpha)
        x_default = x_name
        x_label = plotting_options.get('x_label', x_default)
        plt.xlabel(x_label)
        y_default = y_name
        y_label = plotting_options.get('y_label', y_default)
        plt.ylabel(y_label)
        title_default = f"{self._n_valid_results} valid runs with {self._n_nodes} nodes"
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


class ResultUnpacker:
    """Utility class for unpacking the results of several quantitative probing runs."""
    def __init__(self, results_list, filter_params={}):
        self._results = results_list
        self._filter_params = filter_params

    @classmethod
    def from_experiment_runner(cls, runner):
        return cls(runner.results_list)

    def unpack_results(self):
        """Unpacks the results to extract meaningful analysis quantities."""
        self._check_results_for_validity()
        self._get_n_nodes()
        self._get_hit_rates()
        self._get_effect_differences()
        self._get_absolute_effect_differences()
        self._get_relative_effect_differences()
        self._get_target_effects()
        self._get_correct_graph_founds()
        self._get_edge_differences()
        self._get_n_edge_differences()

    def _check_results_for_validity(self):
        self._exceptional_results = [x for x in self._results if self._check_exception(x)]
        ordinary_result_dicts = [x for x in self._results if not self._check_exception(x)]
        self._ordinary_results = [ExperimentResult.from_result_dict(x) for x in ordinary_result_dicts]
        self._valid_results = self._get_filtered_ordinary_results()
        self._invalid_results = [x for x in self._ordinary_results if x not in self._valid_results]
        self._get_result_counts()
        assert self._n_valid_results + self._n_invalid_results + self._n_exceptional_results == len(self._results)
        self._collect_valid_evaluators()

    def _check_exception(self, result):
        return isinstance(result, Exception)

    def _get_filtered_ordinary_results(self):
        results = self._ordinary_results
        for attribute_name in self._filter_params:
            results = self._apply_single_filter(results, attribute_name)
        return results

    def _apply_single_filter(self, results, attribute_name):
        params = self._filter_params[attribute_name]
        lower_bound = params.get('lower_bound', None)
        upper_bound = params.get('upper_bound', None)
        results_filter = ResultsFilter(results, attribute_name, lower_bound, upper_bound)
        results_filter.filter_results()
        return results_filter.filtered_results

    def _get_result_counts(self):
        self._n_exceptional_results = len(self._exceptional_results)
        self._n_ordinary_results = len(self._ordinary_results)
        self._n_valid_results = len(self._valid_results)
        self._n_invalid_results = len(self._invalid_results)

    def _collect_valid_evaluators(self):
        self._evaluators = [result.evaluator for result in self._valid_results]

    def _get_n_nodes(self):
        self._n_nodes = self._valid_results[0].n_nodes

    def _get_hit_rates(self):
        self._get_attribute_list('hit_rate')

    def _get_effect_differences(self):
        self._get_attribute_list('effect_difference')

    def _get_absolute_effect_differences(self):
        self._get_attribute_list('absolute_effect_difference')

    def _get_relative_effect_differences(self):
        self._get_attribute_list('relative_effect_difference')

    def _get_target_effects(self):
        self._get_attribute_list('target_effect')

    def _get_correct_graph_founds(self):
        self._get_attribute_list('correct_graph_found')

    def _get_edge_differences(self):
        self._get_attribute_list('edge_difference')

    def _get_n_edge_differences(self):
        self._n_edge_differences = [len(diff) for diff in self._edge_differences]

    def _get_attribute_list(self, attribute_name):
        attribute_list = [getattr(evaluator, attribute_name) for evaluator in self._evaluators]
        setattr(self, f"_{attribute_name}s", attribute_list)
