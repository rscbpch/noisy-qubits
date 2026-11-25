"""Slider (1..100) -> real error values (plan, Section 6.3)."""
from __future__ import annotations

MAX_TWO_QUBIT_ERROR = 0.05   # uniform mode: slider 100 = 5% per two-qubit gate
SINGLE_QUBIT_RATIO = 0.1     # single-qubit gates get one tenth of that
DEVICE_REAL_SLIDER = 50      # device mode: slider 50 = the real device


def validate_slider(slider: int) -> int:
    if isinstance(slider, bool) or not isinstance(slider, int):
        raise ValueError(f"Noise slider must be a whole number from 1 to 100, got {slider!r}.")
    if not 1 <= slider <= 100:
        raise ValueError(f"Noise slider must be from 1 to 100, got {slider}.")
    return slider


def uniform_errors(slider: int) -> tuple[float, float]:
    """Return (single-qubit error, two-qubit error) for uniform mode."""
    validate_slider(slider)
    p2 = MAX_TWO_QUBIT_ERROR * slider / 100
    return p2 * SINGLE_QUBIT_RATIO, p2


def device_multiplier(slider: int) -> float:
    """Factor applied to a device's real calibrated error rates."""
    validate_slider(slider)
    return slider / DEVICE_REAL_SLIDER


def _pct(x: float) -> str:
    return f"{x * 100:.2f}".rstrip("0").rstrip(".")


def slider_label(mode: str, slider: int) -> str:
    """Text shown next to the slider."""
    if mode == "uniform":
        _, p2 = uniform_errors(slider)
        return f"Slider {slider} means {_pct(p2)}% error per gate"
    if mode == "device":
        m = device_multiplier(slider)
        return f"Slider {slider} means {m:g}x the real device error rates"
    raise ValueError(f"Unknown noise mode {mode!r}; use 'uniform' or 'device'.")
