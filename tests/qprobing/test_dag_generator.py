import pytest
from qprobing.dag_generator import DagGenerator, get_nodes_from_edges, IsolatedNodeError


@pytest.fixture
def edges():
    return {
        ('a', 'b'),
        ('b', 'c'),
    }


# @pytest.mark.parametrize("edges_, expected_nodes", [
#     (edges, {'a', 'b', 'c'}),
#     (edges - {('b', 'c')}, {'a', 'b'})
# ]
# )
def test_get_nodes_from_edges(edges):
    expected_nodes = {'a', 'b', 'c'}
    extracted_nodes = get_nodes_from_edges(edges)
    assert expected_nodes == extracted_nodes


def test_get_nodes_from_edges_isolated(edges):
    reduced_edges = edges - {('b', 'c')}
    expected_nodes = {'a', 'b'}
    extracted_nodes = get_nodes_from_edges(reduced_edges)
    assert expected_nodes == extracted_nodes


@pytest.fixture
def dag_generator():
    return DagGenerator(n_vars=5, p_edge=0.1, seed=1, max_count=100)


def test_create_random_dag(dag_generator):
    dag_generator.create_random_dag(force_n_vars=True, show=False)
    assert dag_generator.n_vars == len(dag_generator.nodes)


def test_create_random_dag_allow_isolated(dag_generator):
    dag_generator.create_random_dag(force_n_vars=False, show=False)
    with pytest.raises(IsolatedNodeError):
        dag_generator._check_isolated_nodes()
    assert dag_generator.n_vars > len(dag_generator.nodes)
