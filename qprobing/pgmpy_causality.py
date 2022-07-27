"""This module provides the main functionality for determining causal effects from a model and/or data."""

from abc import ABC, abstractmethod
from pgmpy.inference import CausalInference
from pgmpy.models import BayesianNetwork
import networkx as nx


def calculate_effect(model, treatment, outcome, n_samples=None):
    calculator = EffectCalculator(model, treatment, outcome, n_samples)
    return calculator.determine_effect()


def simulate_effect(model, treatment, outcome, n_samples):
    simulator = EffectSimulator(model, treatment, outcome, n_samples)
    return simulator.determine_effect()


class EffectDeterminator(ABC):
    """Abstract Base Class for determining causal effects. Method is up to the subclasses.

    Attributes:
        model: The pgmpy.BayesianNetwork used for data generation.
        treatment: A string indicating the treatment variable of the target causal effect.
        outcome: A string indicating the outcome variable of the target causal effect.
    """
    model: BayesianNetwork
    treatment: str
    outcome: str

    def determine_effect(self):
        """Determines the causal effect."""
        if self._effect_is_trivial_one():
            return 1
        if self._effect_is_trivial_zero():
            return 0
        return self._determine_nontrivial_effect()

    def _effect_is_trivial_zero(self):
        return not nx.has_path(self.model, self.treatment, self.outcome)

    def _effect_is_trivial_one(self):
        return self.treatment == self.outcome

    def _determine_nontrivial_effect(self):
        interventional_means = {
            do_value: self._determine_interventional_mean(do_value)
            for do_value in {0, 1}
        }
        return interventional_means[1] - interventional_means[0]

    @abstractmethod
    def _determine_interventional_mean(self, do_value):
        pass


class EffectCalculator(EffectDeterminator):
    """Main class for analytically calculating causal effects with pgmpy.

    Attributes:
        model: The pgmpy.BayesianNetwork used for data generation.
        treatment: A string indicating the treatment variable of the target causal effect.
        outcome: A string indicating the outcome variable of the target causal effect.
        n_samples: An integer indicating the number of simulation samples to be used when
            calculation is no possible.
    """
    def __init__(self, model, treatment, outcome, n_samples=None):
        self.model = model
        self.treatment = treatment
        self.outcome = outcome
        self.n_samples = n_samples

    def _determine_interventional_mean(self, do_value):
        # pgmpy contains a bug that should be fixed in the next release
        # appears when there is no direct edge between treatment and outcome
        if self._effect_is_problematic():
            return self._use_simulation_fallback(do_value)
        else:
            return self._determine_unproblematic_interventional_mean(do_value)

    def _effect_is_problematic(self):
        return not self._effect_is_trivial_zero() and not self._effect_is_trivial_one() and not self._has_direct_edge()

    def _has_direct_edge(self):
        return (self.treatment, self.outcome) in set(self.model.edges)

    def _use_simulation_fallback(self, do_value):
        print(
            f"Using simulation fallback with {self.n_samples} samples for effect of {self.treatment} "
            f"on {self.outcome} to avoid pgmpy bug."
        )
        if not self.n_samples:
            raise SimulationFallbackError("Fallback not possible since no sample size was speficied at initialization.")
        else:
            simulator = EffectSimulator(self.model, self.treatment, self.outcome, self.n_samples)
            return simulator._determine_interventional_mean(do_value)

    def _determine_unproblematic_interventional_mean(self, do_value):
        infer_adjusted = CausalInference(self.model)
        query_result = infer_adjusted.query(
            variables=[self.outcome],
            do={self.treatment: do_value},
            show_progress=False
        )
        return query_result.values[1]


# simulation recovery could be a fairer benchmark for cause2e estimation
class EffectSimulator(EffectDeterminator):
    """Main class for determining causal effects by simulation with pgmpy.

    Attributes:
        model: The pgmpy.BayesianNetwork used for data generation.
        treatment: A string indicating the treatment variable of the target causal effect.
        outcome: A string indicating the outcome variable of the target causal effect.
        n_samples: An integer indicating the number of simulation samples to be used.
    """
    def __init__(self, model, treatment, outcome, n_samples):
        self.model = model
        self.treatment = treatment
        self.outcome = outcome
        self.n_samples = n_samples

    def _determine_interventional_mean(self, do_value):
        samples = self.model.simulate(
            n_samples=self.n_samples,
            do={self.treatment: do_value},
            show_progress=False,
        )
        return self._mean_from_simulated_samples(samples, self.outcome)

    @staticmethod
    def _mean_from_simulated_samples(samples, var_name):
        target_col = samples[var_name]
        ones = target_col.value_counts()[1]
        return ones / len(samples)


class SimulationFallbackError(Exception):
    """Exception that is raised when simulation fallback is not enabled, but calculation fails."""
    pass
