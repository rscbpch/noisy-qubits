import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from noisy_qubits.mitigation import extrapolate, fold_gates, zne
from noisy_qubits.noise import build_noise_model


def _small():
    qc = QuantumCircuit(3)
    qc.h(0); qc.cx(0, 1); qc.rx(0.3, 2); qc.s(1); qc.cp(0.7, 1, 2); qc.sx(0); qc.ccx(0, 1, 2)
    return qc


@pytest.mark.parametrize("factor", [1, 2, 3, 5])
def test_folding_keeps_the_circuit_the_same(factor):
    qc = _small()
    assert Operator(fold_gates(qc, factor)).equiv(Operator(qc))


def test_folding_scales_gate_count():
    qc = _small()
    n = len(qc.data)
    assert len(fold_gates(qc, 1).data) == n
    assert len(fold_gates(qc, 3).data) == 3 * n
    assert len(fold_gates(qc, 2).data) == pytest.approx(2 * n, abs=1)


def test_skip_and_missing_inverse_are_not_folded():
    qc = QuantumCircuit(1)
    qc.sx(0); qc.rz(0.5, 0)
    assert len(fold_gates(qc, 3, skip=("rz",), basis={"sx", "rz"}).data) == 2  # sx has no sxdg, rz skipped
    assert len(fold_gates(qc, 3, basis={"sx", "rz"}).data) == 4                # only rz folded


def test_bad_inputs():
    with pytest.raises(ValueError):
        fold_gates(_small(), 0.5)
    with pytest.raises(ValueError):
        extrapolate([1, 2, 3], [0.9, 0.8, 0.7], "banana")
    with pytest.raises(ValueError):
        zne(_small(), None, 10, lambda c: 0.0, factors=(2, 3))
    with pytest.raises(ValueError):
        zne(_small(), None, 10, lambda c: 0.0, factors=(1, 1))


def test_extrapolation_recovers_a_known_exponential_and_clips():
    mitigated, curve = extrapolate([1, 2, 3], [0.8, 0.64, 0.512], "exponential")
    assert mitigated == pytest.approx(1.0, abs=1e-6)
    assert curve[0][0] == 0.0 and curve[-1][0] == 3.0
    assert extrapolate([1, 2, 3], [0.2, 0.5, 0.9], "linear")[0] == 0.0  # clipped from a negative value
    assert extrapolate([1, 2, 3], [0.0, 0.0, 0.0], "exponential")[0] == 0.0  # zeros fall back, no log error


def _ladder():
    qc = QuantumCircuit(4, 4)
    qc.x(0)
    for _ in range(30):
        qc.cx(0, 1)
    qc.measure(range(4), range(4))
    return qc


def _score(c):
    return c.get("0001", 0) / sum(c.values())


def test_zne_helps_against_gate_noise():
    nm = build_noise_model("uniform", 25)
    r = zne(_ladder(), nm, 4096, _score, seed=1)
    assert r.scores[0] > r.scores[1] > r.scores[2]
    assert r.mitigated > r.raw + 0.1
    assert r.raw == r.scores[0] and r.factors == (1, 2, 3)


def test_zne_cannot_fix_readout_error():
    nm = build_noise_model("uniform", 50, noise_type="readout")
    r = zne(_ladder(), nm, 4096, _score, seed=1)
    assert r.mitigated == pytest.approx(r.raw, abs=0.03)


def test_zne_flags_an_unreliable_fit_at_extreme_noise():
    ok = zne(_ladder(), build_noise_model("uniform", 25), 4096, _score, seed=1)
    assert ok.reliable
    bad = zne(_ladder(), build_noise_model("uniform", 100, noise_type="bit_flip"), 4096,
              lambda c: c.get("0001", 0) / sum(c.values()) * 0.001, seed=1)  # scores far below 10 shots
    assert not bad.reliable
