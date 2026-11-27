from math import pi

import pytest
from qiskit import qasm2
from qiskit.circuit.library import PhaseGate, phase_estimation
from qiskit.quantum_info import Statevector

from noisy_qubits.algorithms import REGISTRY, qpe
from noisy_qubits.noise import build_noise_model
from noisy_qubits.result import AlgorithmResult


@pytest.mark.parametrize("n", range(2, 11))
def test_no_noise_matches_theory(n):
    r = qpe.run(n, 256, seed=1)
    assert isinstance(r, AlgorithmResult)
    assert r.ideal_score == pytest.approx(1.0)
    assert r.score == 1.0
    assert r.baseline == 1 / 2 ** (n - 1)
    assert r.meta["estimated_phase"] == r.meta["phase"]


@pytest.mark.parametrize("k", range(16))
def test_every_phase_on_4_counting_qubits(k):
    r = qpe.run(5, 32, phase_k=k, seed=1)
    assert r.counts == {format(k, "04b"): 32}


@pytest.mark.parametrize("k", [0, 1, 255, 256, 511])
def test_edge_phases_at_10_qubits(k):
    assert qpe.ideal_score(qpe.build(10, k)) == pytest.approx(1.0)


@pytest.mark.parametrize("k", [1, 5, 6])
def test_matches_qiskit_phase_estimation(k):
    # Independent check against Qiskit's own QPE circuit. Its counting register
    # comes out in reverse bit order (qubit 0 is the most significant bit).
    reference = phase_estimation(3, PhaseGate(2 * pi * k / 8))
    start = Statevector.from_label("1000")  # eigenstate qubit 3 in |1>
    probabilities = start.evolve(reference).probabilities([0, 1, 2])
    reversed_k = int(format(k, "03b")[::-1], 2)
    assert probabilities[reversed_k] == pytest.approx(1.0)
    assert qpe.ideal_score(qpe.build(4, k)) == pytest.approx(1.0)


def test_default_phase():
    qc = qpe.build()
    assert qc.metadata["phase_k"] == 181
    assert qpe.phase_bits(181) == "010110101"


def test_one_controlled_gate_per_counting_qubit():
    # 9 to write the phase + 36 in the inverse QFT, whatever the phase is.
    for k in (0, 181, 256):
        assert qpe.build(10, k).count_ops()["cp"] == 45


def test_uses_only_supported_gates():
    qc = qpe.build()
    assert set(qc.count_ops()) <= {"x", "h", "cp", "swap", "barrier", "measure"}
    assert "cp(" in qasm2.dumps(qc)


@pytest.mark.parametrize("k", [-1, 512, 1.5, "181", True])
def test_bad_phase(k):
    with pytest.raises(qpe.InputError):
        qpe.build(10, k)


def test_phase_range_depends_on_size():
    with pytest.raises(qpe.InputError):
        qpe.build(4, 8)  # 3 counting qubits allow 0 to 7


@pytest.mark.parametrize("n", [0, 1, 11, 2.5, "5", True])
def test_bad_qubit_count(n):
    with pytest.raises(qpe.InputError):
        qpe.build(n)


@pytest.mark.parametrize("shots", [0, -1, 1.5])
def test_bad_shots(shots):
    with pytest.raises(qpe.InputError):
        qpe.run(3, shots)


def test_gate_noise_lowers_score():
    low = qpe.run(6, 1024, build_noise_model("uniform", 5), seed=1).score
    high = qpe.run(6, 1024, build_noise_model("uniform", 100), seed=1).score
    assert high < low < 1.0


def test_device_mode():
    nm = build_noise_model("device", 50, device="FakeKolkata")
    r = qpe.run(4, 512, nm, device="FakeKolkata", seed=1)
    assert 1 / 8 < r.score < 1.0


def test_registered():
    assert REGISTRY["qpe"] is qpe.run
