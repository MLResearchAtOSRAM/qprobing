"""
This module provides methods for generating random directed acyclic graphs (DAGs).

The graphs are constructed as Erdos Renyi graphs: a number of nodes and an edge probability is
specified, which determines the probability of an edge being present between any pair of nodes.
"""

import networkx as nx
import networkx.generators.random_graphs as rg
from cause2e import _graph


class DagGenerator:
    """
    Main class for graph generation via Erdos Renyi graphs.

    Attributes:
        n_vars: An integer indicating the desired number of nodes. The actual number of nodes can be
            smaller due to isolated nodes being filtered out.
        p_edge: A float indicating the probability of having an edge between any two nodes.
        seed: An integer indicating the seed for random edge generation.
        dag_tries: An integer indicating how many tries were necessary to get an acyclic graph.
        nx_graph: A networkx graph storing the generated random graph.
        edges: A set containing the edges of the generated graph.
        nodes: A set containing the nodes of the generated graph.
    """
    def __init__(self, n_vars, p_edge, seed=None, max_count=100):
        self.n_vars = n_vars
        self.p_edge = p_edge
        self.seed = seed
        self.max_count = max_count

    def exception_handler(func):
        def inner_function(*args, **kwargs):
            count = 0
            success = False
            self = args[0]
            self.cyclic_graph_errors = 0
            self.isolated_node_errors = 0
            while not success and count < self.max_count:
                count += 1
                if self.seed:
                    self.seed += 1  # TODO: Is it ok to shift the seed up? Analyze how many subsequent dags are the same
                try:
                    func(*args, **kwargs)
                except CyclicGraphError:
                    self.cyclic_graph_errors += 1
                except IsolatedNodeError:
                    self.isolated_node_errors += 1
                else:  # What if other errors happen?
                    success = True
            if not success:
                raise TooManyAttemptsError(f"No success in random dag generation after {self.max_count} attempts.")
        return inner_function

    @exception_handler
    def create_random_dag(self, force_n_vars=True, show=True):
        """Creates a random directed acyclic graph.

        Args:
            show: A boolean indicating if the graph should be shown. Defaults to True.
        """
        nx_graph = rg.erdos_renyi_graph(self.n_vars, self.p_edge, seed=self.seed, directed=True)
        self._postprocess_nx_graph(nx_graph, force_n_vars=force_n_vars)
        if show:
            self.show_graph()

    def _postprocess_nx_graph(self, nx_graph, force_n_vars=True):
        self._extract_graph_attributes(nx_graph)
        self._check_nx_graph(force_dag=True, force_n_vars=force_n_vars)

    def _extract_graph_attributes(self, nx_graph):
        mapping = {node: f"x{node}" for node in nx_graph.nodes}
        self.nx_graph = nx.relabel.relabel_nodes(nx_graph, mapping)
        self.edges = set(self.nx_graph.edges)
        self.nodes = get_nodes_from_edges(self.edges)

    def _check_nx_graph(self, force_dag=True, force_n_vars=True):
        if force_dag:
            self._check_acyclicity()
        if force_n_vars:
            self._check_isolated_nodes()

    def _check_acyclicity(self):
        if not nx.is_directed_acyclic_graph(self.nx_graph):
            msg = 'The graph is not acyclic.'
            raise CyclicGraphError(msg)

    def _check_isolated_nodes(self):
        self.isolated_nodes = not len(self.nodes) == self.n_vars
        if self.isolated_nodes:
            msg = 'The number of non-isolated nodes is smaller than the desired number of variables.'
            raise IsolatedNodeError(msg)

    def show_graph(self):
        """Shows the graph."""
        cause2e_graph = _graph.Graph.from_edges(directed_edges=self.edges, undirected_edges=set())
        cause2e_graph.show()


def get_nodes_from_edges(edges):
    """Returns a set with a graph's non-isolated nodes from its edges.

    Args:
        edges: A set indicating the edges of the graph.
    """
    nodes = set()
    for source, dest in edges:
        nodes |= {source, dest}
    return nodes


class IsolatedNodeError(Exception):
    pass


class CyclicGraphError(Exception):
    pass


class TooManyAttemptsError(Exception):
    pass
