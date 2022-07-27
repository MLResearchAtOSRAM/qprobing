"""
This module implements methods to prepare the task for a quantitative probing run.

By task, we mean the target causal effect, the probes (both determined by treatment and outcome, as
we currently can only deal with ATEs) and their tolerance, as well as the qualitative domain
knowledge (only present edges are currently supplied, not absent edges or temporal orders).
"""

import random
import itertools
import networkx as nx
from qprobing.pgmpy_causality import calculate_effect


class TaskPreparator:
    """ Main class for preparing the task.

    Attributes:
        treatment: A string indicating the treatment variable for the target causal effect.
        outcome: A string indicating the outcome variable for the target causal effect.
        target_effect: A float indicating the value of the target causal effect.
        hints: A set of edges from the true graph that are passed as domain knowledge to the
             learner.
        probes: A set of target effects that are used for quantitative probing.
    """
    def __init__(self, model, nx_graph, n_samples=1000):
        # TODO: Why pass the graph when the model already holds the structural information?
        self._model = model
        self._nx_graph = nx_graph
        self._n_samples = 1000

    @property
    def _n_variables(self):
        return len(self._model.nodes)

    def prepare_task(self, p_hint, p_probe, tolerance):
        """Prepares target causal effect, edge hints and probes for the analysis.

        Args:
            p_hint (float): The probability for each edge in the true causal graph to be provided as
                a hint to the causal discovery procedure.
            p_probe (float): The probability for each possible causal effect to be selected as a
                validation probe.
            tolerance (float): The tolerance in validating the quantitative probes: By how much can
                the estimated effect deviate from the true effect without failing the validation
                test?
        """
        self.treatment, self.outcome = self._get_random_treatment_and_outcome(nontrivial=True)
        self.target_effect = calculate_effect(self._model, self.treatment, self.outcome, self._n_samples)
        self._prepare_hints(p_hint)
        self._prepare_probes(p_probe, tolerance)

    def _get_random_treatment_and_outcome(self, nontrivial=True):
        nx_nodes = list(self._nx_graph.nodes)
        while True:
            treatment, outcome = random.sample(nx_nodes, 2)
            is_trivial = self._check_trivial_effect(treatment, outcome)
            if not (nontrivial and is_trivial):
                break
        return treatment, outcome

    def _check_trivial_effect(self, treatment, outcome):
        if treatment == outcome:
            return True
        else:
            return not nx.has_path(self._nx_graph, treatment, outcome)

    def _prepare_hints(self, p_hint):
        edges = list(self._model.edges)
        n_hints = int(p_hint * len(edges))
        self.hints = set(random.sample(edges, n_hints))

    def _prepare_probes(self, p_probe, tolerance):
        # TODO: Do we have to adapt p_probe wrt to nontrivial effects? Yes, otherwise endless loop
        n_probes = int(p_probe * self._n_variables**2)
        probe_specs = self._get_probe_specs(n_probes)
        self.probes = {self._create_probe_from_spec(spec, tolerance) for spec in probe_specs}

    def _get_probe_specs(self, n_probes):
        possible_specs = self._create_possible_probe_specs(nontrivial=False)
        return set(random.sample(possible_specs, n_probes))

    def _create_possible_probe_specs(self, nontrivial=False):
        all_possible_specs = self._create_all_possible_probe_specs()
        if nontrivial:
            return self._select_nontrivial_probe_specs(all_possible_specs)
        else:
            return all_possible_specs

    def _create_all_possible_probe_specs(self):
        nx_nodes = list(self._nx_graph.nodes)
        return set(itertools.product(nx_nodes, nx_nodes))

    def _select_nontrivial_probe_specs(self, candidate_specs):
        return {spec for spec in candidate_specs if not self._check_trivial_effect(*spec)}

    def _create_probe_from_spec(self, spec, tolerance):
        treatment, outcome = spec
        effect = calculate_effect(self._model, treatment, outcome, self._n_samples)
        lower_bound = effect - tolerance
        upper_bound = effect + tolerance
        return ((treatment, outcome, 'nonparametric-ate'), ('between', lower_bound, upper_bound))
