import pytest


@pytest.fixture
def result(evaluator):
    return evaluator._valid_results[0]


def test_nontrivial_probes(result):
    assert result.n_nontrivial_probes < len(result.probes)


def test_nontrivial_probes_ratio(result):
    assert 0 < result.nontrivial_probes_ratio < 1
    assert result.nontrivial_probes_ratio < 0.3  # helps to see if triviality is inverted


def test_connected_probes_ratio(result):
    assert 0 < result.connected_probes_ratio < 1
    assert 0.3 < result.connected_probes_ratio < 0.4  # helps to see if connectivity is inverted


def test_true_n_connected_components(result):
    assert result.true_n_connected_components == 2


def test_show_true_graph(result):
    result.show_true_graph()


def test_show_discovered_graph(result):
    result.show_discovered_graph()
