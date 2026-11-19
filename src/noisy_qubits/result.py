"""The shared format every algorithm returns (Member 1: extend as needed)."""
from __future__ import annotations

from dataclasses import dataclass, field

from qiskit import QuantumCircuit


@dataclass
class AlgorithmResult:
    name: str
    circuit: QuantumCircuit
    counts: dict[str, int]
    shots: int
    ideal_score: float          # theory value for a noise-free run
    baseline: float             # classical baseline
    score: float                # measured score
    meta: dict = field(default_factory=dict)

    @property
    def normalized(self) -> float:
        """(measured - baseline) / (ideal - baseline); PASS if >= T (plan 8.2)."""
        return (self.score - self.baseline) / (self.ideal_score - self.baseline)
