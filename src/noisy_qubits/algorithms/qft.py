"""Algorithm 3: Quantum Fourier Transform round trip (2 to 10 qubits).

Circuit: prepare the input bitstring, apply QFT, apply the inverse QFT, measure.
Without noise the input comes back every time.

Bit order is Qiskit's: the RIGHTMOST character of a bitstring is qubit 0, so a
counts key can be compared with the input string directly.

Score = share of shots that return the input (ideal 1.0).
Classical baseline = 1 / 2**n (random guess).

approximation_degree = d leaves out the d smallest rotation sizes
(0 = exact QFT). See approximation_fidelity() for what that costs.
"""
from __future__ import annotations

from math import pi
from typing import Optional

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

from ..noise import run_counts
from ..result import AlgorithmResult
from .deutsch_jozsa import InputError

NAME = "qft"
MIN_QUBITS = 2
MAX_QUBITS = 10
DEFAULT_STATE = "0110010110"


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
def _is_whole(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_qubits(n_qubits: int) -> None:
    if not _is_whole(n_qubits) or not MIN_QUBITS <= n_qubits <= MAX_QUBITS:
        raise InputError("Qubit count must be a whole number from 2 to 10.")


def _check_degree(degree: int, n_qubits: int) -> None:
    if not _is_whole(degree) or not 0 <= degree <= n_qubits - 1:
        raise InputError(f"Approximation degree must be a whole number from 0 to {n_qubits - 1}.")


def check_input_state(input_state: Optional[str], n_qubits: int) -> str:
    """Return a valid input bitstring. None means the default for this size."""
    _check_qubits(n_qubits)
    if input_state is None:
        return DEFAULT_STATE[-n_qubits:]
    if (not isinstance(input_state, str) or len(input_state) != n_qubits
            or set(input_state) - {"0", "1"}):
        raise InputError(
            f"Input state must be exactly {n_qubits} characters, using only 0 and 1."
        )
    return input_state


# --------------------------------------------------------------------------
# circuit
# --------------------------------------------------------------------------
def qft_circuit(n_qubits: int, approximation_degree: int = 0) -> QuantumCircuit:
    """The QFT on its own, using only h, cp and swap."""
    _check_qubits(n_qubits)
    _check_degree(approximation_degree, n_qubits)
    qc = QuantumCircuit(n_qubits, name="qft")
    # Work from the highest qubit down: each one still needs the original
    # values of the qubits below it as controls.
    for target in reversed(range(n_qubits)):
        qc.h(target)
        for control in reversed(range(target)):
            distance = target - control          # angle is pi / 2**distance
            if distance < n_qubits - approximation_degree:
                qc.cp(pi / 2**distance, control, target)
    # The loop leaves the qubit order reversed.
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    return qc


def build(
    n_qubits: int = 10,
    input_state: Optional[str] = None,
    approximation_degree: int = 0,
    measure: bool = True,
) -> QuantumCircuit:
    """Prepare the input, then QFT, then inverse QFT, then (optionally) measure."""
    state = check_input_state(input_state, n_qubits)
    forward = qft_circuit(n_qubits, approximation_degree)

    qc = QuantumCircuit(n_qubits, n_qubits if measure else 0, name=NAME)
    for qubit, bit in enumerate(reversed(state)):
        if bit == "1":
            qc.x(qubit)
    qc.barrier()
    qc.compose(forward, inplace=True)
    # Keep this barrier: without it the device transpiler cancels gates between
    # the two halves, and cancelled gates pick up no noise.
    qc.barrier()
    qc.compose(forward.inverse(), inplace=True)
    if measure:
        qc.barrier()
        qc.measure(range(n_qubits), range(n_qubits))
    qc.metadata = {"input_state": state, "approximation_degree": approximation_degree}
    return qc


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------
def score(counts: dict[str, int], input_state: str) -> float:
    """Share of shots that return the input bitstring."""
    return counts.get(input_state, 0) / sum(counts.values())


def ideal_score(qc: QuantumCircuit) -> float:
    """Exact no-noise score from the state vector (theory: 1.0)."""
    bare = qc.remove_final_measurements(inplace=False)
    probabilities = Statevector.from_instruction(bare).probabilities_dict()
    return float(probabilities.get(qc.metadata["input_state"], 0.0))


def approximation_fidelity(
    n_qubits: int = 10, input_state: Optional[str] = None, approximation_degree: int = 0
) -> float:
    """How close the approximate QFT's output is to the exact QFT's (1.0 = same).

    The round-trip score cannot show this: any circuit followed by its own
    inverse returns the input, however rough the approximation is.
    """
    state = check_input_state(input_state, n_qubits)
    start = Statevector.from_label(state)
    exact = start.evolve(qft_circuit(n_qubits))
    approx = start.evolve(qft_circuit(n_qubits, approximation_degree))
    return float(state_fidelity(exact, approx))


def run(
    n_qubits: int = 10,
    shots: int = 1024,
    noise_model=None,
    *,
    input_state: Optional[str] = None,
    approximation_degree: int = 0,
    device: Optional[str] = None,
    seed: Optional[int] = None,
) -> AlgorithmResult:
    """Run the round trip once.

    device: fake device name. Pass the same name to build_noise_model().
    """
    if not _is_whole(shots) or shots < 1:
        raise InputError("Shots must be a positive whole number.")
    qc = build(n_qubits, input_state, approximation_degree)
    state = qc.metadata["input_state"]
    counts = run_counts(qc, shots, noise_model, device=device, seed=seed)
    return AlgorithmResult(
        name=NAME,
        circuit=qc,
        counts=counts,
        shots=shots,
        ideal_score=ideal_score(qc),
        baseline=1 / 2**n_qubits,
        score=score(counts, state),
        meta={"n_qubits": n_qubits, **qc.metadata},
    )
