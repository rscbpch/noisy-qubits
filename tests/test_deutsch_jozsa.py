import pytest

from noisy_qubits.algorithms import REGISTRY
from noisy_qubits.algorithms import deutsch_jozsa as dj
from noisy_qubits.noise import build_noise_model
from noisy_qubits.result import AlgorithmResult


@pytest.mark.parametrize("n", [2, 3, 5, 10])
@pytest.mark.parametrize("oracle", dj.ORACLES)
def test_no_noise_matches_theory(n, oracle):
    r = dj.run(n, 256, oracle=oracle, seed=1)
    assert isinstance(r, AlgorithmResult)
    assert r.ideal_score == pytest.approx(1.0)
    assert r.score == pytest.approx(1.0)
    assert r.baseline == 0.5
    assert r.normalized == pytest.approx(1.0)
    assert r.meta["answer"] == r.meta["expected"]


def test_balanced_never_reads_all_zeros():
    r = dj.run(6, 512, oracle="balanced", seed=3)
    assert r.counts.get("0" * 5, 0) == 0


def test_balanced_with_given_mask():
    r = dj.run(4, 128, oracle="balanced", mask=0b101, seed=1)
    assert r.meta["mask"] == 0b101 and r.score == pytest.approx(1.0)


def test_typed_oracle():
    r = dj.run(3, 256, truth_table="0110", seed=1)        # balanced on 2 bits
    assert r.meta["expected"] == "balanced" and r.score == pytest.approx(1.0)
    r = dj.run(3, 64, truth_table="1111", seed=1)
    assert r.meta["expected"] == "constant" and r.score == pytest.approx(1.0)


@pytest.mark.parametrize("bad", ["0001", "01", "01x0", ""])
def test_bad_truth_table(bad):
    with pytest.raises(dj.InputError):
        dj.build(3, truth_table=bad)


@pytest.mark.parametrize("n", [0, 1, 11, 2.5, "5", True])
def test_bad_qubit_count(n):
    with pytest.raises(dj.InputError):
        dj.build(n)


@pytest.mark.parametrize("mask", [0, 16, -1, 1.5])
def test_bad_mask(mask):
    with pytest.raises(dj.InputError):
        dj.build(5, "balanced", mask=mask)


def test_bad_oracle_and_shots():
    with pytest.raises(dj.InputError):
        dj.build(4, "random")
    with pytest.raises(dj.InputError):
        dj.run(4, 0)


def test_registered():
    assert REGISTRY["deutsch_jozsa"] is dj.run


def test_readout_noise_lowers_constant_score():
    nm = build_noise_model("uniform", 1, "readout", readout=0.05)
    r = dj.run(10, 1024, nm, oracle="constant-0", seed=1)
    assert r.score < 0.8          # about (1 - 0.05)**9 = 0.63


def test_depolarizing_noise_keeps_dj_robust():
    nm = build_noise_model("uniform", 100)
    r = dj.run(10, 1024, nm, oracle="balanced", seed=1)
    assert r.score > 0.9