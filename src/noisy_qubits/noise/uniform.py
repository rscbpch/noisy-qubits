"""Uniform noise mode: one error probability per gate (plan, Section 6)."""
from __future__ import annotations

from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    amplitude_damping_error,
    depolarizing_error,
    pauli_error,
)

from .slider import uniform_errors

NOISE_TYPES = ("depolarizing", "bit_flip", "phase_flip", "amplitude_damping", "readout")

# Gate names the noise attaches to. Circuits are simulated as written, so
# a cp or swap counts as ONE two-qubit gate here (the device mode transpiles
# and therefore pays for the real gate count).
GATES_1Q = ["id", "x", "y", "z", "h", "s", "sdg", "t", "tdg", "sx", "rx", "ry", "rz", "p", "u"]
GATES_2Q = ["cx", "cy", "cz", "cp", "swap", "crx", "cry", "crz"]
GATES_3Q = ["ccx"]


def _readout_error(r: float) -> ReadoutError:
    """Symmetric readout error: each measured bit flips with probability r."""
    return ReadoutError([[1 - r, r], [r, 1 - r]])


def _per_qubit_error(noise_type: str, p: float):
    """One-qubit error with probability p (gamma = p for T1)."""
    if noise_type == "bit_flip":
        return pauli_error([("X", p), ("I", 1 - p)])
    if noise_type == "phase_flip":
        return pauli_error([("Z", p), ("I", 1 - p)])
    return amplitude_damping_error(p)  # "amplitude_damping"


def _on_n_qubits(err, n: int):
    """The same independent one-qubit error on each of n qubits of a gate."""
    out = err
    for _ in range(n - 1):
        out = out.tensor(err)
    return out


def build_uniform_noise_model(
    slider: int, noise_type: str = "depolarizing", readout: float = 0.0
) -> NoiseModel:
    if noise_type not in NOISE_TYPES:
        raise ValueError(f"Unknown noise type {noise_type!r}; choose one of {NOISE_TYPES}.")
    if not 0 <= readout <= 1:
        raise ValueError(f"Readout error must be between 0 and 1, got {readout}.")
    p1, p2 = uniform_errors(slider)
    nm = NoiseModel(basis_gates=GATES_1Q + GATES_2Q + GATES_3Q)

    if noise_type == "depolarizing":
        nm.add_all_qubit_quantum_error(depolarizing_error(p1, 1), GATES_1Q)
        nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), GATES_2Q)
        nm.add_all_qubit_quantum_error(depolarizing_error(p2, 3), GATES_3Q)
    elif noise_type != "readout":
        # bit_flip / phase_flip / amplitude_damping: each qubit a gate touches
        # gets the error independently, with the same p as depolarizing uses.
        for gates, n, p in ((GATES_1Q, 1, p1), (GATES_2Q, 2, p2), (GATES_3Q, 3, p2)):
            nm.add_all_qubit_quantum_error(_on_n_qubits(_per_qubit_error(noise_type, p), n), gates)
    else:  # "readout": no gate noise, readout error on the same scale as p2
        readout = max(readout, p2)

    if readout > 0:
        nm.add_all_qubit_readout_error(_readout_error(readout))
    return nm
