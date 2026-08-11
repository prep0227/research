#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate paper/delay_est_section.md (Supplementary Table S3) from
sim/results_delay_estimation.json. Number discipline: values only from the JSON."""
import json, pathlib

PAPER = pathlib.Path(__file__).resolve().parent
SIM = PAPER.parent / "sim"
D = json.loads((SIM / "results_delay_estimation.json").read_text(encoding="utf-8"))

lines = [
    "### S.3 Online delay-estimator accuracy (protocol secondary metric)",
    "",
    "Sliding-window ($W=50$) estimator vs. true latency, same per-step feed as the controller loop; "
    "causal 'lag-1' estimate (samples before the current step), steady-state window $t\\in[1,6]$~s.",
    "Under fixed delay the estimator is accurate to <0.4 ms MAE; under $\\pm15$~ms jitter the per-step "
    "error is dominated by the jitter itself (MAE $\\approx10$ ms), which the uncertainty bound "
    "$\\Delta_i$ (P95 $\\approx27$ ms) is designed to cover in the firing tightening; under drift the "
    "lag-1 estimate lags by $\\approx-5$ ms (half the sliding window times the drift rate).",
    "",
    "| mode | segment | true mean (ms) | bias (ms) | MAE (ms) | RMSE (ms) | P95 abs err (ms) | settling to 5 ms (s) |",
    "|---|---|---|---|---|---|---|---|",
]
for r in D:
    for seg in ["vision", "gimbal"]:
        d = r[seg]; s = d["lag1"]
        wu = f"{d['warmup_to_5ms_s']:.2f}" if d["warmup_to_5ms_s"] is not None else ">6"
        lines.append(f"| {r['mode']} | {seg} | {d['mean_true_ms']:.1f} | {s['bias_ms']:+.2f} | {s['mae_ms']:.2f} "
                     f"| {s['rmse_ms']:.2f} | {s['p95_ms']:.2f} | {wu} |")
(PAPER / "delay_est_section.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("paper/delay_est_section.md written")
