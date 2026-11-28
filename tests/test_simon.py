"""Tests for Simon's algorithm. Run with: uv run pytest"""
import pytest

from noisy_qubits.algorithms import simon
from noisy_qubits.algorithms.deutsch_jozsa import InputError
from noisy_qubits.noise import DEVICES, build_device_noise_model


@pytest.mark.parametrize("secret", ["1", "11", "101", "0110", "10011", "00001", "11111"])
def test_no_noise_matches_theory(secret):
    r = simon.run(secret=secret, shots=1024, seed=1)
    assert r.ideal_score == pytest.approx(1.0)      # theory: every y obeys y.s = 0
    assert r.score == pytest.approx(r.ideal_score)  # and the simulator agrees
    assert r.baseline == 0.5
    assert r.meta["passed"]


@pytest.mark.parametrize("n_bits", [1, 2, 3, 4, 5])
def test_size_follows_n_bits(n_bits):
    r = simon.run(n_bits, shots=64, seed=1)
    assert len(r.meta["secret"]) == n_bits
    assert r.circuit.num_qubits == 2 * n_bits
    assert r.circuit.num_clbits == n_bits
    assert r.score == pytest.approx(1.0)


def test_secret_wins_over_n_bits():
    r = simon.run(5, shots=64, secret="101", seed=1)
    assert r.meta["secret"] == "101" and r.circuit.num_qubits == 6


@pytest.mark.parametrize("bad", ["", "000", "1a0", "102", "101010", " 101", 123])
def test_invalid_secret_rejected(bad):
    with pytest.raises(InputError):
        simon.run(secret=bad, shots=16)


@pytest.mark.parametrize("n_bits", [0, 6, 2.5, "3", True])
def test_invalid_n_bits_rejected(n_bits):
    with pytest.raises(InputError):
        simon.run(n_bits, shots=16)


def test_bad_shots_rejected():
    with pytest.raises(InputError):
        simon.run(3, shots=0)


def test_bit_order_is_rightmost_is_qubit_0():
    # s = "011": bits 0 and 1 set. y = "001" (bit 0 only) has dot 1; y = "100" has dot 0.
    assert not simon._orthogonal("001", "011")
    assert simon._orthogonal("100", "011")
    assert simon.score({"001": 30, "100": 70}, "011") == pytest.approx(0.7)


def test_pass_line_is_75_percent():
    assert simon.passes(0.75) and not simon.passes(0.74)
    assert simon.passes(0.7, ideal=0.9) and not simon.passes(0.6, ideal=0.9)


def test_pass_line_equals_normalized_half():
    # Simon's 75 % line is the same as "halfway between random (0.5) and perfect (1.0)"
    r = simon.run(3, shots=1024, seed=1)
    r.score = 0.75
    assert r.normalized == pytest.approx(0.5)


@pytest.mark.parametrize("device", DEVICES)
def test_runs_on_each_device(device):
    nm = build_device_noise_model(device, 50)
    r = simon.run(5, shots=256, noise_model=nm, device=device, seed=1)
    assert 0.5 < r.score <= 1.0          # real device at slider 50 should beat random
    assert r.ideal_score == pytest.approx(1.0)


def test_more_noise_scores_lower():
    dev = DEVICES[0]
    lo = simon.run(5, 512, build_device_noise_model(dev, 5), device=dev, seed=1).score
    hi = simon.run(5, 512, build_device_noise_model(dev, 100), device=dev, seed=1).score
    assert lo > hi