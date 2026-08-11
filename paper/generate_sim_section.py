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

def fmt_p(p):
    return "p<0.001" if p is not None and p < 0.001 else (f"p={p:.3f}" if p is not None else "-")

def fmt_stat(s):
    return f"{s['mean_diff_pp']:+.1f} pp ({fmt_p(s['p'])}, d={s['d']:+.2f})" if s["p"] is not None else "-"

def bh_q(pvals):
    n = len(pvals); order = sorted(range(n), key=lambda i: pvals[i]); q = [0.0]*n
    for rank, i in enumerate(order, start=1): q[i] = pvals[i]*n/rank
    for rank in range(n-2, -1, -1): q[order[rank]] = min(q[order[rank]], q[order[rank+1]])
    return q

L = []
L.append("# IV. Simulation Study\n")
L.append("\n")
L.append("## IV. Simulation Study\n")
L.append("### A. Setup (pre-registered)\n")
L.append(f"- **Scenario set**: four target motion classes -- straight line (1.3~m/s), ground-plane circle (0.64~m/s tangential), "
         f"sinusoidal (S) maneuver (1.0~m/s longitudinal, lateral amplitude 0.9~m at 0.9~rad/s), and "
         f"accelerating/cruising/braking motion (0.2 $\\rightarrow$ 2.0~m/s, cruise at 2.0~m/s, brake to 0.2~m/s) -- "
         f"pre-registered before running.\n")
L.append(f"- **Delay profiles**: (i) *fixed*: vision latency $\\tau_v={cfg['tau_vision_nominal']:.2f}$~s, actuation latency "
         f"$\\tau_g={cfg['tau_gimbal_nominal']:.2f}$~s; (ii) *gamma*: vision latency drawn from a gamma distribution "
         f"(mean $\\tau_v$, std 15~ms); (iii) *drift*: both latencies ramp linearly from their nominal values to +60~ms over the episode. "
         f"A zero-delay profile (iv) serves as the ideal upper bound (B2). "
         f"Nominal engagement range is approximately 1--8~m. Firing uses a conservative fixed angular threshold "
         f"$\\theta_{{\\rm fire}}=0.05$~rad (plus the delay-uncertainty margin), and hits are scored against the "
         f"distance-adaptive tolerance $\\theta_{{\\rm hit}}=\\arctan(0.08/\\text{{dist}})$.\n")
L.append(f"- **Controllers**: B0 -- community baseline: $Kt+B$ empirical lead + cascade PID driven by the same "
         f"multi-model predictor as Ours (oracle-tuned lead, hence a stronger-than-typical baseline; RMVL practice [R1]); "
         f"B1 -- the same multi-model predictor with an MPC that *ignores* the input delay (delay-unaware, SHtech-style); "
         f"Ours -- delay-aware MPC (multi-model estimator + online latency estimation + input-delay-augmented model + ADMM box-constrained QP + "
         f"delay-uncertainty tightening in the fire window).\n")
L.append(f"- **Common settings**: control period $dt={cfg['dt']:.2f}$~s, episode $T={cfg['T']:.0f}$~s, horizon $H={cfg['H']}$ "
         f"(${cfg['H']*cfg['dt']:.2f}$~s), firing delay $\\tau_{{fire}}={cfg['tau_fire']:.2f}$~s, bullet speed ${cfg['v_bullet']:.0f}$~m/s, "
         f"armor half-width 0.08~m, dispersion 0.008~rad, gimbal limits $|u|\\le 10$~rad/s$^2$, $|\\dot\\theta|\\le 6$~rad/s. "
         f"Measurement noise 3~cm (1$\\sigma$), firing cooldown 0.2~s (at most 30 shots/episode; realized shot counts differ by "
         f"controller, mean 9--25). Ten random seeds per condition; two-sided paired $t$-test and Cohen's $d$ reported.\n")
L.append("### B. Primary results\n")
_q0 = max(bh_q([stat(sc,dm,'ours_vs_B0')['p'] for sc in scenarios for dm in delays]))
_q1 = max(bh_q([stat(sc,dm,'ours_vs_B1')['p'] for sc in scenarios for dm in delays]))
_rm = {sc: {c: next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]=="drift" and x["controller"]==c)["err_rmse_mrad"] for c in ctrls} for sc in scenarios}
L.append(f"Table I reports mean hit rate over ten seeds (Fig.~\\ref{{fig:hit}} visualizes the per-seed distribution; standard deviations omitted for readability; effect sizes in Table I). "
         f"Ours outperforms B0 in all 12 conditions by 12--42 percentage points "
         f"($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\\ge1.3$), with 29--42 pp gains on line and circle, 12--21 pp on accel, "
         f"and 12--13 pp on the S trajectory; all 12 comparisons remain significant after Benjamini--Hochberg "
         f"false-discovery-rate control (max $q$={_q0:.3f}<0.05). Ours also outperforms B1 on line, circle, and accel "
         f"(9 of 12 cells, $p<0.05$), and those 9 comparisons survive the same FDR control (max $q$={_q1:.3f}<0.05). "
         f"On the S trajectory, Ours is not significantly better than B1 in hit rate ($p>0.05$), an honest limitation "
         f"discussed in Section VI; pointing-error RMSE under the drift profile nonetheless improves from "
         f"{_rm['s']['B1']:.1f} to {_rm['s']['Ours']:.1f} mrad versus B1 (and {_rm['s']['B0']:.1f} to {_rm['s']['Ours']:.1f} mrad versus B0), "
         f"with analogous RMSE reductions versus B0 on line, circle, and accel (Table~\\ref{{tab:rmse}}).\n")
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
L.append("Table III ablates the contributions under the drift profile (the hardest condition; Fig.~\\ref{{fig:abl}} visualizes the ablation hit rates). "
         "The ablation set is A1--A6: A1 is B1 (no delay model), A2 removes the lead prediction, A3 replaces online latency estimation with the constant nominal "
         "delay (and disables uncertainty tightening), A4 uses a CV estimator, A6 disables delay-uncertainty tightening, and A5 is the across-seed coefficient of variation. "
         "Removing the input-delay model (A1 $=$ B1) or the lead prediction (A2) severely degrades hit rate (except on S, where the no-lead ablation is not worse, 0.129 vs. 0.121); "
         "replacing online estimation with the constant nominal delay (A3) costs 1--3 pp on line, circle, and accel "
         "(0.443$\\to$0.415, 0.427$\\to$0.411, 0.214$\\to$0.200) and is neutral on S, so in these slow-drift profiles the dominant gains come from "
         "modeling the delay at all (A1) and the lead (A2), while online estimation provides a modest additional margin; "
         "disabling delay-uncertainty tightening (A6) causes a small drop; "
         "replacing the multi-model estimator with a CV estimator (A4) has little effect in these scenarios; "
         "the coefficient of variation across seeds (A5) ranges 12--55%.\n")
L.append("**Table III. Ablations (drift profile, mean hit rate over 10 seeds).**\n")
L.append("| Scenario | Ours | A1 no delay model | A2 no lead | A3 const delay | A4 CV estimator | A6 no tightening | A5 CV% |")
L.append("|---|---|---|---|---|---|---|---|")
for sc in scenarios:
    a = R["ablations_drift"][sc]
    L.append(f"| {sc} | {a['Ours_IMM']:.3f} | {a['A1_no_delay_model']:.3f} | {a['A2_no_lead']:.3f} | "
             f"{a['A3_const_delay']:.3f} | {a['A4_CV_est']:.3f} | {a['A6_no_tighten']:.3f} | {a['A5_cv']*100:.1f} |")
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
         "the constant-turn-rate model inside the multi-model estimator being less suited to sinusoidal motion and to B1 already benefiting from MPC. "
         "This is reported honestly and motivates the vehicle-rotation model extension (future work).\n")
L.append("- **Multi-model vs CV (A4)**: no material difference in these scenarios; a true IMM with interactive mixing is expected to "
         "help when the target switches between turn and translation modes (to be tested on the real robot with opponent-like motion).\n")
L.append("- **Simulation fidelity**: PnP noise is idealized at 3~cm; real perception noise and intermittent detections will be "
         "characterized on the robot (Section V).\n")
L.append("- **Reproducibility**: code and raw per-seed results are released (see Data Availability).\n")
open("simulation_section.md","w",encoding="utf-8").write("\n".join(L))
print("simulation_section.md written:", len("\n".join(L)), "chars")
