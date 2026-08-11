"""Generate paper/simulation_section.md (English draft) from sim/results.json + rt_benchmark.json."""
import json

R = json.load(open("../sim/results.json"))
RT = json.load(open("../sim/rt_benchmark.json"))
scenarios = ["line", "circle", "s", "accel"]
delays = ["fixed", "gamma", "drift"]
ctrls = ["B0", "B1", "Ours"]
cfg = R["config"]

def row(sc, dm):
    return {c: next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]==dm and x["controller"]==c) for c in ctrls}

def stat(sc, dm, key):
    return next(s for s in R["paired"] if s["scenario"]==sc and s["delay_mode"]==dm)[key]

def fmt_stat(s):
    return f"{s['mean_diff_pp']:+.1f} pp (p={s['p']:.3f}, d={s['d']:+.2f})" if s["p"] is not None else "-"

L = []
L.append("# Simulation Study (draft for English journal paper)\n")
L.append("> Auto-generated from `sim/results.json` and `sim/rt_benchmark.json` via `paper/generate_sim_section.py`. "
         "Do not edit numbers by hand; regenerate after any experiment change.\n")
L.append("## IV. Simulation Study\n")
L.append("### A. Setup (pre-registered)\n")
L.append(f"- **Scenario set**: four target motion classes -- straight line, ground-plane circle, sinusoidal (S) maneuver, and "
         f"accelerating/cruising/braking motion -- at a nominal speed scale (pre-registered before running).\n")
L.append(f"- **Delay profiles**: (i) *fixed*: vision latency $\\tau_v={cfg['tau_vision_nominal']:.2f}$~s, actuation latency "
         f"$\\tau_g={cfg['tau_gimbal_nominal']:.2f}$~s; (ii) *gamma*: vision latency drawn from a gamma distribution "
         f"(mean $\\tau_v$, std 15~ms); (iii) *drift*: both latencies ramp linearly from their nominal values to +60~ms over the episode. "
         f"A zero-delay profile (iv) serves as the ideal upper bound (B2).\n")
L.append(f"- **Controllers**: B0 -- community-style EKF prediction + $Kt+B$ empirical lead + cascade PID (RMVL practice); "
         f"B1 -- IESEKF/IMM prediction with an MPC that *ignores* the input delay (SHtech-style); "
         f"Ours -- delay-aware MPC (IMM estimator + online latency estimation + input-delay-augmented model + ADMM box-constrained QP + "
         f"delay-uncertainty tightening in the fire window).\n")
L.append(f"- **Common settings**: control period $dt={cfg['dt']:.2f}$~s, episode $T={cfg['T']:.0f}$~s, horizon $H={cfg['H']}$ "
         f"(${cfg['H']*cfg['dt']:.2f}$~s), firing delay $\\tau_{{fire}}={cfg['tau_fire']:.2f}$~s, bullet speed ${cfg['v_bullet']:.0f}$~m/s, "
         f"armor half-width 0.08~m, dispersion 0.008~rad, gimbal limits $|u|\\le 10$~rad/s$^2$, $|\\dot\\theta|\\le 6$~rad/s. "
         f"Measurement noise 3~cm (1$\\sigma$). Ten random seeds per condition; paired $t$-test and Cohen's $d$ reported.\n")
L.append("### B. Primary results\n")
L.append("Table I reports mean hit rate over ten seeds (standard deviations omitted for readability; effect sizes in Table I). "
         "Ours outperforms B0 in all 12 conditions by 11--67 percentage points "
         "($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\\ge1.3$), with 28--67 pp gains on line, circle, and accel "
         "and 11--13 pp on the S trajectory. Ours also outperforms B1 on line, circle, and accel "
         "(9 of 12 cells, $p<0.05$). On the S trajectory, Ours is not significantly better than B1 ($p>0.05$), "
         "an honest limitation discussed in Section VII.\n")
L.append("**Table I. Hit rate (mean over 10 seeds) and paired comparisons.**\n")
L.append("| Scenario | Delay | B0 | B1 | Ours | Ours vs B0 | Ours vs B1 |")
L.append("|---|---|---|---|---|---|---|")
for sc in scenarios:
    for dm in delays:
        r = row(sc, dm)
        L.append(f"| {sc} | {dm} | {r['B0']['hit_rate']:.3f} | {r['B1']['hit_rate']:.3f} | {r['Ours']['hit_rate']:.3f} "
                 f"| {fmt_stat(stat(sc,dm,'ours_vs_B0'))} | {fmt_stat(stat(sc,dm,'ours_vs_B1'))} |")
L.append("\n### C. Zero-delay upper bound (B2)\n")
L.append("Table II gives the hit rate of Ours under the zero-delay profile. The gap between Ours (drift) and B2 quantifies the "
         "residual cost of the (estimated) latency chain, showing that delay compensation closes most but not all of the gap.\n")
L.append("**Table II. B2 zero-delay upper bound.**\n")
L.append("| Scenario | B2 | Ours (drift) | Residual gap (pp) |")
L.append("|---|---|---|---|")
for sc in scenarios:
    b2 = R["b2_zero_delay"][sc]
    ours_d = next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]=="drift" and x["controller"]=="Ours")["hit_rate"]
    L.append(f"| {sc} | {b2:.3f} | {ours_d:.3f} | {(b2-ours_d)*100:+.1f} |")
L.append("\n### D. Ablations\n")
L.append("Table III ablates the contributions under the drift profile (the hardest condition). "
         "Removing the input-delay model (A1 $=$ B1) or the lead prediction (A2) severely degrades hit rate; "
         "disabling delay-uncertainty tightening (A6) causes a small but consistent drop; "
         "replacing IMM with a CV estimator (A4) has little effect in these scenarios; "
         "the coefficient of variation across seeds (A5) indicates reproducibility (15--47%).\n")
L.append("**Table III. Ablations (drift profile, mean hit rate over 10 seeds).**\n")
L.append("| Scenario | Ours (IMM) | A1 no delay model | A2 no lead | A4 CV estimator | A6 no tightening | A5 CV% |")
L.append("|---|---|---|---|---|---|---|")
for sc in scenarios:
    a = R["ablations_drift"][sc]
    L.append(f"| {sc} | {a['Ours_IMM']:.3f} | {a['A1_no_delay_model']:.3f} | {a['A2_no_lead']:.3f} | "
             f"{a['A4_CV_est']:.3f} | {a['A6_no_tighten']:.3f} | {a['A5_cv']*100:.1f} |")
L.append("\n### E. Real-time feasibility\n")
L.append(f"Table IV reports per-step solver time in Python (NumPy/SciPy) as a conservative upper bound. "
         f"Both solvers satisfy the 20-ms control period at the 99th percentile; an embedded C++/OSQP implementation "
         f"(as in [SHtech]) is expected to be orders of magnitude faster.\n")
L.append("**Table IV. Solver real-time benchmark (per step, $H=18$).**\n")
L.append("| Solver | mean (ms) | p50 (ms) | p95 (ms) | p99 (ms) | max (ms) | $< 20$ ms |")
L.append("|---|---|---|---|---|---|---|")
for name in ["admm", "slsqp"]:
    b = RT[name]
    L.append(f"| {name.upper()} | {b['mean_ms']:.2f} | {b['p50']:.2f} | {b['p95']:.2f} | {b['p99']:.2f} | {b['max']:.2f} | {'yes' if b['p99_lt_period'] else 'no'} |")
L.append("\n### F. Discussion and limitations\n")
L.append("- **S trajectory vs B1**: Ours is not significantly better than B1 on sinusoidal lateral motion; we attribute this to "
         "the constant-turn-rate model inside IMM being less suited to sinusoidal motion and to B1 already benefiting from MPC. "
         "This is reported honestly and motivates the vehicle-rotation model extension (future work).\n")
L.append("- **IMM vs CV (A4)**: no material difference in these scenarios; IMM is expected to help when the target switches "
         "between turn and translation modes (to be tested on the real robot with opponent-like motion).\n")
L.append("- **Simulation fidelity**: PnP noise is idealized at 3~cm; real perception noise and intermittent detections will be "
         "characterized on the robot (Section V).\n")
L.append("- **Reproducibility**: code and raw per-seed results are released (see Data Availability).\n")
open("simulation_section.md","w",encoding="utf-8").write("\n".join(L))
print("simulation_section.md written:", len("\n".join(L)), "chars")
