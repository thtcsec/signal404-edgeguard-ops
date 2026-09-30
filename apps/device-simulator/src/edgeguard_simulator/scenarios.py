from typing import Protocol

from edgeguard_simulator.models import ScenarioName, TelemetrySample


class Scenario(Protocol):
    """Future hook for deterministic fault injection."""

    name: ScenarioName

    def apply(self, sample: TelemetrySample) -> TelemetrySample:
        """Return a modified sample. Not implemented in the scaffold."""


class _UnimplementedScenario:
    def __init__(self, name: ScenarioName) -> None:
        self.name = name

    def apply(self, sample: TelemetrySample) -> TelemetrySample:
        raise NotImplementedError(
            f"Scenario {self.name.value} is not implemented. "
            "Fault simulation belongs to the 2026-10-10 to 2026-10-24 build window."
        )


def scenario_for(name: ScenarioName) -> Scenario:
    # TODO(build-window): return a deterministic generator for each scenario.
    return _UnimplementedScenario(name)
