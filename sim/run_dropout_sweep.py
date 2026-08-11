#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detection-dropout robustness sweep (supplementary, NOT canonical).

Design: scenario{line,accel} x dropout{0.0,0.1,0.2} x controller{B1,Ours} x 10 seeds,
delay_mode=drift. Quantifies sensitivity to missed/failed detections (real pipelines
drop frames); dropout=0.0 reproduces the canonical B1/Ours drift numbers.

Writes: results_dropout.jsonl (raw) + results_dropout.json (aggregated) +
        results_dropout.md (summary, consumed by paper generator).
"""
import json, pathlib, time
import numpy as np

from run_experiments import run_once, SEEDS, paired

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "results_dropout.jsonl"
SCENARIOS = ["line", "accel"]
DROPOUTS = [0.0, 0.1, 0.2]
CONTROLLERS = ["B1", "Ours"]
DELAY_MODE = "drift"

def _key(r):
    return (r["scenario"], r["dropout"], r["controller"], r["seed"])

def main():
    t0 = time.time()
    raw = {}
    try:
        for line in RAW.open(encoding="utf-8"):
            r = json.loads(line); raw[_key(r)] = r
    except FileNotFoundError:
        pass
    todo = [(sc, dp, c, sd) for sc in SCENARIOS for dp in DROPOUTS for c in CONTROLLERS for sd in SEEDS]
    missing = [t for t in todo if t not in raw]
    print(f"dropout sweep: {len(todo)} planned, {len(missing)} to run", flush=True)
    with RAW.open("a", encoding="utf-8") as f:
        for i, (sc, dp, c, sd) in enumerate(missing):
            r = run_once(sc, DELAY_MODE, c, sd, dropout=dp)
            raw[_key(r)] = r
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if (i+1) % 40 == 0:
                print(f"[{time.time()-t0:.1f}s] {i+1}/{len(missing)}", flush=True)
    results = list(raw.values())
    print(f"[{time.time()-t0:.1f}s] done: {len(results)}", flush=True)

    out = {"design": "scenario{line,accel} x dropout{0,10,20%} x {B1,Ours} x 10 seeds, drift delay",
           "results": {}}
    for sc in SCENARIOS:
        for dp in DROPOUTS:
            key = f"{sc}/dropout={dp:.1f}"
            out["results"][key] = {}
            for c in CONTROLLERS:
                sub = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]==c
                       and abs(r["dropout"]-dp) < 1e-9 and r["seed"] in SEEDS]
                out["results"][key][c] = {"hit_rate": float(np.mean(sub)), "std": float(np.std(sub))}
            o = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]=="Ours" and abs(r["dropout"]-dp)<1e-9 and r["seed"] in SEEDS]
            b1 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]=="B1" and abs(r["dropout"]-dp)<1e-9 and r["seed"] in SEEDS]
            out["results"][key]["ours_vs_B1"] = paired(o, b1)
    (HERE / "results_dropout.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Detection-Dropout Robustness (Supplementary, drift delay)\n",
          "Dropout probability applied to detection updates; 10 seeds.",
          "", "| scenario | dropout | B1 | Ours | Ours-B1 (pp, p) |"]
    md.append("|---|---|---|---|---|")
    for sc in SCENARIOS:
        for dp in DROPOUTS:
            key = f"{sc}/dropout={dp:.1f}"; d = out["results"][key]
            p1 = d["ours_vs_B1"]; p1s = f"{p1['p']:.3f}" if p1["p"] is not None else "n/a"
            md.append(f"| {sc} | {dp:.0%} | {d['B1']['hit_rate']:.3f} | {d['Ours']['hit_rate']:.3f} | "
                      f"{p1['mean_diff_pp']:+.1f} ({p1s}) |")
    (HERE / "results_dropout.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("wrote results_dropout.json + .md")

if __name__ == "__main__":
    main()
