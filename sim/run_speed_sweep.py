#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Speed-gear sensitivity sweep (supplementary, NOT canonical).

Design: scenario x nominal_speed{0.5,1.2,2.0 m/s} x controller{B0,B1,Ours} x 10 seeds,
delay_mode=drift (most challenging). Scale factors chosen per scenario so the nominal
target speed matches the protocol speed gears (0.5/1.2/2.0 m/s).

Writes: results_speed_sweep.jsonl (raw) + results_speed_sweep.json (aggregated) +
        results_speed_sweep.md (summary, used by paper generator).
"""
import json, pathlib, time
import numpy as np
from scipy import stats

from run_experiments import run_once, SEEDS, paired

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "results_speed_sweep.jsonl"
SCENARIOS = ["line", "circle", "s", "accel"]
SPEEDS = {"low": 0.5, "mid": 1.2, "high": 2.0}
# scale so that nominal speed ~ target m/s:
# line |v|=1.3, circle r*omega=0.64, s vx=1.0, accel v_cruise=2.0 (all at scale=1)
SCALE = {
    "line":   {"low": 0.5/1.30, "mid": 1.2/1.30, "high": 2.0/1.30},
    "circle": {"low": 0.5/0.64, "mid": 1.2/0.64, "high": 2.0/0.64},
    "s":      {"low": 0.5/1.00, "mid": 1.2/1.00, "high": 2.0/1.00},
    "accel":  {"low": 0.5/2.00, "mid": 1.2/2.00, "high": 2.0/2.00},
}
CONTROLLERS = ["B0", "B1", "Ours"]
DELAY_MODE = "drift"

def _key(r):
    return (r["scenario"], r["scale"], r["controller"], r["seed"])

def main():
    t0 = time.time()
    raw = {}
    try:
        for line in RAW.open(encoding="utf-8"):
            r = json.loads(line); raw[_key(r)] = r
    except FileNotFoundError:
        pass
    todo = [(sc, sp, c, sd) for sc in SCENARIOS for sp in SPEEDS for c in CONTROLLERS for sd in SEEDS]
    missing = [t for t in todo if t not in raw]
    print(f"speed sweep: {len(todo)} planned, {len(missing)} to run", flush=True)
    with RAW.open("a", encoding="utf-8") as f:
        for i, (sc, sp, c, sd) in enumerate(missing):
            r = run_once(sc, DELAY_MODE, c, sd, scale=SCALE[sc][sp])
            raw[_key(r)] = r
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if (i+1) % 60 == 0:
                print(f"[{time.time()-t0:.1f}s] {i+1}/{len(missing)}", flush=True)
    results = list(raw.values())
    print(f"[{time.time()-t0:.1f}s] done: {len(results)} runs", flush=True)

    # aggregated json
    out = {"design": "scenario x nominal speed {0.5,1.2,2.0} m/s x {B0,B1,Ours} x 10 seeds, drift delay",
           "scales": SCALE, "results": {}}
    for sc in SCENARIOS:
        for sp in SPEEDS:
            key = f"{sc}/{sp}"
            out["results"][key] = {}
            for c in CONTROLLERS:
                sub = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]==c
                       and abs(r["scale"]-SCALE[sc][sp])<1e-9 and r["seed"] in SEEDS]
                out["results"][key][c] = {"hit_rate": float(np.mean(sub)), "std": float(np.std(sub))}
            o = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]=="Ours" and abs(r["scale"]-SCALE[sc][sp])<1e-9 and r["seed"] in SEEDS]
            b0 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]=="B0" and abs(r["scale"]-SCALE[sc][sp])<1e-9 and r["seed"] in SEEDS]
            b1 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["controller"]=="B1" and abs(r["scale"]-SCALE[sc][sp])<1e-9 and r["seed"] in SEEDS]
            out["results"][key]["ours_vs_B0"] = paired(o, b0)
            out["results"][key]["ours_vs_B1"] = paired(o, b1)
    (HERE / "results_speed_sweep.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # markdown summary
    md = ["# Speed-Gear Sensitivity (Supplementary, drift delay)\n",
          "Nominal target speed gears 0.5 / 1.2 / 2.0 m/s; 10 seeds; drift latency profile.",
          "", "| scenario | speed (m/s) | B0 | B1 | Ours | Ours-B0 (pp, p) | Ours-B1 (pp, p) |"]
    md.append("|---|---|---|---|---|---|---|")
    for sc in SCENARIOS:
        for sp in SPEEDS:
            key = f"{sc}/{sp}"; d = out["results"][key]
            def fmt(x, prec=3):
                return f"{x:.{prec}f}"
            v0, v1, vo = d["B0"]["hit_rate"], d["B1"]["hit_rate"], d["Ours"]["hit_rate"]
            p0 = d["ours_vs_B0"]; p1 = d["ours_vs_B1"]
            p0s = f"{p0['p']:.3f}" if p0["p"] is not None else "n/a"
            p1s = f"{p1['p']:.3f}" if p1["p"] is not None else "n/a"
            md.append(f"| {sc} | {SPEEDS[sp]:.1f} | {fmt(v0)} | {fmt(v1)} | {fmt(vo)} | "
                      f"{p0['mean_diff_pp']:+.1f} ({p0s}) | {p1['mean_diff_pp']:+.1f} ({p1s}) |")
    (HERE / "results_speed_sweep.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("wrote results_speed_sweep.json + .md")

if __name__ == "__main__":
    main()
