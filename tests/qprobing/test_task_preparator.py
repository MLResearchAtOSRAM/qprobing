import pytest
from qprobing.task_preparator import TaskPreparator


@pytest.fixture
def example_preparator(example_model, example_nx_graph):
    return TaskPreparator(example_model, example_nx_graph)


def test_prepare_task(example_preparator):
    example_preparator.prepare_task(
        p_hint=0.5,
        p_probe=0.5,
        tolerance=0.1,
    )
    assert example_preparator.hints
    assert example_preparator.probes


def test_prepare_task_full_knowledge(example_preparator):
    example_preparator.prepare_task(
        p_hint=1,
        p_probe=1,
        tolerance=0.1,
    )
    assert _all_edges_known(example_preparator)
    assert _all_probes_selected(example_preparator)


def _all_edges_known(task_preparator):
    return len(task_preparator.hints) == len(task_preparator._model.edges)


def _all_probes_selected(task_preparator):
    return len(task_preparator.probes) == len(task_preparator._model.nodes) ** 2


def test_prepare_task_no_knowledge(example_preparator):
    example_preparator.prepare_task(
        p_hint=0,
        p_probe=0,
        tolerance=0.1,
    )
    assert _no_edges_known(example_preparator)
    assert _no_probes_selected(example_preparator)


def _no_edges_known(task_preparator):
    return not task_preparator.hints


def _no_probes_selected(task_preparator):
    return not task_preparator.probes


def test_prepare_task_too_many_hints(example_preparator):
    with pytest.raises(ValueError):
        example_preparator.prepare_task(
            p_hint=2,
            p_probe=0.5,
            tolerance=0.1,
        )
    assert not hasattr(example_preparator, 'hints')
    assert not hasattr(example_preparator, 'probes')


def test_prepare_task_too_many_probes(example_preparator):
    with pytest.raises(ValueError):
        example_preparator.prepare_task(
            p_hint=0.5,
            p_probe=2,
            tolerance=0.1,
        )
    assert example_preparator.hints
    assert not hasattr(example_preparator, 'probes')
    example_preparator.prepare_task(
        p_hint=0,
        p_probe=0.5,
        tolerance=0.1,
    )
    assert not example_preparator.hints  # no remains of failed preparation interfere with new preparation
    assert example_preparator.probes
