import pytest
from qprobing.analysis_evaluator import AnalysisEvaluator
from test_analysis_runner import run_test_analysis


@pytest.mark.uses_jvm
def test_evaluate_analysis(example_data_path, example_preparator):
    runner = run_test_analysis(example_data_path, example_preparator, keep_vm=False)
    evaluator = AnalysisEvaluator.from_runner_and_preparator(runner, example_preparator)
    evaluator.evaluate_analysis(verbose=False)
