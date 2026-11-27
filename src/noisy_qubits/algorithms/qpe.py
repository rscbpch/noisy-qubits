"""Algorithm 4: Quantum Phase Estimation (2 to 10 qubits).

Layout: qubits 0..m-1 are the counting register (m = n_qubits - 1) and qubit m
is the eigenstate. 10 qubits = 9 counting + 1 eigenstate.

The hidden gate is a phase gate P(2*pi*theta), whose eigenstate is |1>.
theta = phase_k / 2**m, so it fits exactly in m bits and a noise-free run
always reads phase_k. Only the counting register is measured.

Bit order is Qiskit's: the RIGHTMOST character of a bitstring is qubit 0.

Score = share of shots that read the correct phase bits (ideal 1.0).
Classical baseline = 1 / 2**m (random guess).
"""
from __future__ import annotations

from math import pi
from typing import Optional

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from ..noise import run_counts
from ..result import AlgorithmResult
from .deutsch_jozsa import InputError
from .qft import qft_circuit

NAME = "qpe"
MIN_QUBITS = 2
MAX_QUBITS = 10
DEFAULT_K = 181  # 010110101 in binary


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
def _is_whole(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _n_counting(n_qubits: int) -> int:
    """Check the qubit count and return the number of counting qubits m."""
    if not _is_whole(n_qubits) or not MIN_QUBITS <= n_qubits <= MAX_QUBITS:
        raise InputError("Qubit count must be a whole number from 2 to 10.")
    return n_qubits - 1


def check_phase_k(phase_k: Optional[int], n_qubits: int) -> int:
    """Return a valid k for theta = k / 2**m. None means the default."""
    size = 2 ** _n_counting(n_qubits)
    if phase_k is None:
        return DEFAULT_K % size
    if not _is_whole(phase_k) or not 0 <= phase_k < size:
        raise InputError(
            f"The phase is k/{size}, where k is a whole number from 0 to {size - 1}."
        )
    return phase_k


def phase_bits(phase_k: int, n_qubits: int = 10) -> str:
    """The bitstring a noise-free run reads."""
    k = check_phase_k(phase_k, n_qubits)
    return format(k, f"0{n_qubits - 1}b")


# --------------------------------------------------------------------------
# circuit
# --------------------------------------------------------------------------
def build(
    n_qubits: int = 10, phase_k: Optional[int] = None, measure: bool = True
) -> QuantumCircuit:
    """Build the QPE circuit for theta = phase_k / 2**m."""
    m = _n_counting(n_qubits)
    k = check_phase_k(phase_k, n_qubits)
    size = 2**m
    eigen = m

    qc = QuantumCircuit(QuantumRegister(n_qubits, "q"), name=NAME)
    if measure:
        qc.add_register(ClassicalRegister(m, "c"))

    # 1. Eigenstate |1>, counting qubits in an equal mix.
    qc.x(eigen)
    qc.h(range(m))
    qc.barrier()

    # 2. Counting qubit j applies the hidden gate 2**j times. For a phase gate
    #    that is one gate with 2**j times the angle (full turns removed).
    #    Every qubit keeps its gate, even at angle 0, so in uniform mode the
    #    gate count is the same for every phase.
    for j in range(m):
        turns = (k * 2**j) % size
        qc.cp(2 * pi * turns / size, j, eigen)
    qc.barrier()

    # 3. The inverse QFT turns the phase pattern into the bits of k.
    qc.compose(qft_circuit(m).inverse() if m > 1 else _one_qubit_iqft(),
               qubits=range(m), inplace=True)

    if measure:
        qc.barrier()
        qc.measure(range(m), range(m))
    qc.metadata = {"phase_k": k, "phase": k / size, "n_counting": m}
    return qc


def _one_qubit_iqft() -> QuantumCircuit:
    """qft_circuit() starts at 2 qubits; on 1 qubit the (inverse) QFT is just H."""
    qc = QuantumCircuit(1)
    qc.h(0)
    return qc


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------
def score(counts: dict[str, int], phase_k: int, n_qubits: int = 10) -> float:
    """Share of shots that read the correct phase bits."""
    return counts.get(phase_bits(phase_k, n_qubits), 0) / sum(counts.values())


def ideal_score(qc: QuantumCircuit) -> float:
    """Exact no-noise score from the state vector (theory: 1.0)."""
    m = qc.metadata["n_counting"]
    bare = qc.remove_final_measurements(inplace=False)
    probabilities = Statevector.from_instruction(bare).probabilities(list(range(m)))
    return float(probabilities[qc.metadata["phase_k"]])


def run(
    n_qubits: int = 10,
    shots: int = 1024,
    noise_model=None,
    *,
    phase_k: Optional[int] = None,
    device: Optional[str] = None,
    seed: Optional[int] = None,
) -> AlgorithmResult:
    """Run QPE once.

    device: fake device name. Pass the same name to build_noise_model().
    """
    if not _is_whole(shots) or shots < 1:
        raise InputError("Shots must be a positive whole number.")
    qc = build(n_qubits, phase_k)
    k = qc.metadata["phase_k"]
    m = qc.metadata["n_counting"]
    counts = run_counts(qc, shots, noise_model, device=device, seed=seed)
    # The most frequent reading is the algorithm's answer.
    measured = max(counts, key=counts.get)
    return AlgorithmResult(
        name=NAME,
        circuit=qc,
        counts=counts,
        shots=shots,
        ideal_score=ideal_score(qc),
        baseline=1 / 2**m,
        score=score(counts, k, n_qubits),
        meta={
            "n_qubits": n_qubits,
            "estimated_phase": int(measured, 2) / 2**m,
            **qc.metadata,
        },
    )
