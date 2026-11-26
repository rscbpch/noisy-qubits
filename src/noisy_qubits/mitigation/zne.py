"""Zero-noise extrapolation by gate folding (plan, Section 10)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate

from ..noise.devices import TRANSPILE_SEED, get_backend, run_counts

METHODS = ("exponential", "linear", "richardson")
_NOT_FOLDABLE = {"measure", "reset", "barrier", "delay"}


@dataclass
class ZNEResult:
    factors: tuple[float, ...]
    scores: list[float]   # score at each noise factor
    mitigated: float      # extrapolated score at noise 0 (clipped to 0..1)
    raw: float            # score at factor 1
    method: str = "exponential"
    curve: list[tuple[float, float]] = field(default_factory=list)  # for the ZNE picture
    # False when the fit rests on scores that are mostly shot noise (see min_count).
    # The test flow should then report FAIL, not RECOVERED.
    reliable: bool = True


def _eligible(inst, skip, basis) -> bool:
    op = inst.operation
    if not isinstance(op, Gate) or op.name in _NOT_FOLDABLE or op.name in skip:
        return False
    return basis is None or op.inverse().name in basis


def fold_gates(circuit: QuantumCircuit, factor: float, skip=(), basis=None) -> QuantumCircuit:
    """Scale the noise by `factor` (>= 1) by replacing gate G with G, G^-1, G.

    Only gates whose inverse exists in `basis` are folded (otherwise the extra
    gates would run noise-free). Factor 3 folds every such gate once; factor 2
    folds half of them (evenly spread); other factors work the same way.
    The folded circuit does the same thing as the original when noise is off.
    """
    if factor < 1:
        raise ValueError(f"Noise factor must be at least 1, got {factor}.")
    idx = [i for i, inst in enumerate(circuit.data) if _eligible(inst, skip, basis)]
    pairs = (factor - 1) / 2            # extra (G^-1, G) pairs per eligible gate
    full = int(pairs)
    n_extra = round((pairs - full) * len(idx))
    extra = set()
    if n_extra:
        spread = np.linspace(0, len(idx) - 1, n_extra).round().astype(int)
        extra = {idx[j] for j in spread}

    out = circuit.copy_empty_like()
    for i, inst in enumerate(circuit.data):
        out.append(inst.operation, inst.qubits, inst.clbits)
        if i in idx:
            for _ in range(full + (1 if i in extra else 0)):
                out.append(inst.operation.inverse(), inst.qubits)
                out.append(inst.operation, inst.qubits)
    return out


def extrapolate(factors, scores, method="exponential") -> tuple[float, list[tuple[float, float]]]:
    """Fit the scores against the noise factor and read the curve at 0."""
    if method not in METHODS:
        raise ValueError(f"Unknown fit {method!r}; choose one of {METHODS}.")
    x, y = np.asarray(factors, float), np.asarray(scores, float)
    grid = np.linspace(0, float(x.max()), 31)
    if method == "exponential" and np.all(y > 0):
        b, a = np.polyfit(x, np.log(y), 1)
        f = lambda t: np.exp(a + b * t)
    else:  # also the fallback when a score is 0 and a log is impossible
        deg = 2 if method == "richardson" and len(x) >= 3 else 1
        coef = np.polyfit(x, y, deg)
        f = lambda t: np.polyval(coef, t)
    clip = lambda v: float(min(max(v, 0.0), 1.0))
    return clip(f(0.0)), [(float(t), clip(f(t))) for t in grid]


def zne(
    circuit: QuantumCircuit,
    noise_model,
    shots: int,
    score_fn: Callable[[dict[str, int]], float],
    factors: tuple[float, ...] = (1, 2, 3),
    device: str | None = None,
    method: str = "exponential",
    seed: int | None = None,
    min_count: int = 10,
) -> ZNEResult:
    """Run at several noise factors and extrapolate the score back to zero noise.

    `reliable` is False if the lowest measured score is below min_count / shots
    (fewer than ~10 correct shots): extrapolating from that is guessing.
    """
    if len(set(factors)) < 2 or min(factors) != 1:
        raise ValueError("Factors need at least two different values and must start at 1.")
    skip = ()
    if device is not None:  # transpile once, then fold, so the folds carry noise
        circuit = transpile(circuit, backend=get_backend(device), optimization_level=1,
                            seed_transpiler=TRANSPILE_SEED)
        skip = ("rz",)       # rz is virtual on IBM hardware: no noise, only cost
    basis = set(noise_model.basis_gates) if noise_model is not None else None

    scores = []
    for f in factors:
        counts = run_counts(fold_gates(circuit, f, skip=skip, basis=basis), shots, noise_model, seed=seed)
        scores.append(float(score_fn(counts)))
    mitigated, curve = extrapolate(factors, scores, method)
    reliable = min(scores) * shots >= min_count
    return ZNEResult(tuple(factors), scores, mitigated, scores[factors.index(1)], method, curve, reliable)
