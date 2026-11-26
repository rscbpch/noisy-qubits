"""Algorithm 2: Deutsch-Jozsa (2 to 10 qubits = n-1 input qubits + 1 helper).

Layout: qubits 0..m-1 are the input register (m = n_qubits - 1) and qubit m
is the helper. Only the input register is measured.

Answer rule:
    measured 00...0  -> the function is CONSTANT
    anything else    -> the function is BALANCED

Score = share of shots whose answer is the correct one (ideal 1.0).
Classical baseline = 1/2 (guess "constant" or "balanced").
"""
from __future__ import annotations

import random
from typing import Optional

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from ..result import AlgorithmResult

NAME = "deutsch_jozsa"
MIN_QUBITS = 2
MAX_QUBITS = 10
BASELINE = 0.5
ORACLES = ("constant-0", "constant-1", "balanced")


class InputError(ValueError):
    """Invalid user input. The message is safe to show in the UI."""


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
def _n_inputs(n_qubits: int) -> int:
    """Check the qubit count and return the number of input bits m."""
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, int) \
            or not MIN_QUBITS <= n_qubits <= MAX_QUBITS:
        raise InputError("Qubit count must be a whole number from 2 to 10.")
    return n_qubits - 1


def check_truth_table(table: str, m: int) -> str:
    """Typed oracle: 2**m characters, table[x] = f(x), bit i of x = qubit i."""
    if not isinstance(table, str) or not table or set(table) - {"0", "1"}:
        raise InputError("Truth table must contain only the characters 0 and 1.")
    if len(table) != 2**m:
        raise InputError(
            f"Truth table needs exactly {2**m} characters for {m} input bits "
            f"(got {len(table)})."
        )
    if table.count("1") not in (0, len(table), len(table) // 2):
        raise InputError(
            "Function must be constant (all 0 or all 1) or balanced "
            "(exactly half of the outputs are 1)."
        )
    return table


def _kind(table: str) -> str:
    return "constant" if len(set(table)) == 1 else "balanced"


# --------------------------------------------------------------------------
# circuit
# --------------------------------------------------------------------------
def _add_oracle(qc, m, oracle, mask, truth_table, seed) -> dict:
    """Append the oracle gates; return info about it."""
    helper = m
    if truth_table is not None:
        table = check_truth_table(truth_table, m)
        kind = _kind(table)
        if kind == "constant":
            if table[0] == "1":
                qc.x(helper)
        else:
            for x, bit in enumerate(table):
                if bit != "1":
                    continue
                zeros = [i for i in range(m) if not (x >> i) & 1]
                for i in zeros:
                    qc.x(i)
                qc.mcx(list(range(m)), helper)
                for i in zeros:
                    qc.x(i)
        return {"expected": kind, "oracle": "typed", "truth_table": table}

    if oracle == "constant-0":
        return {"expected": "constant", "oracle": oracle}
    if oracle == "constant-1":
        qc.x(helper)
        return {"expected": "constant", "oracle": oracle}
    if oracle == "balanced":
        if mask is None:
            mask = random.Random(seed).randint(1, 2**m - 1)
        if isinstance(mask, bool) or not isinstance(mask, int) or not 1 <= mask <= 2**m - 1:
            raise InputError(f"Balanced mask must be a whole number from 1 to {2**m - 1}.")
        # f(x) = mask . x (mod 2) is balanced for every non-zero mask
        for i in range(m):
            if (mask >> i) & 1:
                qc.cx(i, helper)
        return {"expected": "balanced", "oracle": oracle, "mask": mask}
    raise InputError("Oracle must be constant-0, constant-1, balanced, or a typed truth table.")


def build(
    n_qubits: int = 10,
    oracle: str = "balanced",
    mask: Optional[int] = None,
    truth_table: Optional[str] = None,
    seed: Optional[int] = None,
    measure: bool = True,
) -> QuantumCircuit:
    """Build the DJ circuit. Oracle info is kept in circuit.metadata."""
    m = _n_inputs(n_qubits)
    qc = QuantumCircuit(QuantumRegister(n_qubits, "q"), name="deutsch_jozsa")
    if measure:
        qc.add_register(ClassicalRegister(m, "c"))
    qc.x(m)
    qc.h(range(n_qubits))
    qc.barrier()
    info = _add_oracle(qc, m, oracle, mask, truth_table, seed)
    qc.barrier()
    qc.h(range(m))
    if measure:
        qc.measure(range(m), range(m))
    qc.metadata = {**info, "n_inputs": m}
    return qc


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------
def ideal_score(qc: QuantumCircuit) -> float:
    """Exact no-noise score from the state vector (theory: 1.0)."""
    m = qc.metadata["n_inputs"]
    bare = qc.remove_final_measurements(inplace=False)
    p_zero = Statevector.from_instruction(bare).probabilities(list(range(m)))[0]
    return float(p_zero if qc.metadata["expected"] == "constant" else 1.0 - p_zero)


def success_rate(counts: dict[str, int], expected: str, n_inputs: int) -> float:
    """Share of shots that give the correct answer."""
    shots = sum(counts.values())
    p_zero = counts.get("0" * n_inputs, 0) / shots
    return p_zero if expected == "constant" else 1.0 - p_zero


def run(
    n_qubits: int = 10,
    shots: int = 1024,
    noise_model=None,
    *,
    oracle: str = "balanced",
    mask: Optional[int] = None,
    truth_table: Optional[str] = None,
    seed: Optional[int] = None,
    simulator=None,
) -> AlgorithmResult:
    """Run Deutsch-Jozsa once.

    Same first three arguments as the other algorithms' run().
    simulator: optional AerSimulator (e.g. AerSimulator.from_backend(fake_device));
               it replaces noise_model.
    """
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        raise InputError("Shots must be a positive whole number.")
    qc = build(n_qubits, oracle, mask, truth_table, seed)
    m = qc.metadata["n_inputs"]
    expected = qc.metadata["expected"]

    backend = simulator or AerSimulator(noise_model=noise_model)
    # level 0: keep the circuit as written so no gates are cancelled away.
    # Typed oracles use mcx, which is decomposed into the backend's gates here.
    tqc = transpile(qc, backend, optimization_level=0, seed_transpiler=seed)
    counts = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()

    answer = "constant" if counts.get("0" * m, 0) / shots > 0.5 else "balanced"
    return AlgorithmResult(
        name=NAME,
        circuit=qc,
        counts=counts,
        shots=shots,
        ideal_score=ideal_score(qc),
        baseline=BASELINE,
        score=success_rate(counts, expected, m),
        meta={
            "n_qubits": n_qubits,
            "n_inputs": m,
            "answer": answer,
            **{k: v for k, v in qc.metadata.items() if k != "n_inputs"},
        },
    )