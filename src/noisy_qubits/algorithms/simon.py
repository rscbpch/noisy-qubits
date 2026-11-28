from __future__ import annotations
from math import pi
from typing import Optional
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity

from ..noise import run_counts
from ..result import AlgorithmResult
from .deutsch_jozsa import InputError

NAME = 'simon'
MIN_BITS = 1
MAX_BITS = 5
DEFAULT_SECRET = "10101"
BASELINE = 0.5
PASS_LINE = 0.75


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------
def _is_whole(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

def check_secret(secret: Optional[str], n_bits: Optional[int] = None) -> str:
    if secret is None:
        if n_bits is None:
            n_bits = len(DEFAULT_SECRET)
        if not _is_whole(n_bits) or not MIN_BITS <= n_bits <= MAX_BITS:
            raise InputError("Secret length must be a whole number from 1 to 5.")
        return DEFAULT_SECRET[-n_bits:]
    if not isinstance(secret, str) or secret == "":
        raise InputError("Secret s is empty. Enter 1 to 5 bits, for example 101.")
    if set(secret) - {"0", "1"}:
        raise InputError("Secret s may only contain the characters 0 and 1.")
    if len(secret) > MAX_BITS:
        raise InputError(f"Secret s has {len(secret)} bits. The maximum is {MAX_BITS}.")
    if "1" not in secret:
        raise InputError("Secret s must not be all zeros (that makes f one-to-one).")
    if n_bits is not None and len(secret) != n_bits:
        raise InputError(f"Secret s must have exactly {n_bits} bits.")
    return secret

# --------------------------------------------------------------------------
# circuit
# --------------------------------------------------------------------------

def build(secret: Optional[str] = None, n_bits: Optional[int] = None, measure: bool = True) -> QuantumCircuit:
    s = check_secret(secret, n_bits)
    n = len(s)
    bits = [int(c) for c in reversed(s)]

    inp = QuantumRegister(n, "x")
    out = QuantumRegister(n, "f")
    qc = QuantumCircuit(inp, out)

    if measure:
        qc.add_register(ClassicalRegister(n, "y"))
    qc.h(inp)
    qc.barrier()

    for i in range(n):
        qc.cx(inp[i], out[i])
    j = bits.index(1)
    for i in range(n):
        if bits[i]:
            qc.cx(inp[j], out[i])
    qc.barrier()
    qc.h(inp)
    if measure:
        qc.barrier()
        qc.measure(inp, qc.cregs[0])
    qc.metadata = {"secret": s}
    return qc

# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------

def _orthogonal(y: str, secret: str) -> bool:
    return sum(int(a) & int(b) for a, b in zip(y, secret)) % 2 == 0

def score(counts: dict[str, int], secret: str) -> float:
    total = sum(counts.values())
    good = sum(c for y, c in counts.items() if _orthogonal(y.replace(" ", ""), secret))
    return good / total

def ideal_score(qc: QuantumCircuit) -> float:
    secret = qc.metadata["secret"]
    n = len(secret)

    bare = qc.remove_final_measurements(inplace=False)
    probs = Statevector.from_instruction(bare).probabilities_dict(qargs=list(range(n)))
    return round(float(sum(p for y, p in probs.items() if _orthogonal(y, secret))), 9)

def passes(measured: float, ideal: float = 1.0) -> bool:
    return measured >= PASS_LINE * ideal

def run(n_bits: int = 5, shots: int = 1024, noise_model = None, *,
    secret: Optional[str] = None,
    device: Optional[str] = None,
    seed: Optional[int] = None) -> AlgorithmResult: 
    if not _is_whole(shots) or shots < 1:
        raise InputError("Shots must be a positive whole number.")
    qc = build(secret, None if secret is not None else n_bits)
    s = qc.metadata["secret"]
    counts = run_counts(qc, shots, noise_model, device=device, seed=seed)
    measured = score(counts, s)
    ideal = ideal_score(qc)
    return AlgorithmResult(
        name=NAME,
        circuit=qc,
        counts=counts,
        shots=shots,
        ideal_score=ideal,
        baseline=BASELINE,
        score=measured,
        meta={"n_bits": len(s), "pass_line": PASS_LINE, "passed": passes(measured, ideal), **qc.metadata},
    )