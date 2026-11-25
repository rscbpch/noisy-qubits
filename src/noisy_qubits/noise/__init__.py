"""Noise models (Member 5). Contract: docs/noise-contract.md."""
from __future__ import annotations

from typing import Literal

from qiskit_aer.noise import NoiseModel

from .slider import slider_label, validate_slider
from .uniform import NOISE_TYPES, build_uniform_noise_model

NoiseType = Literal[
    "depolarizing", "bit_flip", "phase_flip", "amplitude_damping", "readout"
]
Mode = Literal["uniform", "device"]

__all__ = ["build_noise_model", "slider_label", "NoiseType", "Mode", "NOISE_TYPES"]


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
        raise NotImplementedError("Device mode comes in step 3.")
    raise ValueError(f"Unknown noise mode {mode!r}; use 'uniform' or 'device'.")
