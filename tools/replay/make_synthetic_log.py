#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a synthetic event log (schema in EVENT_LOG_SCHEMA.md) from sim
trajectories + latency profiles, so replay.py is testable without hardware."""
import json, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "sim"))
from trajectories import make_trajectory, az_el
from delay import make_delay

DT = 0.02
TAU_VISION_NOMINAL = 0.03

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="line")
    ap.add_argument("--delay", default="drift", choices=["fixed", "gamma", "drift"])
    ap.add_argument("--out", default="synthetic_log.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed); np.random.seed(a.seed)
    traj = make_trajectory(a.scenario)
    if a.delay == "drift":
        # same drift profile as sim/run_experiments.py (nominal -> nominal+60ms over T=6s)
        def vfn(t): return TAU_VISION_NOMINAL + 0.06 * (t / 6.0)
    else:
        vfn = make_delay(a.delay, TAU_VISION_NOMINAL, jitter=0.015, seed=7)
    events = []
    for k in range(int(6.0 / DT)):
        t = k * DT
        tau_v = vfn(t)
        t_meas = max(0.0, t - tau_v)
        pos = traj.position(t_meas) + rng.normal(0.0, 0.03, 3)
        events.append({"event": "cam_exposure", "t_start_ms": round((t-0.005)*1000,2),
                       "t_mid_ms": round(t*1000,2), "t_end_ms": round((t+0.005)*1000,2), "frame_id": k})
        events.append({"event": "detection", "t_meas_ms": round(t_meas*1000,2), "frame_id": k,
                       "pos": [round(float(x),4) for x in pos], "conf": 0.98})
        events.append({"event": "latency_measure", "t_ms": round(t*1000,2), "segment": "vision",
                       "value_ms": round(tau_v*1000,2)})
        events.append({"event": "target_truth", "t_ms": round(t*1000,2),
                       "pos": [round(float(x),4) for x in traj.position(t)]})
    out = pathlib.Path(a.out)
    with out.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"wrote {len(events)} events -> {out}")

if __name__ == "__main__":
    main()
