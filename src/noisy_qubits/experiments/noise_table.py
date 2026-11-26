"""Fill the 'what ZNE fixes' table (plan Section 10.2) and the highest passing slider.

    uv run python -m noisy_qubits.experiments.noise_table --out results

For each benchmark and noise setting it finds the highest slider (1..100) that
still passes, without and with ZNE. The search assumes pass at low noise and
fail at high noise (plan, Section 13), so it takes about 7 steps per search.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from ..mitigation import zne
from ..noise import DEVICES, NOISE_TYPES, build_noise_model, run_counts
from .benchmarks import Benchmark, all_benchmarks

SHOTS = 1024
SEED = 11


def highest_passing(passes, lo: int = 1, hi: int = 100) -> int:
    """Largest slider in lo..hi with passes(slider) True (0 if even `lo` fails)."""
    if not passes(lo):
        return 0
    if passes(hi):
        return hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if passes(mid) else (lo, mid)
    return lo


def run_setting(b: Benchmark, mode: str, noise_type: str = "depolarizing", device: str | None = None) -> dict:
    ideal = b.score(run_counts(b.circuit, SHOTS, None, seed=SEED))
    thr = b.pass_fraction * ideal
    dev = device if mode == "device" else None
    raw_cache, zne_cache = {}, {}

    def model(s):
        return build_noise_model(mode, s, noise_type=noise_type, device=dev)

    def raw_ok(s):
        if s not in raw_cache:
            raw_cache[s] = b.score(run_counts(b.circuit, SHOTS, model(s), device=dev, seed=SEED))
        return raw_cache[s] >= thr

    def zne_ok(s):  # test flow: raw first, ZNE only if raw fails; unreliable fits do not count
        if s not in zne_cache:
            r = zne(b.circuit, model(s), SHOTS, b.score, device=dev, seed=SEED)
            zne_cache[s] = max(r.raw, r.mitigated if r.reliable else 0.0)
        return zne_cache[s] >= thr

    t = time.time()
    without = highest_passing(raw_ok)
    with_zne = max(highest_passing(zne_ok), without)
    return dict(benchmark=b.name, mode=mode, setting=device if dev else noise_type, ideal=round(ideal, 3),
                pass_line=round(thr, 3), without=without, with_zne=with_zne, gain=with_zne - without,
                seconds=round(time.time() - t))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--only", default=None, help="benchmark name")
    ap.add_argument("--no-devices", action="store_true")
    args = ap.parse_args()

    rows = []
    for b in all_benchmarks():
        if args.only and b.name != args.only:
            continue
        settings = [("uniform", nt, None) for nt in NOISE_TYPES]
        if not args.no_devices and b.name != "superposition":
            settings += [("device", "mixed", d) for d in DEVICES]
        for mode, nt, dev in settings:
            row = run_setting(b, mode, nt, dev)
            rows.append(row)
            print(row, flush=True)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    with open(out / "noise_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    settings = list(dict.fromkeys(r["setting"] for r in rows))
    names = list(dict.fromkeys(r["benchmark"] for r in rows))
    cell = {(r["setting"], r["benchmark"]): f'{r["without"]} -> {r["with_zne"]} (+{r["gain"]})' for r in rows}
    lines = ["| Noise setting | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for s in settings:
        lines.append(f"| {s} | " + " | ".join(cell.get((s, n), "-") for n in names) + " |")
    (out / "noise_table.md").write_text(
        "Highest passing slider, without -> with ZNE (gain). 1024 shots, +/- a few points.\n\n" + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
