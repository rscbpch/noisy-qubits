from noisy_qubits.algorithms import superposition


def test_ideal_run_is_near_uniform():
    r = superposition.run(n_qubits=4, shots=8192)
    assert r.score > 0.9
    assert r.circuit.num_qubits == 4
