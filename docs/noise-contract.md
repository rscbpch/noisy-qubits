# Noise and mitigation contract

Owner: Member 5 (noise and error handling). Other members code against these
signatures. Changing one needs a heads-up to the team (plan, Working rules).

## 1. Noise model

```python
from noisy_qubits.noise import build_noise_model, slider_label

nm = build_noise_model(
    mode="uniform",            # "uniform" | "device"
    slider=40,                 # whole number 1..100
    noise_type="depolarizing", # "depolarizing" | "bit_flip" | "phase_flip"
                               # | "amplitude_damping" | "readout"
    readout=0.0,               # extra readout error, 0..1 (uniform mode only)
    device=None,               # e.g. "FakeKolkata" (device mode only)
)  # -> qiskit_aer.noise.NoiseModel
```

- Uniform: two-qubit gate error p = 5% * slider/100, single-qubit gates p/10.
- Device: real calibrated errors * slider/50 (slider 50 = the real device).
- `slider_label(mode, slider)` returns the text shown next to the slider,
  e.g. "Slider 40 means 2% error per gate".
- Invalid input raises `ValueError` with a readable message (plan, Section 13).

## 2. What every algorithm module must provide

ZNE re-runs the same circuit with folded gates, so building, running and
scoring are separate:

```python
def build(...) -> QuantumCircuit
def score(counts: dict[str, int], **params) -> float   # the Section 4 score
def run(..., shots=1024, noise_model=None) -> AlgorithmResult
```

`run()` is just build + simulate + `score()`. Superposition already follows
this (`uniformity()` is its score function).

## 3. Mitigation (ZNE)

```python
from noisy_qubits.mitigation import zne

res = zne(
    circuit,                 # user-level circuit, with measurements
    noise_model,             # same model as the raw run
    shots=1024,
    score_fn=lambda counts: score(counts, **params),
    factors=(1, 2, 3),
    device=None,             # device mode: pass the same device name as the raw run
    method="exponential",    # "exponential" | "linear" | "richardson"
    seed=None,
)  # -> ZNEResult
```

`ZNEResult` fields: `factors`, `scores` (one per factor), `mitigated`
(curve value at noise 0, clipped to 0..1), `raw` (score at factor 1),
`method`, and `curve` (list of (factor, score) points from 0 to the largest
factor, for the ZNE picture).

- Gate folding is done on the transpiled circuit (device mode), so the extra
  gates get noise. Only gates whose inverse is in the noise model are folded.
- Fit: exponential by default. It was the most stable at 1024 shots and the
  best for T1 decay (see the experiment table, Section 10.2).
- Cost: the circuit runs at every factor, about 3x the raw run for the
  gate-heavy part. A deep 10-qubit QFT test takes about 12 s.
- Readout error is not mitigated (known limit, plan Section 10).
