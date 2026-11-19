"""Algorithm 1: superposition / quantum randomness (H on every qubit)."""
from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from ..result import AlgorithmResult


def build(n_qubits: int = 10) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def uniformity(counts: dict[str, int], n_qubits: int) -> float:
    """1 - total variation distance to the uniform distribution."""
    shots = sum(counts.values())
    uni = 1 / 2**n_qubits
    seen = sum(abs(c / shots - uni) for c in counts.values())
    unseen = (2**n_qubits - len(counts)) * uni
    return 1 - 0.5 * (seen + unseen)


def run(n_qubits: int = 10, shots: int = 1024, noise_model=None) -> AlgorithmResult:
    qc = build(n_qubits)
    backend = AerSimulator(noise_model=noise_model)
    counts = backend.run(qc, shots=shots).result().get_counts()
    return AlgorithmResult(
        name="superposition",
        circuit=qc,
        counts=counts,
        shots=shots,
        ideal_score=1.0,
        baseline=0.0,  # placeholder: define with the team (plan 3, "classical random")
        score=uniformity(counts, n_qubits),
        meta={"n_qubits": n_qubits},
    )
