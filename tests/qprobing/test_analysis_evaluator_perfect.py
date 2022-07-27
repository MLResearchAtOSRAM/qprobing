import pytest
from qprobing.analysis_evaluator import AnalysisEvaluator
from qprobing.task_preparator import TaskPreparator
from qprobing.analysis_runner import AnalysisRunner


@pytest.mark.uses_jvm
def test_evaluate_perfect_analysis(example_data_path, example_model, example_nx_graph):
    preparator = TaskPreparator(example_model, example_nx_graph)
    preparator.prepare_task(
        p_hint=1.0,
        p_probe=0.5,
        tolerance=0.1,
    )
    runner = AnalysisRunner.from_task_preparator(
        data_path=example_data_path,
        task_preparator=preparator,
    )
    runner.run_analysis(keep_vm=False)
    evaluator = AnalysisEvaluator.from_runner_and_preparator(runner, preparator)
    evaluator.evaluate_analysis(verbose=True)
    assert evaluator.correct_graph_found
    assert not evaluator.edge_difference
    assert evaluator.effect_difference < 0.1
    assert not evaluator.validation_counts['fail']
    assert evaluator.hit_rate == 1
