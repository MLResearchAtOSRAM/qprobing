"""
This module implements methods for evaluating the success of a causal analysis.

The evaluation includes several checks:
Has the true causal graph been recovered by the causal discovery algorithm?
Has the causal effect of interest been estimated correctly?
Do the estimates for known causal effects match our expectations?
"""


class AnalysisEvaluator:
    """
    Main class for evaluating the success of a causal analysis.

    Attributes:
        correct_graph: A boolean indicating whether the learner has found the true causal
            graph during causal discovery.
        edge_difference: A set containing all the edges that are in the true graph and not in the
            discovered graph, or the other way around.
        effect_difference: A float indicating the difference between the estimated target effect and
            the true target effect.
        effect_learner: A float indicating the learner's estimate of the target effect.
        effect_pgmpy: A float indicating the true target effect. The true value is calculated by
            explicit calculation of the different intervention distributions in the Bayesian
            Network.
        validations: A dictionary containing all/passed/failed validations of the learner.
        validation_counts: A dictionary containing the number of all/passed/failed validations of
            the learner.
        hit_rate: A float indicating the success rate of the validations.
    """
    def __init__(self, learner, nx_graph, treatment, outcome, target_effect):
        self._graph_checker = _GraphChecker(learner, nx_graph)
        self._target_effect_checker = _TargetEffectChecker(learner, treatment, outcome, target_effect)
        self._validation_checker = _ValidationChecker(learner)
        self.target_effect = target_effect

    @classmethod
    def from_runner_and_preparator(cls, runner, preparator):
        return cls(
            learner=runner.learner,
            nx_graph=preparator._nx_graph,
            treatment=preparator.treatment,
            outcome=preparator.outcome,
            target_effect=preparator.target_effect,
        )

    def evaluate_analysis(self, verbose):
        """Evaluates the success of a causal analysis.

        Args:
            verbose: optional; A boolean indicating whether the results should be displayed.
        """
        self._check_graph(verbose)
        self._check_target_effect(verbose)
        self._check_validations()

    def _check_graph(self, verbose):
        self._graph_checker.check_graph(verbose)
        self.n_nodes = self._graph_checker.n_nodes
        self.discovered_graph = self._graph_checker.discovered_graph
        self.true_graph = self._graph_checker.true_graph
        self.correct_graph_found = self._graph_checker.correct_graph_found
        self.edge_difference = self._graph_checker.edge_difference
        self.n_edge_differences = self._graph_checker.n_edge_differences

    def _check_target_effect(self, verbose):
        self._target_effect_checker.check_target_effect(verbose)
        self.treatment = self._target_effect_checker.treatment
        self.outcome = self._target_effect_checker.outcome
        self.effect_learner = self._target_effect_checker.effect_learner
        self.effect_difference = self._target_effect_checker.effect_difference
        self.absolute_effect_difference = self._target_effect_checker.absolute_effect_difference
        self.relative_effect_difference = self._target_effect_checker.relative_effect_difference

    def _check_validations(self):
        self._validation_checker.check_validations()
        self.validations = self._validation_checker.validations
        self.validation_counts = self._validation_checker.validation_counts
        self.probes = self._validation_checker.probes
        self.hit_rate = self._validation_checker.hit_rate


class _GraphChecker:
    """
    Helper class for evaluating the success of the causal discovery procedure.

    Attributes:
        correct_graph: A boolean indicating whether the learner has found the true causal
            graph during causal discovery.
        edge_difference: A set containing all the edges that are in the true graph and not in the
            discovered graph, or the other way around.
    """
    def __init__(self, learner, nx_graph):
        self.n_nodes = len(learner.variables)
        self.discovered_graph = learner.graph
        self.true_graph = nx_graph  # TODO: graphs should not be stored in different formats
        self._discovered_edges = learner.graph.edges
        self._true_edges = set(nx_graph.edges)

    def check_graph(self, verbose):
        """Evaluates the success of the causal discovery procedure.

        Args:
            verbose: optional; A boolean indicating whether the results should be displayed.
        """
        self.edge_difference = self._discovered_edges ^ self._true_edges
        self.n_edge_differences = len(self.edge_difference)
        self.correct_graph_found = not self.edge_difference
        if verbose:
            self._show_graph_analysis()

    def _show_graph_analysis(self):
        print(f"Correct graph: {self.correct_graph_found}.")
        print("Differing edges:")
        for edge in self.edge_difference:
            print(edge)


class _TargetEffectChecker:
    """
    Helper class for evaluating the estimation of the target causal effect.

    Attributes:
        effect_difference: A float indicating the difference between the estimated target effect and
            the true target effect.
        effect_learner: A float indicating the learner's estimate of the target effect.
        effect_pgmpy: A float indicating the true target effect. The true value is calculated by
            explicit calculation of the different intervention distributions in the Bayesian
            Network.
    """
    def __init__(self, learner, treatment, outcome, target_effect):
        self.treatment = treatment
        self.outcome = outcome
        self.target_effect = target_effect
        self.effect_learner = self._get_effect_learner(learner)

    def check_target_effect(self, verbose):
        """Evaluates the success of the estimation of the target causal effect.

        Args:
            verbose: optional; A boolean indicating whether the results should be displayed.
        """
        self.effect_difference = self.effect_learner - self.target_effect
        self.absolute_effect_difference = abs(self.effect_difference)
        self.relative_effect_difference = abs(self.effect_difference / self.target_effect)
        if verbose:
            self._show_target_effect_analysis()

    def _get_effect_learner(self, learner):
        return learner._estimator.get_quick_result_estimate(
            treatment=self.treatment,
            outcome=self.outcome,
            estimand_type='nonparametric-ate',
        )

    def _show_target_effect_analysis(self):
        print(f"Estimated: {self.effect_learner}. True: {self.target_effect}. Difference: {self.effect_difference}.")


class _ValidationChecker:
    """
    Helper class for evaluating the success of the causal validations.

    Attributes:
        validations: A dictionary containing all/passed/failed validations of the learner.
        validation_counts: A dictionary containing the number of all/passed/failed validations of
            the learner.
        hit_rate: A float indicating the success rate of the validations.
    """
    def __init__(self, learner):
        self._get_validations(learner)

    def check_validations(self):
        """Evaluates the success of the causal validations.

        Args:
            verbose: optional; A boolean indicating whether the results should be displayed.
        """
        self._get_validation_counts()
        self._get_hit_rate()

    def _get_validations(self, learner):
        self.validations = {}
        self.validations['all'] = learner._estimator._result_mgr._validation_dict
        self.probes = self.validations['all']
        self.validations['pass'] = self._get_filtered_validations(True)
        self.validations['fail'] = self._get_filtered_validations(False)

    def _get_filtered_validations(self, valid):
        return {k: v for k, v in self.validations['all'].items() if v['Valid'] == valid}

    def _get_validation_counts(self):
        filters = {'all', 'pass', 'fail'}
        self.validation_counts = {filter: len(self.validations[filter]) for filter in filters}

    def _get_hit_rate(self):
        self.hit_rate = self.validation_counts['pass'] / self.validation_counts['all']
