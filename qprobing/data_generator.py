"""
This module provides methods for generating random binary data from a given causal graph.

The graph is used to build a Bayesian Network in pgmpy and the corresponding conditional probability
distributions (CPDs) are initialized randomly. The fully parameterized network can then be used to
sample data points according to the specified distribution. The results can be written to a csv file
for futher processing.
"""

import numpy as np
import networkx as nx
from pgmpy.factors.discrete import TabularCPD
from pgmpy.models import BayesianNetwork
from qprobing.dag_generator import DagGenerator, get_nodes_from_edges


class DataGenerator:
    """
    Main class for generating random data from a given causal graph.

    Isolated nodes are not supported.
    Parameters of the binary cpds are initialized randomly.

    Attributes:
        edges: A set indicating the edges of the causal graph.
        nodes: A set indicating the nodes of the causal graph.
        model: A pgmpy.BayesianNetwork built from the causal graph and random cpds.
        data: A pandas.DataFrame with simulated data from the model.
    """
    def __init__(self, edges):
        self.edges = edges
        self.nodes = get_nodes_from_edges(edges)
        self.nx_graph = nx.DiGraph(edges)

    @classmethod
    def from_nx_graph(cls, nx_graph):
        """Alternative constructor using a networkx graph."""
        return cls(set(nx_graph.edges))

    @classmethod
    def from_scratch(cls, n_vars, p_edge, dag_seed, show=False):
        dag_generator = DagGenerator(
            n_vars=n_vars,
            p_edge=p_edge,
            seed=dag_seed,
        )
        dag_generator.create_random_dag(show=show)
        return cls.from_nx_graph(dag_generator.nx_graph)

    def create_random_model(self, seed=None):
        """Creates a Bayesian Network with random cpds.

        Args:
            seed: optional; An integer indicating the seed for creating cpds. Defaults to None.
        """
        self.model = BayesianNetwork(self.edges)
        cpds = self._create_random_binary_cpds(seed=seed)
        self.model.add_cpds(*cpds)

    def _create_random_binary_cpds(self, seed=None):
        return {self._create_random_binary_cpd(node, seed) for node in self.nodes}

    def _create_random_binary_cpd(self, node, seed=None):
        vals = self._get_vals(node, seed)
        parents = self._get_parents(node)
        return create_binary_cpd(node, vals, parents)

    def _get_vals(self, node, seed=None):
        parents = self._get_parents(node)
        np.random.seed(seed)  # is this problematic?
        return np.random.uniform(0, 1, 2 ** len(parents))

    def _get_parents(self, node):
        return {source for source, dest in self.edges if dest == node}

    def generate_data(self, n_samples, seed=None, save_to_file=None):
        """Generated simulated data from the model.

        Args:
            n_samples: An integer indicating the number of samples to be generated.
            seed: optional; An integer indicating the seed for data generation. Defaults to None.
            save_to_file: optional; A string indicating the name of the csv file for saving.
                Defaults to None.

        Raises:
            MissingModelError
        """
        if not hasattr(self, 'model'):
            raise MissingModelError('You have to create a model before you can generate data from it.')
        self.data = self.model.simulate(n_samples=n_samples, seed=seed, show_progress=False)
        if save_to_file:
            self.data.to_csv(save_to_file)


def create_binary_cpd(node, vals, parents):
    return TabularCPD(
        variable=node,
        variable_card=2,
        values=[
            [1 - val for val in vals],
            vals,
        ],
        evidence=parents,
        evidence_card=[2 for _ in parents]
    )


class MissingModelError(Exception):
    pass
