import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from noisy_qubits.noise import build_noise_model, slider_label
from noisy_qubits.noise.slider import device_multiplier, uniform_errors


@pytest.mark.parametrize("bad", [0, 101, -5, 1.5, "40", None, True])
def test_slider_rejects_bad_values(bad):
    with pytest.raises(ValueError):
        build_noise_model("uniform", bad)


def test_uniform_error_scale():
    assert uniform_errors(100) == pytest.approx((0.005, 0.05))
    assert uniform_errors(40) == pytest.approx((0.002, 0.02))


def test_device_multiplier():
    assert device_multiplier(50) == 1.0
    assert device_multiplier(100) == 2.0


def test_labels():
    assert slider_label("uniform", 40) == "Slider 40 means 2% error per gate"
    assert slider_label("uniform", 1) == "Slider 1 means 0.05% error per gate"
    assert slider_label("device", 50) == "Slider 50 means 1x the real device error rates"


def test_unknown_mode_and_type():
    with pytest.raises(ValueError):
        build_noise_model("banana", 10)
    with pytest.raises(ValueError):
        build_noise_model("uniform", 10, noise_type="banana")
    with pytest.raises(ValueError):
        build_noise_model("uniform", 10, readout=1.5)


def _success(qc, nm, shots=4096):
    counts = AerSimulator(noise_model=nm).run(qc, shots=shots).result().get_counts()
    return counts.get("01", 0) / shots


def test_depolarizing_degrades_a_deep_circuit():
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    for _ in range(40):  # 40 CX = identity, so the ideal answer is always '01'
        qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    assert _success(qc, None) == 1.0
    assert _success(qc, build_noise_model("uniform", 100)) < 0.8
    assert _success(qc, build_noise_model("uniform", 1)) > _success(qc, build_noise_model("uniform", 100))


def test_readout_error_flips_measurements():
    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    nm = build_noise_model("uniform", 1, readout=0.3)
    counts = AerSimulator(noise_model=nm).run(qc, shots=4096).result().get_counts()
    assert 0.6 < counts.get("0", 0) / 4096 < 0.8
