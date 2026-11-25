"""Error mitigation: zero-noise extrapolation (Member 5). See docs/noise-contract.md."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from qiskit import QuantumCircuit


@dataclass
class ZNEResult:
    factors: tuple[int, ...]
    scores: list[float]   # score at each noise factor
    mitigated: float      # extrapolated score at noise 0
    raw: float            # score at factor 1


def zne(
    circuit: QuantumCircuit,
    noise_model,
    shots: int,
    score_fn: Callable[[dict[str, int]], float],
    factors: tuple[int, ...] = (1, 2, 3),
) -> ZNEResult:
    raise NotImplementedError
