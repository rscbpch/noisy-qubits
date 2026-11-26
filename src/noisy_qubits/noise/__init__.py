"""Noise models (Member 5). Contract: docs/noise-contract.md."""
from __future__ import annotations

from typing import Literal

from qiskit_aer.noise import NoiseModel

from .devices import DEVICES, build_device_noise_model, check_fits, run_counts, transpile_for_device
from .slider import slider_label, validate_slider
from .uniform import NOISE_TYPES, build_uniform_noise_model

NoiseType = Literal[
    "depolarizing", "bit_flip", "phase_flip", "amplitude_damping", "readout"
]
Mode = Literal["uniform", "device"]

__all__ = [
    "build_noise_model", "slider_label", "NoiseType", "Mode", "NOISE_TYPES",
    "DEVICES", "check_fits", "run_counts", "transpile_for_device",
]


def build_noise_model(
    mode: Mode,
    slider: int,
    noise_type: NoiseType = "depolarizing",
    readout: float = 0.0,
    device: str | None = None,
) -> NoiseModel:
    """Return a qiskit_aer NoiseModel for the slider value (1..100)."""
    validate_slider(slider)
    if mode == "uniform":
        return build_uniform_noise_model(slider, noise_type, readout)
    if mode == "device":
        if device is None:
            raise ValueError(f"Device mode needs a device; choose one of {DEVICES}.")
        return build_device_noise_model(device, slider)
    raise ValueError(f"Unknown noise mode {mode!r}; use 'uniform' or 'device'.")
