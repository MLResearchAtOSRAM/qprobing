"""This module provides the main functionality for analyzing a single quantitative probing run.

Its structure is not yet finalized.
"""

import networkx as nx
from cause2e._graph import Graph
from qprobing.probe_checkers import TrivialityChecker, ConnectivityChecker


class ExperimentResult:
    """Main class for analyzing a single quantitative probing run.

    Its structure is not yet finalized.
    """

    def __init__(self, evaluator):
        self.evaluator = evaluator
        self._get_analysis_evaluator_info()
        self._graph_helper = _GraphHelper(self.true_graph, self.discovered_graph)
        self.true_n_connected_components = self._graph_helper.true_n_connected_components
        self._get_nontrivial_probes_info()
        self._get_connected_probes_info()

    @classmethod
    def from_result_dict(cls, result_dict):
        return cls(result_dict['evaluator'])

    def _get_analysis_evaluator_info(self):
        # TODO: ExperimentResults responsibilities should be taken over by AnalysisEvaluator
        self.treatment = self.evaluator.treatment
        self.outcome = self.evaluator.outcome
        self.n_nodes = self.evaluator.n_nodes
        self.true_graph = self.evaluator.true_graph
        self.discovered_graph = self.evaluator.discovered_graph
        self.correct_graph_found = self.evaluator.correct_graph_found
        self.n_edge_differences = self.evaluator.n_edge_differences
        self.effect_difference = self.evaluator.effect_difference
        self.target_effect = self.evaluator.target_effect
        self.relative_effect_difference = self.evaluator.relative_effect_difference
        self.probes = self.evaluator.probes
        self.hit_rate = self.evaluator.hit_rate

    def _get_nontrivial_probes_info(self):
        self._get_filtered_probes_info(TrivialityChecker, False)

    def _get_connected_probes_info(self):
        self._get_filtered_probes_info(
            checker_class=ConnectivityChecker,
            valid=True,
            graph_helper=self._graph_helper,
            target_treatment=self.treatment,
            target_outcome=self.outcome,
        )

    def _get_filtered_probes_info(self, checker_class, valid, **checker_kwargs):
        probes_filter = _ProbesFilter(self.probes, checker_class, valid, **checker_kwargs)
        probes_filter.filter_probes()
        descriptor = checker_class.descriptor
        self._unpack_filter_results(probes_filter, descriptor, valid)

    def _unpack_filter_results(self, probes_filter, descriptor, valid):
        if not valid:
            descriptor = f"non{descriptor}"
        setattr(self, f"{descriptor}_probes", probes_filter.filtered_probes)
        setattr(self, f"n_{descriptor}_probes", probes_filter.n_filtered_probes)
        setattr(self, f"{descriptor}_probes_ratio", probes_filter.filtered_probes_ratio)

    def show_true_graph(self, save_path=None):
        self._graph_helper.show_true_graph(save_path)

    def show_discovered_graph(self, save_path=None):
        self._graph_helper.show_discovered_graph(save_path)


class _GraphHelper:
    """Helper class for analyzing the result with respect to graphical criteria.

    Attributes:
        true_n_connected_components (int): The number of (weakly) connected components in the true graph.
    """
    def __init__(self, true_graph, discovered_graph):
        self._discovered_cause2e_graph = discovered_graph
        self._true_cause2e_graph = Graph.from_edges(directed_edges=set(true_graph.edges), undirected_edges=set())
        self._true_undirected_nx_graph = true_graph.to_undirected()
        self.true_n_connected_components = nx.number_connected_components(self._true_undirected_nx_graph)

    def are_connected(self, node1, node2):
        """Checks if two nodes are connected.

        Args:
            node1 (str): The name of the first node.
            node2 (str): The name of the second node.
        """
        return node1 in self._get_connected_nodes(node2)

    def _get_connected_nodes(self, node):
        return nx.node_connected_component(self._true_undirected_nx_graph, node)

    def show_true_graph(self, save_path=None):
        """Shows the true causal graph."""
        self._true_cause2e_graph.show()
        if save_path:
            self._true_cause2e_graph.save(save_path, 'png')

    def show_discovered_graph(self, save_path=None):
        """Shows the result that has been found as the result of causal discovery."""
        self._discovered_cause2e_graph.show()
        if save_path:
            self._discovered_cause2e_graph.save(save_path, 'png')


class _ProbesFilter:
    """Helper class for filtering quantitative probes by applying a check to each of them.

    Attributes:
        filtered_probes (dict): All of the original probes that passed the given check.
        n_filtered_probes (int): The number of probes that passed the given check.
        filtered_probes_ratio (float): The ratio of probes that passed the given check vs. all probes.
    """

    def __init__(self, probes, checker_class, valid, **checker_kwargs):
        self._probes = probes
        self._checker_class = checker_class
        self._valid = valid
        self._checker_kwargs = checker_kwargs

    def filter_probes(self):
        """Applies the filtering by applying the specified check to each probe."""
        self._get_filtered_probes()
        self._get_n_filtered_probes()
        self._get_filtered_probes_ratio()

    def _get_filtered_probes(self):
        self.filtered_probes = {k: v for k, v in self._probes.items() if self._check_probe(k, v)}

    def _check_probe(self, probe_key, probe_val):
        checker_instance = self._checker_class(probe_key, probe_val, **self._checker_kwargs)
        return checker_instance.check_probe() == self._valid

    def _get_n_filtered_probes(self):
        self.n_filtered_probes = len(self.filtered_probes)

    def _get_filtered_probes_ratio(self):
        self.filtered_probes_ratio = len(self.filtered_probes) / len(self._probes)
