"""This module provides the main functionality for filtering a list of quantitative probing results.

The filtering works by checking if a specified attribute of a result falls within the specified
bounds. Each attribute of the result can be queried. If new criteria are to be queried, it is
recommended to create a new ProbeChecker that allows the ExperimentResult class to add an attribute
which can then be used for the filtering.
"""


class ResultsFilter:
    """Main class for filtering quantitative probing results.

    Attributes:
        filtered_results (list): A list of all results that passed the filtering process.
    """

    def __init__(self, results, attribute_name, lower_bound=None, upper_bound=None):
        self._results = results
        self._attribute_name = attribute_name
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    def filter_results(self):
        """Filters the results by checking for each result whether the attribute lies within the bounds."""
        self.filtered_results = [result for result in self._results if self._apply_filter_to_result(result)]

    def _apply_filter_to_result(self, result):
        self._attribute_val = getattr(result, self._attribute_name)
        return self._compare_attribute_val_to_bounds()

    def _compare_attribute_val_to_bounds(self):
        has_lower_bound = self._lower_bound is not None  # is not None is necessary because 0 evaluates to False
        has_upper_bound = self._upper_bound is not None
        if has_lower_bound and has_upper_bound:
            return self._lower_bound <= self._attribute_val <= self._upper_bound
        elif not has_lower_bound and has_upper_bound:
            return self._attribute_val <= self._upper_bound
        elif has_lower_bound and not has_upper_bound:
            return self._lower_bound <= self._attribute_val
        else:
            raise NoBoundsError("You must specify at least one bound (upper or lower) to filter the results.")


class NoBoundsError(Exception):
    pass
