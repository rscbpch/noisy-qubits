# Experiment table: what zero-noise extrapolation (ZNE) fixes

Highest slider value (1 to 100) that still passes, **without -> with ZNE (gain)**.
Pass rule: score >= 50% of the ideal score. 1024 shots, so +/- a few points.
A ZNE result only counts if it is reliable (the lowest measured score is at least 10 shots' worth).

| Noise setting | Superposition | QFT round trip (10 qubits) |
|---|---|---|
| Depolarizing (uniform) | 100 -> 100 (+0) | 18 -> 51 (+33) |
| Bit-flip (uniform) | 100 -> 100 (+0) | 9 -> 25 (+16) |
| Phase-flip (uniform) | 100 -> 100 (+0) | 12 -> 34 (+22) |
| Amplitude damping, T1 (uniform) | 100 -> 100 (+0) | 18 -> 46 (+28) |
| Readout error (uniform) | 100 -> 100 (+0) | 100 -> 100 (+0) |
| FakeGuadalupe | not run | 7 -> 20 (+13) |
| FakeKolkata | not run | 11 -> 27 (+16) |
| FakeMontreal | not run | 11 -> 25 (+14) |

100 means it passed at every slider value tested. Raw data: `docs/noise_table.csv`.
Regenerate: `uv run python -m noisy_qubits.experiments.noise_table --out results`
(about 15 minutes). Deutsch-Jozsa, QPE and Simon's rows are added by adding a
`Benchmark` in `src/noisy_qubits/experiments/benchmarks.py` once those algorithms exist.

Notes
- Uniform mode runs the circuit as written, so a controlled-phase or swap counts as one
  two-qubit gate. Device mode transpiles first and pays for the real gate count, which is
  why the QFT looks more fragile there.
- The search assumes pass at low noise and fail at high noise (plan, Section 13).
- Readout error at the top of the uniform scale (5%) is small enough that QFT still passes.
  ZNE cannot change it: the scores are identical at every noise factor.
