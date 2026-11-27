import pytest
from qiskit import qasm2
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

from noisy_qubits.algorithms import REGISTRY, qft
from noisy_qubits.noise import build_noise_model, transpile_for_device
from noisy_qubits.result import AlgorithmResult


@pytest.mark.parametrize("n", range(2, 11))
def test_no_noise_matches_theory(n):
    r = qft.run(n, 256, seed=1)
    assert isinstance(r, AlgorithmResult)
    assert r.ideal_score == pytest.approx(1.0)
    assert r.score == 1.0
    assert r.baseline == 1 / 2**n


@pytest.mark.parametrize("n", [2, 3, 5, 6])
def test_matches_qiskit_qft(n):
    # A round trip passes even if the QFT is wrong, so check the QFT on its own.
    assert Operator(qft.qft_circuit(n)).equiv(Operator(QFTGate(n)))


@pytest.mark.parametrize("state", ["000", "001", "100", "101", "111"])
def test_bit_order(state):
    r = qft.run(3, 64, input_state=state, seed=1)
    assert r.counts == {state: 64}


def test_default_input_state():
    assert qft.build().metadata["input_state"] == "0110010110"
    assert qft.build(4).metadata["input_state"] == "0110"


def test_uses_only_supported_gates():
    names = set(qft.build().count_ops())
    assert names <= {"x", "h", "cp", "swap", "barrier", "measure"}
    assert "cp(" in qasm2.dumps(qft.build())


@pytest.mark.parametrize("bad", ["01", "01100", "012", "0 1", "", 101])
def test_bad_input_state(bad):
    with pytest.raises(qft.InputError):
        qft.build(3, bad)


@pytest.mark.parametrize("n", [0, 1, 11, 2.5, "5", True])
def test_bad_qubit_count(n):
    with pytest.raises(qft.InputError):
        qft.build(n)


@pytest.mark.parametrize("degree", [-1, 4, 1.5, True])
def test_bad_approximation_degree(degree):
    with pytest.raises(qft.InputError):
        qft.build(4, approximation_degree=degree)


@pytest.mark.parametrize("shots", [0, -1, 1.5])
def test_bad_shots(shots):
    with pytest.raises(qft.InputError):
        qft.run(3, shots)


def test_approximation_drops_gates_and_fidelity():
    exact = qft.build(6).count_ops()["cp"]
    approx = qft.build(6, approximation_degree=3).count_ops()["cp"]
    assert approx < exact
    assert qft.approximation_fidelity(6, approximation_degree=0) == pytest.approx(1.0)
    assert qft.approximation_fidelity(6, approximation_degree=3) < 0.99
    # The round trip still looks perfect without noise.
    assert qft.run(6, 128, approximation_degree=3, seed=1).score == 1.0


def test_barrier_stops_transpiler_cancellation():
    with_barriers = qft.build(6)
    without = with_barriers.copy_empty_like()
    for inst in with_barriers.data:
        if inst.operation.name != "barrier":
            without.append(inst)

    def cx(circuit):
        return transpile_for_device(circuit, "FakeKolkata").count_ops()["cx"]

    assert cx(with_barriers) > cx(without)


def test_gate_noise_lowers_score():
    low = qft.run(6, 1024, build_noise_model("uniform", 5), seed=1).score
    high = qft.run(6, 1024, build_noise_model("uniform", 100), seed=1).score
    assert high < low < 1.0


def test_device_mode():
    nm = build_noise_model("device", 50, device="FakeKolkata")
    r = qft.run(4, 512, nm, device="FakeKolkata", seed=1)
    assert 1 / 16 < r.score < 1.0


def test_registered():
    assert REGISTRY["qft"] is qft.run
