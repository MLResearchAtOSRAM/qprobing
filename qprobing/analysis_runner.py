"""
This module implements methods for running an end-to-end causal analysis for quantitative probing.

It runs the standard version of an analysis with the goal of estimating a target causal effect as
well as some other effects that are used for quantitative probing.
"""

import pathlib
import contextlib
from cause2e import path_mgr, knowledge
from qprobing.custom_cause2e import CustomLearner


class AnalysisRunner:
    """Main class for running the end-to-end causal analysis.

    Attributes:
        learner: A cause2e.discovery.StructureLearner that is used to perform the analysis.
    """
    def __init__(self, data_path, treatment, outcome, hints=set(), probes=set()):
        self._treatment = treatment
        self._outcome = outcome
        self._hints = hints
        self._probes = probes
        self._data_path = data_path

    @classmethod
    def from_task_preparator(cls, data_path, task_preparator):
        return cls(
            data_path=data_path,
            treatment=task_preparator.treatment,
            outcome=task_preparator.outcome,
            hints=task_preparator.hints,
            probes=task_preparator.probes,
        )

    def run_analysis(self, keep_vm=True):
        """Runs the end-to-end causal analysis.

        Args:
            keep_vm (bool, optional): Determines whether we want to keep the Java VM alive. Defaults to True.
        """
        self._create_learner()
        self.learner.read_csv(index_col=0)
        self._specify_datatypes()
        self._specify_knowledge()
        with contextlib.redirect_stdout(None):
            self.learner.run_quick_search(
                verbose=False,
                show_graph=False,
                save_graph=False,
                keep_vm=keep_vm
            )
        self.learner.orient_all_edges(verbose=False)
        self._run_selected_estimations()

    def _create_learner(self):
        data_dir, data_name = self._split_data_path()
        paths = path_mgr.PathManager(experiment_name='random_dag',
                                     data_name=data_name,
                                     data_dir=data_dir,
                                     output_dir='./output/random_dag'  # TODO: Output dir should be free
                                     )
        self.learner = CustomLearner(paths)

    def _split_data_path(self):
        self._sanitize_data_path()
        directory = self._data_path.parent
        filename = self._data_path.name
        return directory, filename

    def _sanitize_data_path(self):
        if isinstance(self._data_path, str):
            self._data_path = pathlib.Path(self._data_path)

    def _specify_datatypes(self):
        self.learner.discrete = self.learner.variables
        self.learner.continuous = set()

    def _specify_knowledge(self):
        edge_creator = self._get_edge_creator()
        validation_creator = self._get_validation_creator()
        self.learner.set_knowledge(
            edge_creator=edge_creator,
            validation_creator=validation_creator,
            show=False,
            save=False,
        )

    def _get_edge_creator(self):
        edge_creator = knowledge.EdgeCreator()
        for hint in self._hints:
            edge_creator.require_edge(*hint)
        return edge_creator

    def _get_validation_creator(self):
        validation_creator = knowledge.ValidationCreator()
        for probe in self._probes:
            validation_creator.add_expected_effect(*probe)
        return validation_creator

    def _run_selected_estimations(self):
        self.learner._create_estimator()
        for treatment, outcome in self._collect_effects_of_interest():
            self.learner._estimator.run_quick_analysis(
                treatment=treatment,
                outcome=outcome,
                estimand_type='nonparametric-ate',
                robustness_method=None,
                verbose=False,
            )
            effect = (treatment, outcome, 'nonparametric-ate')
            self.learner._estimator._result_mgr.validate_effect(effect)

    def _collect_effects_of_interest(self):
        probe_specs = {self._get_treatment_and_outcome_from_probe(probe) for probe in self._probes}
        target_spec = (self._treatment, self._outcome)
        return probe_specs | {target_spec}

    @staticmethod
    def _get_treatment_and_outcome_from_probe(probe):
        return probe[0][0:2]
