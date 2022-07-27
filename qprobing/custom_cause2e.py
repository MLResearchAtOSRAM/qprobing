"""This module extends cause2e functionality to match the needs of our experiments."""

from cause2e import discovery, estimator


class CustomLearner(discovery.StructureLearner):
    """Custom version of the cause2e.discovery.StructureLearner.

    Added functionality:
        - Passing result of the causal discovery to the estimator without saving to a file.
        - Orienting all unoriented edges after causal discovery randomly.
    """
    def _create_estimator(self):
        self._estimator = CustomEstimator.from_learner(self, same_data=True)
        self._estimator._dot_str = self._reformat_dot(str(self.graph.dot))

    def _reformat_dot(self, dot_str):
        front = "digraph {"
        end = "}"
        edges = self._get_edges(dot_str)
        return front + ";".join(edges) + end

    def _get_edges(self, dot_str):
        graph_particles = dot_str.replace("\n", " ").replace("G", " ").split(" ")
        edges = []
        for i, particle in enumerate(graph_particles):
            if particle in {'->', '<-'}:  # Assumes that undirected edges have been oriented
                edges.append(" ".join([graph_particles[i - 1], particle, graph_particles[i + 1]]))
        return edges

    def orient_all_edges(self, verbose=False):
        """Orients all unoriented edges randomly.

        Args:
            verbose: A boolean indicating whether the undirected edges should be printed.
        """
        undirected_edges = list(self.graph.undirected_edges)
        if verbose:
            print(undirected_edges)
        for edge in undirected_edges:
            self.add_edge(*edge, show=False)


class CustomEstimator(estimator.Estimator):
    """Custom version of the cause2e.estimator.Estimator.

    Added functionality:
        -
    """
    @property
    def _dot_name(self):
        return self._dot_str
