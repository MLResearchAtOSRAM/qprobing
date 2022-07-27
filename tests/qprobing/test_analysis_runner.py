import pytest
import faulthandler
from qprobing.analysis_runner import AnalysisRunner


@pytest.mark.uses_jvm
def test_run_analysis(example_data_path, example_preparator):
    run_test_analysis(example_data_path, example_preparator, keep_vm=False)


@pytest.mark.skip(reason="Running discovery in a separate process makes this obsolete.")
def test_run_analysis_vm_timeout(example_data_path, example_preparator):
    with pytest.raises(RuntimeError):
        run_test_analysis(example_data_path, example_preparator, keep_vm=True)


def run_test_analysis(example_data_path, example_preparator, keep_vm=True):
    runner = AnalysisRunner.from_task_preparator(
        data_path=example_data_path,
        task_preparator=example_preparator,
    )
    faulthandler.disable()
    runner.run_analysis(keep_vm=keep_vm)
    faulthandler.enable()
    return runner


def test_constructor_equivalence(example_preparator):
    data_path = 'foo.csv'
    from_task_preparator = AnalysisRunner.from_task_preparator(
        data_path=data_path,
        task_preparator=example_preparator
    )
    from_default_constructor = AnalysisRunner(
        data_path=data_path,
        treatment=example_preparator.treatment,
        outcome=example_preparator.outcome,
        hints=example_preparator.hints,
        probes=example_preparator.probes,
    )
    # TODO: use this for data_generator and maybe implement it as __eq__ in the class itself?
    attribute_names = vars(from_task_preparator).keys() | vars(from_default_constructor).keys()
    for name in attribute_names:
        assert getattr(from_task_preparator, name) == getattr(from_default_constructor, name)


def test_bad_path(example_preparator):
    with pytest.raises(FileNotFoundError):
        _read_file(example_preparator, 'tests/qprobing/fixtures/nonsense.csv')


def test_string_path(example_preparator):
    learner = _read_file(example_preparator, 'tests/qprobing/fixtures/dag_data.csv')
    assert learner.data is not None


def _read_file(example_preparator, data_path):
    runner = AnalysisRunner.from_task_preparator(
        data_path=data_path,
        task_preparator=example_preparator,
    )
    runner._create_learner()
    learner = runner.learner
    assert learner.data is None
    learner.read_csv(index_col=0)
    return learner
