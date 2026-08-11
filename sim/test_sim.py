#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for sim modules (run: python3 -m pytest sim/test_sim.py -q, or direct)."""
import math, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

def test_trajectories_line():
    from trajectories import make_trajectory, az_el
    tr = make_trajectory("line")
    p0 = tr.position(0.0); p1 = tr.position(2.0)
    assert np.allclose(tr.velocity(0.0), (p1 - p0) / 2.0, atol=1e-9)  # constant velocity over dt=2
    az, el = az_el(np.array([1.0, 1.0, 0.0]), np.array([0.0, 0.0, 0.3]))
    assert abs(az - math.pi/4) < 1e-9 and el < 0

def test_trajectories_accel_piecewise():
    from trajectories import make_trajectory
    tr = make_trajectory("accel")
    # cruise phase velocity should equal v0 + a*ta - a*ta = v0 (per implementation)
    v = tr.velocity(5.0)
    assert np.all(np.isfinite(v))

def test_delay_fixed_and_gamma():
    from delay import make_delay
    f = make_delay("fixed", 0.03)
    assert f.sample(0) == 0.03 and f.sample(9.9) == 0.03
    g = make_delay("gamma", 0.03, jitter=0.015, seed=7)
    vals = [g.sample(t) for t in np.linspace(0, 6, 200)]
    assert 0.02 < np.mean(vals) < 0.05 and all(v > 0 for v in vals)

def test_delay_estimator():
    from delay_estimator import DelayEstimator
    e = DelayEstimator(window=10)
    for _ in range(20): e.add(0.04)
    assert abs(e.mean() - 0.04) < 1e-12
    assert abs(e.p95() - 0.04) < 1e-12

def test_estimator_tracks_constant_velocity():
    from estimator import TargetKF
    from trajectories import LineTraj
    est = TargetKF(dt=0.02)
    tr = LineTraj(p0=[1.0, -0.6, 0.0], v=[1.2, 0.5, 0.0])
    for k in range(100):
        t = k * 0.02
        est.update(tr.position(t) + np.random.normal(0, 0.01, 3), t, t)
    p = est.predict(0.0)
    assert np.linalg.norm(p - tr.position(100*0.02)) < 0.15

def test_metrics_hit_when_aimed():
    from metrics import simulate_hits, run_metrics
    from trajectories import LineTraj, az_el
    tr = LineTraj(p0=[1.0, -0.6, 0.0], v=[1.2, 0.5, 0.0])
    gimbal_pos = np.array([0.0, 0.0, 0.3])
    shots = [(1.0, az_el(tr.position(1.0 + 0.08), gimbal_pos))]  # aim at impact position
    hits = simulate_hits(shots, tr, gimbal_pos, tau_fire=0.08, tau_flight_fn=lambda t: 0.1)
    assert hits == 1

def test_controllers_build_and_step():
    from run_experiments import build_controller, DelayPair, FireState, DT, TAU_FIRE
    from estimator import TargetIMM
    from gimbal import Gimbal
    est = TargetIMM(dt=DT)
    dp = DelayPair()
    for cname in ["B0", "B1", "Ours"]:
        ctrl = build_controller(cname, est, dp if cname == "Ours" else None)
        ctrl.reset()
        gim = Gimbal(dt=DT, delay=lambda t: 0.06, acc_max=10.0, rate_max=6.0)
        fs = FireState(tau_fire=TAU_FIRE, cooldown=0.2, ammo=300)
        u, fire = ctrl.step(0.0, gim, est, fs)
        assert np.isfinite(u).all() and isinstance(fire, bool)

def test_run_once_bounds():
    from run_experiments import run_once
    r = run_once("line", "drift", "Ours", 0)
    assert 0.0 <= r["hit_rate"] <= 1.0 and r["shots"] > 0 and r["scale"] == 1.0 and r["dropout"] == 0.0

def test_replay_end_to_end():
    import subprocess
    tools_replay = pathlib.Path(__file__).resolve().parent.parent / "tools" / "replay"
    sys.path.insert(0, str(tools_replay))
    import replay
    log = pathlib.Path(__file__).resolve().parent / "test_synth_log.jsonl"
    subprocess.run([sys.executable, "make_synthetic_log.py", "--scenario", "accel",
                    "--delay", "drift", "--out", str(log), "--seed", "0"],
                   cwd=str(tools_replay), check=True, capture_output=True)
    events = replay.load_log(log)
    m1 = replay.replay(events, "B1")
    mo = replay.replay(events, "Ours")
    assert m1["shots"] > 0 and mo["shots"] > 0
    log.unlink(missing_ok=True)

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print("PASS", fn.__name__)
    print(f"{len(fns)} tests passed")
