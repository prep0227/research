#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate paper/speed_sweep_section.md (Supplementary Table S1) from
sim/results_speed_sweep.json. Number discipline: values come only from the JSON."""
import json, pathlib

PAPER = pathlib.Path(__file__).resolve().parent
SIM = PAPER.parent / "sim"
D = json.loads((SIM / "results_speed_sweep.json").read_text(encoding="utf-8"))
SPEEDS = {"low": "0.5", "mid": "1.2", "high": "2.0"}

def fmt(v):
    return f"{v:.3f}"

def fmt_p(p):
    return "p<0.001" if p is not None and p < 0.001 else (f"{p:.3f}" if p is not None else "n/a")

lines = [
    "### S.1 Speed-gear sensitivity (supplementary)",
    "",
    "Nominal target speed gears 0.5 / 1.2 / 2.0 m/s, drifting-latency profile, 10 seeds. "
    "Hit rate (mean) by controller; gains are paired mean differences with one-sided paired t-test p-values "
    "(statistics computed from per-seed data in `sim/results_speed_sweep.json`).",
    "",
    "| scenario | speed (m/s) | B0 | B1 | Ours | Ours$-$B0 (pp, p) | Ours$-$B1 (pp, p) |",
    "|---|---|---|---|---|---|---|",
]
for sc in ["line", "circle", "s", "accel"]:
    for sp in ["low", "mid", "high"]:
        key = f"{sc}/{sp}"
        d = D["results"][key]
        b0, b1, o = d["B0"]["hit_rate"], d["B1"]["hit_rate"], d["Ours"]["hit_rate"]
        p0 = d["ours_vs_B0"]; p1 = d["ours_vs_B1"]
        p0s = fmt_p(p0["p"])
        p1s = fmt_p(p1["p"])
        lines.append(f"| {sc} | {SPEEDS[sp]} | {fmt(b0)} | {fmt(b1)} | {fmt(o)} | "
                     f"{p0['mean_diff_pp']:+.1f} ({p0s}) | {p1['mean_diff_pp']:+.1f} ({p1s}) |")
(PAPER / "speed_sweep_section.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("paper/speed_sweep_section.md written")
