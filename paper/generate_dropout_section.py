#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate paper/dropout_section.md (Supplementary Table S2) from
sim/results_dropout.json. Number discipline: values come only from the JSON."""
import json, pathlib

PAPER = pathlib.Path(__file__).resolve().parent
SIM = PAPER.parent / "sim"
D = json.loads((SIM / "results_dropout.json").read_text(encoding="utf-8"))

def fmt_p(p):
    return "p<0.001" if p is not None and p < 0.001 else (f"{p:.3f}" if p is not None else "n/a")

_dd = {f"{sc}/dropout={dp:.1f}": D["results"][f"{sc}/dropout={dp:.1f}"]["ours_vs_B1"]
          for sc in ["line", "accel"] for dp in [0.0, 0.1, 0.2]}
_lin0 = _dd["line/dropout=0.0"]["mean_diff_pp"]; _lin0p = fmt_p(_dd["line/dropout=0.0"]["p"])
_lin1 = _dd["line/dropout=0.1"]["mean_diff_pp"]; _lin1p = fmt_p(_dd["line/dropout=0.1"]["p"])
_lin2 = _dd["line/dropout=0.2"]["mean_diff_pp"]; _lin2p = fmt_p(_dd["line/dropout=0.2"]["p"])
_acc0 = _dd["accel/dropout=0.0"]["mean_diff_pp"]; _acc0p = fmt_p(_dd["accel/dropout=0.0"]["p"])
_acc1 = _dd["accel/dropout=0.1"]["mean_diff_pp"]; _acc1p = fmt_p(_dd["accel/dropout=0.1"]["p"])
_acc2 = _dd["accel/dropout=0.2"]["mean_diff_pp"]; _acc2p = fmt_p(_dd["accel/dropout=0.2"]["p"])
lines = [
    "### S.2 Detection-dropout robustness (supplementary)",
    "",
    f"Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. "
    f"Ours is significantly better than B1 at 0% and 10% dropout in both scenarios ($p<0.05$: line {_lin0:+.1f}/{_lin1:+.1f} pp, "
    f"accel {_acc0:+.1f}/{_acc1:+.1f} pp). At 20% dropout the line gain remains significant ({_lin2:+.1f} pp, {_lin2p}) but the "
    f"accel gain narrows to {_acc2:+.1f} pp ({_acc2p}), so the benefit degrades as detections are lost on the fastest "
    f"trajectory; multi-model prediction absorbs missed frames on line but not fully on accelerating motion.",
    "",
    "| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |",
    "|---|---|---|---|---|",
]
for sc in ["line", "accel"]:
    for dp in [0.0, 0.1, 0.2]:
        key = f"{sc}/dropout={dp:.1f}"
        d = D["results"][key]
        p1 = d["ours_vs_B1"]
        p1s = fmt_p(p1["p"])
        lines.append(f"| {sc} | {dp:.0%} | {d['B1']['hit_rate']:.3f} | {d['Ours']['hit_rate']:.3f} | "
                     f"{p1['mean_diff_pp']:+.1f} ({p1s}) |")
(PAPER / "dropout_section.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("paper/dropout_section.md written")
