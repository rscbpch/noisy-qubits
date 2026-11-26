# Noise and error handling: write-up (Member 5)

## What was built

| Part | Where | What it does |
|---|---|---|
| Slider | `noise/slider.py` | Turns the 1 to 100 slider into real error rates and the label text. Uniform: 5% x slider/100 per two-qubit gate (a tenth for one-qubit gates). Device: real calibrated errors x slider/50. |
| Uniform noise | `noise/uniform.py` | Five noise types: depolarizing (main), bit-flip, phase-flip, T1 amplitude damping, readout error. |
| Fake devices | `noise/devices.py` | Noise built from the calibration data of FakeGuadalupe, FakeKolkata and FakeMontreal (gate errors, T1/T2, readout per qubit), scaled by the slider. Circuits are mapped to the device with a fixed seed. |
| Runner | `noise.run_counts` | Simulates a circuit with or without a device. Uses the density-matrix method, about 3x faster than the default for deep 10-qubit circuits. |
| ZNE | `mitigation/zne.py` | Gate folding at noise x1, x2, x3, an exponential fit, and the value at zero noise. Reports whether the fit is reliable. |
| Experiments | `experiments/` | Finds the highest passing slider with and without ZNE and writes the table. |
| About tab | `frontend/src/components/AboutTab.tsx` | Explains the selected algorithm and the noise types. Text lives in `data/aboutContent.ts`. |
| Contract | `docs/noise-contract.md` | The function signatures the team codes against. |

39 tests cover the slider, each noise type (for example, a phase flip cannot change a plain
0/1 result but breaks interference), device noise (slider 50 gives the real readout error,
slider 100 gives double), and ZNE (folding never changes what a circuit computes).

## Results (see docs/noise-table.md)

1. **ZNE helps with gate noise.** On the 10-qubit QFT round trip it raised the highest passing
   slider by 13 to 33 points for depolarizing, bit-flip, phase-flip, T1 and all three devices.
2. **ZNE cannot fix readout error.** The score is the same at every noise factor.
3. **Phase-flip breaks QFT** even though it is invisible on basis states, because QFT relies
   on interference.
4. **A real device is too noisy for a 10-qubit QFT round trip.** Slider 50 is the real
   device, and the QFT passes only up to about 11 raw and 25 to 27 with ZNE.
5. **Superposition passes at every slider value in every noise type.** It is a control case,
   but the plan's claim that readout error breaks it did not hold at our scale.

## Choices and why

- **Exponential fit.** Compared with linear and quadratic (Richardson) fits: lowest spread at
  1024 shots and the best for T1 decay. Richardson was slightly closer for depolarizing noise
  but jumpier.
- **Reliability guard.** Without it, depolarizing QFT looked like +58 (recovered up to slider
  76), but at that point the fit rested on a raw score of 6% and one correct shot out of 1024
  at x3. A result now counts only if the lowest measured score is at least 10 shots' worth.
  The honest figure is +33.
- **Folding.** Only gates whose inverse exists in the noise model are folded, and rz is skipped
  in device mode (it is virtual on IBM hardware).

## Limits to state in the report

- ZNE is unreliable at high noise and cannot rescue near-pure noise (the guard enforces this).
- Results are statistical: about 3 points of shot noise at 1024 shots.
- The highest-passing search assumes pass at low noise and fail at high noise.
- Uniform mode counts each gate once; device mode counts transpiled gates.
- Only Superposition and the QFT round trip are measured so far.

## Open items for the team

- Every algorithm needs a separate `score(counts, ...)` so ZNE can re-score. The Superposition
  score should use per-qubit bias (about 0.97 ideal at 1024 shots); the current score is about 0.64.
- The test flow must report FAIL, not RECOVERED, when `ZNEResult.reliable` is False.
- A mitigated deep circuit takes about 12 s, and one compare-grid cell with ZNE takes 1.5 to 2.5
  minutes. The grid needs caching and a coarse slider step.
- Fill the Deutsch-Jozsa, QPE and Simon's rows once those algorithms exist.
