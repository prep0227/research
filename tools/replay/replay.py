#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline replay: run B0/B1/Ours control laws on a recorded event log
(detection stream + latency measurements + target truth) and compare.

The detection/PnP front end is identical across controllers; only the
prediction/control/firing-decision blocks differ -> isolates their contribution.

Usage:
    python3 replay.py --log log.jsonl [--controller B0|B1|Ours] [--all]
"""
import argparse, json, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "sim"))
from run_experiments import build_controller, DelayPair, DT, T, TAU_FIRE, GIMBAL_POS, V_BULLET, ACC_MAX, RATE_MAX, TAU_GIMBAL_NOMINAL, TAU_VISION_NOMINAL, FireState
from estimator import TargetIMM
from gimbal import Gimbal
from metrics import run_metrics
from trajectories import az_el

class TruthTraj:
    """Interpolated target-truth trajectory from log target_truth events."""
    def __init__(self, points):
        self.ts = np.array([p[0] for p in points])
        self.pos = np.array([p[1] for p in points])
    def position(self, t):
        return np.array([np.interp(t, self.ts, self.pos[:, i]) for i in range(3)])
    def velocity(self, t):
        return np.zeros(3)

def load_log(path):
    events = []
    for line in pathlib.Path(path).open(encoding="utf-8"):
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events

def build_streams(events):
    dets = [(e["t_meas_ms"]/1000.0, np.asarray(e["pos"], float))
            for e in events if e["event"] == "detection"]
    dets.sort(key=lambda d: d[0])
    truth = [(e["t_ms"]/1000.0, np.asarray(e["pos"], float))
             for e in events if e["event"] == "target_truth"]
    truth.sort(key=lambda d: d[0])
    lat_vis = [e["value_ms"]/1000.0 for e in events if e["event"] == "latency_measure" and e.get("segment") in ("vision", "cam")]
    lat_gim = [e["value_ms"]/1000.0 for e in events if e["event"] == "latency_measure" and e.get("segment") == "gimbal"]
    return dets, truth, lat_vis, lat_gim

def replay(events, controller_name, seed=0, estimator_type="IMM"):
    rng = np.random.default_rng(seed); np.random.seed(seed)
    dets, truth, lat_vis, lat_gim = build_streams(events)
    assert len(dets) > 0, "no detection events in log"
    assert len(truth) > 0, "no target_truth events in log (required for offline evaluation)"
    traj = TruthTraj(truth)
    gimbal = Gimbal(dt=DT, delay=lambda t: TAU_GIMBAL_NOMINAL, acc_max=ACC_MAX, rate_max=RATE_MAX)
    est = TargetIMM(dt=DT)
    delay_est = DelayPair() if controller_name == "Ours" else None
    if delay_est is not None:
        for v in lat_vis: delay_est.vision.add(v)
        for v in lat_gim: delay_est.gimbal.add(v)
    ctrl = build_controller(controller_name, est, delay_est, lead=True, tighten=True)
    ctrl.reset()
    fs = FireState(tau_fire=TAU_FIRE, cooldown=0.2, ammo=300)
    tau_v_used = TAU_VISION_NOMINAL if delay_est is None else delay_est.vision_mean()
    di = 0
    log = []
    steps = int(T / DT)
    for k in range(steps):
        t = k * DT
        # feed all detections whose measurement time is at/before t - tau_v_used
        while di < len(dets) and dets[di][0] <= t - tau_v_used:
            z = dets[di][1]
            if delay_est is not None:
                # online: update with the *observed* vision latency sample
                delay_est.vision.add(max(1e-3, t - dets[di][0]))
                tau_v_used = delay_est.vision_mean()
            est.update(z, t, max(0.0, dets[di][0]))
            di += 1
        gun_pre = gimbal.pointing()
        u, fire = ctrl.step(t, gimbal, est, fs)
        gimbal.step(t, u)
        gun = gimbal.pointing()
        true_azel = az_el(traj.position(t), GIMBAL_POS)
        shot = (t, gun_pre.copy()) if fire else None
        log.append({"t": t, "gun_dir": gun, "target_azel_true": true_azel, "shot": shot})
    m = run_metrics(log, traj, GIMBAL_POS, TAU_FIRE,
                    lambda t: np.linalg.norm(traj.position(t) - np.asarray(GIMBAL_POS)) / V_BULLET)
    m["controller"] = controller_name
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--controller", choices=["B0", "B1", "Ours"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    events = load_log(a.log)
    ctrls = ["B0", "B1", "Ours"] if a.all else [a.controller]
    for c in ctrls:
        m = replay(events, c, seed=a.seed)
        print(f"{c:>4}: hit_rate={m['hit_rate']:.3f} shots={m['shots']} "
              f"err_rmse={m['err_rmse']*1e3:.1f} mrad")

if __name__ == "__main__":
    main()
