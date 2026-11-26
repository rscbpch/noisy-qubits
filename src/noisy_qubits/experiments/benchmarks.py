"""Circuits + scores the noise experiments run on.

Teammates' algorithms are added here as they appear: one `Benchmark` each,
using the algorithm's build() and score(). Until then, Superposition and the
QFT round trip (QFT then inverse QFT, plan Section 4) are defined locally.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from qiskit import QuantumCircuit
from qiskit.synthesis.qft import synth_qft_full

N = 10


@dataclass
class Benchmark:
    name: str
    circuit: QuantumCircuit
    score: Callable[[dict[str, int]], float]
    pass_fraction: float = 0.5   # pass if score >= pass_fraction * ideal (Simon's: 0.75)


def _superposition() -> Benchmark:
    qc = QuantumCircuit(N, N)
    qc.h(range(N))
    qc.measure(range(N), range(N))

    def score(counts):  # 1 - 2*mean|P(qubit=1) - 0.5|: ~0.97 ideal at 1024 shots
        tot = sum(counts.values())
        p1 = np.zeros(N)
        for key, v in counts.items():
            for i, ch in enumerate(reversed(key.replace(" ", ""))):
                p1[i] += v * (ch == "1")
        return float(1 - 2 * np.mean(np.abs(p1 / tot - 0.5)))

    return Benchmark("superposition", qc, score)


def _qft_roundtrip(state: str = "0110010110") -> Benchmark:
    qc = QuantumCircuit(N, N)
    for i, bit in enumerate(reversed(state)):
        if bit == "1":
            qc.x(i)
    qft = synth_qft_full(N)             # h, cp and swap gates only
    qc.compose(qft, inplace=True)
    qc.compose(qft.inverse(), inplace=True)
    qc.measure(range(N), range(N))
    return Benchmark("qft_roundtrip", qc, lambda c: c.get(state, 0) / sum(c.values()))


def all_benchmarks() -> list[Benchmark]:
    return [_superposition(), _qft_roundtrip()]
