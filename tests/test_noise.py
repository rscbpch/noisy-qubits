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


def _p(qc, nm, key, shots=4096):
    counts = AerSimulator(noise_model=nm).run(qc, shots=shots).result().get_counts()
    return counts.get(key, 0) / shots


@pytest.mark.parametrize("nt", ["bit_flip", "phase_flip", "amplitude_damping"])
def test_new_types_build_and_validate(nt):
    build_noise_model("uniform", 50, noise_type=nt)
    with pytest.raises(ValueError):
        build_noise_model("uniform", 0, noise_type=nt)


def test_bit_flip_breaks_a_basis_state_circuit():
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    for _ in range(40):
        qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    assert _p(qc, build_noise_model("uniform", 100, noise_type="bit_flip"), "01") < 0.8


def test_phase_flip_cannot_change_a_basis_state_but_breaks_interference():
    basis = QuantumCircuit(2, 2)
    basis.x(0)
    for _ in range(40):
        basis.cx(0, 1)
    basis.measure([0, 1], [0, 1])
    nm = build_noise_model("uniform", 100, noise_type="phase_flip")
    assert _p(basis, nm, "01") == 1.0  # Z errors are invisible in the Z basis

    interf = QuantumCircuit(1, 1)
    interf.h(0)
    for _ in range(200):
        interf.rz(0, 0)
    interf.h(0)
    interf.measure(0, 0)  # ideal answer is always '0'
    assert _p(interf, nm, "0") < 0.8


def test_t1_pulls_one_down_but_never_zero_up():
    nm = build_noise_model("uniform", 100, noise_type="amplitude_damping")
    one = QuantumCircuit(1, 1)
    one.x(0)
    for _ in range(200):
        one.id(0)
    one.measure(0, 0)
    assert _p(one, nm, "1") < 0.6
    zero = QuantumCircuit(1, 1)
    for _ in range(200):
        zero.id(0)
    zero.measure(0, 0)
    assert _p(zero, nm, "0") == 1.0
