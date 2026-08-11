"""Phase-2/3 (v0.3) experiment runner.

Primary matrix : scenario x delay_mode(fixed/gamma/drift) x controller(B0/B1/Ours) x 10 seeds
Upper bound     : B2 (no delay) with Ours
Ablations       : A1=B1 (no delay model), A2 (no lead), A3 (delay-mode effect, in primary),
                  A4 (CV estimator), A5 (reproducibility CV%), A6 (no delay-uncertainty tightening)
Solver          : ADMM (box-constrained QP), warm-started.
"""
import json, time
import numpy as np
from scipy import stats

from trajectories import make_trajectory, az_el
from delay import make_delay
from gimbal import Gimbal
from estimator import TargetIMM, TargetKF
from delay_estimator import DelayEstimator
from controllers import LeadCompPID, PlainMPC, DelayAwareMPC, FireState
from metrics import run_metrics

DT = 0.02
T = 6.0
H = 18
TAU_FIRE = 0.08
V_BULLET = 15.0
GIMBAL_POS = (0.0, 0.0, 0.3)
ACC_MAX = 10.0
RATE_MAX = 6.0
SEEDS = list(range(10))
TAU_VISION_NOMINAL = 0.03
TAU_GIMBAL_NOMINAL = 0.06
RAW_FILE = "results_raw.jsonl"

class DelayPair:
    def __init__(self, vision=None, gimbal=None):
        self.vision = vision or DelayEstimator()
        self.gimbal = gimbal or DelayEstimator()
    def vision_mean(self): return self.vision.mean()
    def gimbal_mean(self): return self.gimbal.mean()

def delay_fns(mode):
    m = mode.lower()
    if m == "none":
        return (lambda t: 0.0, lambda t: 0.0)
    if m == "fixed":
        return (lambda t: TAU_VISION_NOMINAL, lambda t: TAU_GIMBAL_NOMINAL)
    if m == "gamma":
        vd = make_delay("gamma", TAU_VISION_NOMINAL, jitter=0.015, seed=7)
        return (lambda t: vd.sample(t), lambda t: TAU_GIMBAL_NOMINAL)
    if m == "drift":
        return (lambda t: TAU_VISION_NOMINAL + 0.06*(t/T),
                lambda t: TAU_GIMBAL_NOMINAL + 0.06*(t/T))
    raise ValueError(mode)

def build_controller(name, est, delay_est, lead=True, tighten=True):
    tf = lambda t: float(np.linalg.norm(est.predict(0.0))) / V_BULLET
    if name == "B0":
        return LeadCompPID(dt=DT, tau_fire=TAU_FIRE, tau_flight_fn=tf,
                           gimbal_pos=GIMBAL_POS, B=TAU_GIMBAL_NOMINAL)
    if name == "B1":
        return PlainMPC(dt=DT, H=H, tau_fire=TAU_FIRE, tau_flight_fn=tf,
                        gimbal_pos=GIMBAL_POS, acc_max=ACC_MAX, rate_max=RATE_MAX,
                        d_steps=int(round(TAU_GIMBAL_NOMINAL/DT)))
    if name == "Ours":
        return DelayAwareMPC(dt=DT, H=H, tau_fire=TAU_FIRE, tau_flight_fn=tf,
                             gimbal_pos=GIMBAL_POS, acc_max=ACC_MAX, rate_max=RATE_MAX,
                             d_steps=int(round(TAU_GIMBAL_NOMINAL/DT)), delay_est=delay_est,
                             lead=lead, tighten=tighten)
    if name == "A3":
        # ablation: delay-aware MPC with the constant NOMINAL delay (d_steps),
        # i.e. no online latency estimation and no uncertainty tightening
        return DelayAwareMPC(dt=DT, H=H, tau_fire=TAU_FIRE, tau_flight_fn=tf,
                             gimbal_pos=GIMBAL_POS, acc_max=ACC_MAX, rate_max=RATE_MAX,
                             d_steps=int(round(TAU_GIMBAL_NOMINAL/DT)), delay_est=None,
                             lead=lead, tighten=False)
    raise ValueError(name)

def run_once(scenario, delay_mode, controller_name, seed, estimator_type="IMM", lead=True, tighten=True, scale=1.0, dropout=0.0):
    """dropout: probability of dropping a detection update (missed-frame robustness).
    Default 0.0 keeps the canonical pipeline bit-identical."""
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    traj = make_trajectory(scenario, scale=scale)
    vfn, gfn = delay_fns(delay_mode)
    gimbal = Gimbal(dt=DT, delay=gfn, acc_max=ACC_MAX, rate_max=RATE_MAX)
    est = TargetIMM(dt=DT) if estimator_type == "IMM" else TargetKF(dt=DT)
    delay_est = DelayPair() if controller_name == "Ours" else None
    ctrl = build_controller(controller_name, est, delay_est, lead=lead, tighten=tighten)
    ctrl.reset()
    fs = FireState(tau_fire=TAU_FIRE, cooldown=0.2, ammo=300)

    log = []
    steps = int(T / DT)
    for k in range(steps):
        t = k * DT
        tau_v_true = vfn(t)
        if delay_est is not None:
            delay_est.vision.add(tau_v_true + rng.normal(0.0, 0.002))
            tau_v_used = delay_est.vision_mean()
        else:
            tau_v_used = TAU_VISION_NOMINAL if delay_mode != "none" else 0.0
        t_meas = max(0.0, t - tau_v_used)
        if dropout > 0.0 and rng.random() < dropout:
            continue  # detection lost: skip measurement update (estimator propagates)
        z = traj.position(max(0.0, t - tau_v_true)) + rng.normal(0.0, 0.03, 3)
        est.update(z, t, t_meas)
        if delay_est is not None:
            # causal: only samples completed before the current step are observable
            delay_est.gimbal.add(gfn(max(0.0, t - DT)) + rng.normal(0.0, 0.003))
        gun_pre = gimbal.pointing()
        u, fire = ctrl.step(t, gimbal, est, fs)
        gimbal.step(t, u)
        gun = gimbal.pointing()
        true_azel = az_el(traj.position(t), GIMBAL_POS)
        shot = (t, gun_pre.copy()) if fire else None
        log.append({"t": t, "gun_dir": gun, "target_azel_true": true_azel, "shot": shot})
    m = run_metrics(log, traj, GIMBAL_POS, TAU_FIRE,
                    lambda t: np.linalg.norm(traj.position(t) - np.asarray(GIMBAL_POS)) / V_BULLET)
    m.update({"controller": controller_name, "scenario": scenario, "delay_mode": delay_mode,
              "seed": seed, "estimator": estimator_type, "lead": lead, "tighten": tighten,
              "scale": float(scale), "dropout": float(dropout)})
    return m

def paired(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = a - b
    mean = d.mean(); sd = d.std(ddof=1)
    if len(a) < 2 or sd == 0:
        return {"mean_diff_pp": float(mean*100), "p": None, "d": None}
    t, p = stats.ttest_rel(a, b)
    return {"mean_diff_pp": float(mean*100), "p": float(p), "d": float(mean/sd)}

def _key(r):
    return (r["scenario"], r["delay_mode"], r["controller"], r["seed"], r["estimator"], r["lead"], r.get("tighten", True))

def _load_raw():
    out = {}
    try:
        with open(RAW_FILE, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                out[_key(r)] = r
    except FileNotFoundError:
        pass
    return out

def aggregate(results):
    rows = []
    for sc in ["line", "circle", "s", "accel"]:
        for dm in ["fixed", "gamma", "drift"]:
            for c in ["B0", "B1", "Ours"]:
                filt = (lambda r: r["estimator"]=="IMM" and r["lead"] and r.get("tighten", True)) if c == "Ours" else (lambda r: True)
                sub = [r for r in results if r["scenario"]==sc and r["delay_mode"]==dm and r["controller"]==c and filt(r)]
                if not sub: continue
                rows.append({
                    "scenario": sc, "delay_mode": dm, "controller": c,
                    "hit_rate": float(np.mean([r["hit_rate"] for r in sub])),
                    "hit_std": float(np.std([r["hit_rate"] for r in sub])),
                    "shots": int(np.mean([r["shots"] for r in sub])),
                    "err_rmse_mrad": float(np.mean([r["err_rmse"] for r in sub])*1e3),
                })
    return rows

def main():
    t0 = time.time()
    raw = _load_raw()
    scenarios = ["line", "circle", "s", "accel"]
    delay_modes = ["fixed", "gamma", "drift"]
    controllers = ["B0", "B1", "Ours"]
    todo = []
    for sc in scenarios:
        for dm in delay_modes:
            for c in controllers:
                for sd in SEEDS:
                    todo.append((sc, dm, c, sd, "IMM", True, True))
    for sc in scenarios:
        for sd in SEEDS:
            todo.append((sc, "none", "Ours", sd, "IMM", True, True))          # B2
    for sc in scenarios:
        for sd in SEEDS:
            todo.append((sc, "drift", "Ours", sd, "IMM", False, True))        # A2 no lead
            todo.append((sc, "drift", "Ours", sd, "CV", True, True))          # A4 CV estimator
            todo.append((sc, "drift", "Ours", sd, "IMM", True, False))        # A6 no tightening
            todo.append((sc, "drift", "A3", sd, "IMM", True, True))           # A3 constant-delay MPC
    missing = [t for t in todo if t not in raw]
    with open(RAW_FILE, "a", encoding="utf-8") as f:
        for i, (sc, dm, c, sd, est, lead, tighten) in enumerate(missing):
            r = run_once(sc, dm, c, sd, estimator_type=est, lead=lead, tighten=tighten)
            raw[_key(r)] = r
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if (i+1) % 60 == 0:
                print(f"[{time.time()-t0:.1f}s] {i+1}/{len(missing)} runs", flush=True)
    results = list(raw.values())
    print(f"[{time.time()-t0:.1f}s] runs done: {len(results)}", flush=True)

    rows = aggregate(results)
    stats_out = []
    for sc in scenarios:
        for dm in delay_modes:
            ours = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]==dm and r["controller"]=="Ours" and r["lead"] and r["estimator"]=="IMM" and r.get("tighten", True)]
            b0 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]==dm and r["controller"]=="B0"]
            b1 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]==dm and r["controller"]=="B1"]
            stats_out.append({"scenario": sc, "delay_mode": dm,
                              "ours_vs_B0": paired(ours, b0), "ours_vs_B1": paired(ours, b1)})
    b2 = [r for r in results if r["delay_mode"] == "none"]
    b2_mean = {sc: float(np.mean([r["hit_rate"] for r in b2 if r["scenario"]==sc])) for sc in scenarios}

    abl_rows = {}
    for sc in scenarios:
        a1 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="B1"]
        a2 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="Ours" and r["lead"]==False]
        a4 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="Ours" and r["estimator"]=="CV"]
        a6 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="Ours" and r.get("tighten", True)==False]
        a3 = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="A3"]
        ours_d = [r["hit_rate"] for r in results if r["scenario"]==sc and r["delay_mode"]=="drift" and r["controller"]=="Ours" and r["lead"] and r["estimator"]=="IMM" and r.get("tighten", True)]
        cv = float(np.std(ours_d) / (np.mean(ours_d) + 1e-9))
        abl_rows[sc] = {"Ours_IMM": float(np.mean(ours_d)), "A1_no_delay_model": float(np.mean(a1)),
                        "A2_no_lead": float(np.mean(a2)), "A3_const_delay": float(np.mean(a3)),
                        "A4_CV_est": float(np.mean(a4)),
                        "A6_no_tighten": float(np.mean(a6)), "A5_cv": cv}

    out = {"config": {"dt": DT, "T": T, "H": H, "tau_fire": TAU_FIRE,
                      "tau_gimbal_nominal": TAU_GIMBAL_NOMINAL, "tau_vision_nominal": TAU_VISION_NOMINAL,
                      "v_bullet": V_BULLET, "seeds": SEEDS, "estimator": "IMM(CV+CT)", "solver": "ADMM"},
           "rows": rows, "paired": stats_out, "b2_zero_delay": b2_mean,
           "ablations_drift": abl_rows, "wall_sec": time.time()-t0}
    with open("results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    md = ["# Phase-2/3 Simulation Results (v0.3, ADMM solver)", "",
          f"Config: dt={DT}s, T={T}s, H={H}, tau_fire={TAU_FIRE}s, tau_vision={TAU_VISION_NOMINAL}s, "
          f"tau_gimbal={TAU_GIMBAL_NOMINAL}s, estimator=IMM(CV+CT), solver=ADMM, seeds={len(SEEDS)}, wall={out['wall_sec']:.0f}s",
          "", "## 1. Primary matrix (hit_rate, mean over 10 seeds)", "",
          "| scenario | delay | B0 | B1 | Ours | ours_vs_B0 (pp, p, d) | ours_vs_B1 (pp, p, d) |", "|---|---|---|---|---|---|---|"]
    for sc in scenarios:
        for dm in delay_modes:
            row = {r["controller"]: r for r in rows if r["scenario"]==sc and r["delay_mode"]==dm}
            st = next(s for s in stats_out if s["scenario"]==sc and s["delay_mode"]==dm)
            def fmt(x):
                if x["p"] is None: return "-"
                return f"{x['mean_diff_pp']:+.1f}pp p={x['p']:.3f} d={x['d']:+.2f}"
            md.append(f"| {sc} | {dm} | {row['B0']['hit_rate']:.3f} | {row['B1']['hit_rate']:.3f} | {row['Ours']['hit_rate']:.3f} | {fmt(st['ours_vs_B0'])} | {fmt(st['ours_vs_B1'])} |")
    md += ["", "## 2. B2 zero-delay upper bound (Ours, hit_rate)", "", "| scenario | B2 |", "|---|---|"]
    for sc in scenarios:
        md.append(f"| {sc} | {b2_mean[sc]:.3f} |")
    md += ["", "## 3. Ablations (drift mode, hit_rate)", "",
           "| scenario | Ours(IMM) | A1 no-delay-model(B1) | A2 no-lead | A3 const-delay | A4 CV-est | A6 no-tighten | A5 CV% |", "|---|---|---|---|---|---|---|---|"]
    for sc in scenarios:
        a = abl_rows[sc]
        md.append(f"| {sc} | {a['Ours_IMM']:.3f} | {a['A1_no_delay_model']:.3f} | {a['A2_no_lead']:.3f} | {a['A3_const_delay']:.3f} | {a['A4_CV_est']:.3f} | {a['A6_no_tighten']:.3f} | {a['A5_cv']*100:.1f}% |")
    md += ["", "> v0.3 说明：Ours=时延感知 MPC(IMM+在线时延估计+ADMM 盒约束+时延不确定性约束收紧)；B1=无时延建模 MPC；B0=Kt+B+PID。",
           "> 出口准则：Ours 在 >=2 类轨迹显著优于 B0/B1 且 P99 求解耗时 < 控制周期。"]
    open("results_summary.md", "w").write("\n".join(md))
    print("\n".join(md))

if __name__ == "__main__":
    main()
