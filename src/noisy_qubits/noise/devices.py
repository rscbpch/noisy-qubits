"""Fake IBM devices: noise copied from calibration data, scaled by the slider.

Device mode (plan, Section 6): the real calibrated errors are multiplied by
slider / 50, so slider 50 is the real device and slider 100 is twice as noisy.
Circuits must be transpiled to the device first (this adds SWAPs), so use
`run_counts()` or `transpile_for_device()` before simulating.
"""
from __future__ import annotations

from functools import lru_cache

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import average_gate_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
    thermal_relaxation_error,
)
from qiskit_ibm_runtime.fake_provider import (
    FakeGuadalupeV2,
    FakeKolkataV2,
    FakeMontrealV2,
)

from .slider import device_multiplier

_BACKENDS = {
    "FakeGuadalupe": FakeGuadalupeV2,
    "FakeKolkata": FakeKolkataV2,
    "FakeMontreal": FakeMontrealV2,
}
DEVICES = tuple(_BACKENDS)
MIN_QUBITS = 10
DM_MAX_QUBITS = 12
TRANSPILE_SEED = 7  # fixed, so the same circuit always maps the same way
_SKIP = {"measure", "reset", "delay", "barrier"}


def _canonical(device: str) -> str:
    name = device[:-2] if isinstance(device, str) and device.endswith("V2") else device
    if name not in _BACKENDS:
        raise ValueError(f"Unknown device {device!r}; choose one of {DEVICES}.")
    return name


@lru_cache(maxsize=None)
def get_backend(device: str):
    backend = _BACKENDS[_canonical(device)]()
    if backend.num_qubits < MIN_QUBITS:
        raise ValueError(f"{device} has only {backend.num_qubits} qubits; need at least {MIN_QUBITS}.")
    return backend


def check_fits(circuit: QuantumCircuit, device: str) -> None:
    n = get_backend(device).num_qubits
    if circuit.num_qubits > n:
        raise ValueError(
            f"Circuit uses {circuit.num_qubits} qubits but {device} has {n}. Pick another device."
        )


def transpile_for_device(circuit: QuantumCircuit, device: str) -> QuantumCircuit:
    """Map the circuit onto the device layout and basis gates (adds SWAPs)."""
    check_fits(circuit, device)
    return transpile(
        circuit,
        backend=get_backend(device),
        optimization_level=1,
        seed_transpiler=TRANSPILE_SEED,
    )


def _depol_param(error: float, relax_error, dim: int) -> float:
    """Depolarizing parameter so that depolarizing + relaxation add up to `error`."""
    relax_infid = 0.0
    if relax_error is not None:
        relax_infid = 1 - average_gate_fidelity(relax_error.to_quantumchannel())
    if error <= relax_infid:
        return 0.0
    p = dim * (error - relax_infid) / (dim * (1 - relax_infid) - 1)
    return min(max(p, 0.0), dim * dim / (dim * dim - 1))


def _thermal(backend, qubits, duration: float):
    """Thermal relaxation on each qubit of a gate (None if no T1/T2 data)."""
    err = None
    for q in qubits:
        props = backend.qubit_properties(q)
        t1, t2 = getattr(props, "t1", None), getattr(props, "t2", None)
        if not t1 or not t2 or duration <= 0:
            return None
        one = thermal_relaxation_error(t1, min(t2, 2 * t1), duration)
        err = one if err is None else err.tensor(one)
    return err


def build_device_noise_model(device: str, slider: int) -> NoiseModel:
    """Noise model from the device's calibration data, scaled by slider/50."""
    m = device_multiplier(slider)
    backend = get_backend(device)
    target = backend.target
    nm = NoiseModel(basis_gates=[n for n in target.operation_names if n not in _SKIP])

    for name in target.operation_names:
        if name in _SKIP:
            continue
        for qargs, props in target[name].items():
            if qargs is None or props is None or props.error is None:
                continue
            n = len(qargs)
            dim = 2 ** n
            error = min(props.error * m, dim / (dim + 1))
            # More noise also means longer effective gate time for T1/T2
            relax = _thermal(backend, qargs, (props.duration or 0.0) * m)
            p = _depol_param(error, relax, dim)
            err = depolarizing_error(p, n) if p > 0 else None
            if relax is not None:
                err = relax if err is None else err.compose(relax)
            if err is not None:
                nm.add_quantum_error(err, name, list(qargs))

    for (q,), props in target["measure"].items():
        if props is not None and props.error is not None:
            r = min(props.error * m, 0.5)
            nm.add_readout_error(ReadoutError([[1 - r, r], [r, 1 - r]]), [q])
    return nm


def run_counts(
    circuit: QuantumCircuit, shots: int, noise_model: NoiseModel | None = None,
    device: str | None = None, seed: int | None = None,
) -> dict[str, int]:
    """Simulate. With a device, transpile to it first. Returns the counts."""
    if device is not None:
        circuit = transpile_for_device(circuit, device)
    active = {circuit.find_bit(q).index for inst in circuit.data for q in inst.qubits}
    # Density matrix evolves the noisy state once and then samples, which is
    # ~3x faster than one trajectory per shot for deep 10-qubit circuits.
    # It needs 4^n memory, so fall back above 12 active qubits.
    method = "density_matrix" if noise_model is not None and len(active) <= DM_MAX_QUBITS else "automatic"
    sim = AerSimulator(noise_model=noise_model, method=method, seed_simulator=seed)
    return sim.run(circuit, shots=shots).result().get_counts()
