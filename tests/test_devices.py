import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from noisy_qubits.noise import DEVICES, build_noise_model, check_fits, run_counts
from noisy_qubits.noise.devices import get_backend


def _ladder(n=4, cx=30):
    qc = QuantumCircuit(n, n)
    qc.x(0)
    for _ in range(cx):
        qc.cx(0, 1)
    qc.measure(range(n), range(n))
    return qc


def test_unknown_device_and_missing_device():
    with pytest.raises(ValueError):
        build_noise_model("device", 50, device="FakeNope")
    with pytest.raises(ValueError):
        build_noise_model("device", 50)


@pytest.mark.parametrize("dev", DEVICES)
def test_devices_have_enough_qubits_and_accept_v2_names(dev):
    assert get_backend(dev).num_qubits >= 10
    build_noise_model("device", 50, device=dev + "V2")


def test_circuit_too_big_for_device_is_rejected():
    with pytest.raises(ValueError, match="Pick another device"):
        check_fits(QuantumCircuit(40), "FakeGuadalupe")


@pytest.mark.parametrize("slider,factor", [(50, 1.0), (100, 2.0)])
def test_readout_error_is_the_real_one_times_slider_over_50(slider, factor):
    real = get_backend("FakeKolkata").target["measure"][(0,)].error
    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)  # physical qubit 0, no transpile
    nm = build_noise_model("device", slider, device="FakeKolkata")
    counts = AerSimulator(noise_model=nm).run(qc, shots=20000).result().get_counts()
    assert counts.get("1", 0) / 20000 == pytest.approx(real * factor, abs=0.004)


def test_more_slider_means_worse_result_on_a_device():
    qc = _ladder()
    low = run_counts(qc, 2048, build_noise_model("device", 5, device="FakeKolkata"), "FakeKolkata", seed=1)
    high = run_counts(qc, 2048, build_noise_model("device", 100, device="FakeKolkata"), "FakeKolkata", seed=1)
    key = "0001"  # X on qubit 0, 30 CX = identity
    assert low.get(key, 0) > high.get(key, 0)
    assert low.get(key, 0) / 2048 > 0.7
