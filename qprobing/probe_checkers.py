""" This module provides the main functionality for checking if a quantitative probe fulfills some
criterion. This tool can be used to filter out uninteresting quantitative probing runs.

Currently implemented are:
- Checking if a probes is "trivial", in the sense that either there is no path from treatment to
  outcome (trivially zero), or treatment and outcome are identical (trivially 1).
- Checking if a probe is "connected", in the sense that both, probe treatment and probe outcome, are
  each connected to both, target effect treatment and target effect outcome.
"""

from abc import ABC, abstractmethod


class ProbeChecker(ABC):
    """Abstract base class for checking a probe.

    Attributes:
        descriptor (string): Describes the type of check.
    """

    descriptor: str

    def __init__(self, probe_key, probe_val):
        self._probe_key = probe_key
        self._probe_val = probe_val

    @abstractmethod
    def check_probe(self):
        """Implementing the check is the task of the child classes."""
        pass


class TrivialityChecker(ProbeChecker):
    """Main class for checking if a probe is trivial."""

    descriptor = 'trivial'

    def check_probe(self):
        """Checks if a probes is trivial.

        Trivial means that either there is no path from treatment to outcome (trivially zero), or
        treatment and outcome are identical (trivially 1).
        """
        return self._get_expected_lower_bound() in {0.9, -0.1}

    def _get_expected_lower_bound(self):
        return self._probe_val['Expected'][1]


class ConnectivityChecker(ProbeChecker):
    """Main class for checking if a probe is connected to the target effect."""

    descriptor = 'connected'

    def __init__(self, probe_key, probe_val, target_treatment, target_outcome, graph_helper):
        super().__init__(probe_key, probe_val)
        self._target_treatment = target_treatment
        self._target_outcome = target_outcome
        self._graph_helper = graph_helper

    def check_probe(self, verbose=False):
        """Checks if a probe is connected to the target effect.

        This means that both, probe treatment and probe outcome, are each connected to both, target
        effect treatment and target effect outcome.
        """

        probe_treatment = self._get_treatment()
        probe_outcome = self._get_outcome()
        if not self._graph_helper.are_connected(probe_treatment, self._target_treatment):
            if verbose:
                print('Probe treatment is not connected to target treatment!')
            return False
        if not self._graph_helper.are_connected(probe_treatment, self._target_outcome):
            if verbose:
                print('Probe treatment is not connected to target outcome!')
            return False
        if not self._graph_helper.are_connected(probe_outcome, self._target_treatment):
            if verbose:
                print('Probe outcome is not connected to target treatment!')
            return False
        if not self._graph_helper.are_connected(probe_outcome, self._target_outcome):
            if verbose:
                print('Probe outcome is not connected to target outcome!')
            return False
        return True

    def _get_treatment(self):
        return self._probe_key[0]

    def _get_outcome(self):
        return self._probe_key[1]
