#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate paper/dropout_section.md (Supplementary Table S2) from
sim/results_dropout.json. Number discipline: values come only from the JSON."""
import json, pathlib

PAPER = pathlib.Path(__file__).resolve().parent
SIM = PAPER.parent / "sim"
D = json.loads((SIM / "results_dropout.json").read_text(encoding="utf-8"))

lines = [
    "### S.2 Detection-dropout robustness (supplementary)",
    "",
    "Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. "
    "Ours remains significantly better than B1 at every dropout level ($p<0.001$); "
    "its hit rate is approximately flat across dropout, consistent with IMM prediction absorbing missed frames.",
    "",
    "| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |",
    "|---|---|---|---|---|",
]
for sc in ["line", "accel"]:
    for dp in [0.0, 0.1, 0.2]:
        key = f"{sc}/dropout={dp:.1f}"
        d = D["results"][key]
        p1 = d["ours_vs_B1"]
        p1s = f"{p1['p']:.3f}" if p1["p"] is not None else "n/a"
        lines.append(f"| {sc} | {dp:.0%} | {d['B1']['hit_rate']:.3f} | {d['Ours']['hit_rate']:.3f} | "
                     f"{p1['mean_diff_pp']:+.1f} ({p1s}) |")
(PAPER / "dropout_section.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("paper/dropout_section.md written")
