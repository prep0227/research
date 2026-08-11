#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Online delay-estimator accuracy (protocol secondary metric: time-delay estimation error).

Measures the sliding-window DelayEstimator (sim/delay_estimator.py) against the three
latency profiles used in the paper, with the SAME feed convention as run_once
(per-step sample = true delay + measurement noise). We report BOTH:
  - "used"  : mean after adding the current sample (exactly what run_once uses), and
  - "lag-1" : mean over samples strictly before the current step (conservative,
              what a causal implementation can actually know).
Steady-state window: t in [1, 6] s (after warm-up). Also reports warm-up time to 5 ms bias.
"""
import json, pathlib
import numpy as np

from delay import make_delay
from delay_estimator import DelayEstimator

DT = 0.02
T = 6.0
TAU_VISION_NOMINAL = 0.03
TAU_GIMBAL_NOMINAL = 0.06
N_VIS, N_GIM = 0.002, 0.003

def profiles(mode):
    if mode == "fixed":
        return (lambda t: TAU_VISION_NOMINAL, lambda t: TAU_GIMBAL_NOMINAL)
    if mode == "gamma":
        vd = make_delay("gamma", TAU_VISION_NOMINAL, jitter=0.015, seed=7)
        return (lambda t: vd.sample(t), lambda t: TAU_GIMBAL_NOMINAL)
    if mode == "drift":
        return (lambda t: TAU_VISION_NOMINAL + 0.06*(t/T), lambda t: TAU_GIMBAL_NOMINAL + 0.06*(t/T))
    raise ValueError(mode)

def run(mode, seed=0):
    rng = np.random.default_rng(seed); np.random.seed(seed)
    vfn, gfn = profiles(mode)
    ev, eg = DelayEstimator(), DelayEstimator()
    used_vis, lag_vis, true_vis = [], [], []
    used_gim, lag_gim, true_gim = [], [], []
    warmup_vis = None; warmup_gim = None
    for k in range(int(T / DT)):
        t = k * DT
        tv, tg = vfn(t), gfn(t)
        lag_vis.append(ev.mean() - tv)          # before adding current sample
        lag_gim.append(eg.mean() - tg)
        ev.add(tv + rng.normal(0.0, N_VIS))
        eg.add(tg + rng.normal(0.0, N_GIM))
        used_vis.append(ev.mean() - tv)
        used_gim.append(eg.mean() - tg)
        true_vis.append(tv); true_gim.append(tg)
        if warmup_vis is None and abs(lag_vis[-1]) < 0.005:
            warmup_vis = t
        if warmup_gim is None and abs(lag_gim[-1]) < 0.005:
            warmup_gim = t
    def stats(err):
        a = np.asarray(err)
        return {"bias_ms": float(np.mean(a)*1e3), "mae_ms": float(np.mean(np.abs(a))*1e3),
                "rmse_ms": float(np.sqrt(np.mean(np.square(a)))*1e3),
                "p95_ms": float(np.quantile(np.abs(a), 0.95)*1e3)}
    def steady(err):
        # t in [1,6]s => skip first 50 steps
        return stats(err[50:])
    return {"mode": mode,
            "vision": {"used": steady(used_vis), "lag1": steady(lag_vis),
                       "warmup_to_5ms_s": (warmup_vis if warmup_vis is not None else None),
                       "mean_true_ms": float(np.mean(true_vis)*1e3)},
            "gimbal": {"used": steady(used_gim), "lag1": steady(lag_gim),
                       "warmup_to_5ms_s": (warmup_gim if warmup_gim is not None else None),
                       "mean_true_ms": float(np.mean(true_gim)*1e3)}}

def main():
    out = [run(m) for m in ["fixed", "gamma", "drift"]]
    p = pathlib.Path(__file__).resolve().parent
    (p / "results_delay_estimation.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    md = ["# Online Delay-Estimator Accuracy (protocol secondary metric)\n",
          "Sliding-window (W=50) estimator vs. true latency; per-step feed as in run_once.",
          "Steady-state window t in [1,6] s; 'lag-1' = causal (samples before current step).",
          "", "| mode | segment | true mean (ms) | bias (ms) | MAE (ms) | RMSE (ms) | P95 abs err (ms) | warm-up to 5 ms (s) |",
          "|---|---|---|---|---|---|---|---|"]
    for r in out:
        for seg in ["vision", "gimbal"]:
            d = r[seg]; s = d["lag1"]
            wu = f"{d['warmup_to_5ms_s']:.2f}" if d["warmup_to_5ms_s"] is not None else ">6"
            md.append(f"| {r['mode']} | {seg} | {d['mean_true_ms']:.1f} | {s['bias_ms']:+.2f} | {s['mae_ms']:.2f} "
                      f"| {s['rmse_ms']:.2f} | {s['p95_ms']:.2f} | {wu} |")
    (p / "results_delay_estimation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))

if __name__ == "__main__":
    main()
