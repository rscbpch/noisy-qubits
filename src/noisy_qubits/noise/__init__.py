"""Noise models (Member 5). Contract: docs/noise-contract.md."""
from __future__ import annotations

from typing import Literal

NoiseType = Literal[
    "depolarizing", "bit_flip", "phase_flip", "amplitude_damping", "readout"
]
Mode = Literal["uniform", "device"]


def build_noise_model(
    mode: Mode,
    slider: int,
    noise_type: NoiseType = "depolarizing",
    readout: float = 0.0,
    device: str | None = None,
):
    """Return a qiskit_aer NoiseModel for the slider value (1..100)."""
    raise NotImplementedError


def slider_label(mode: Mode, slider: int) -> str:
    """Text shown next to the slider, e.g. 'Slider 40 means 2% error per gate'."""
    raise NotImplementedError
