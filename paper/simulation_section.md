# Simulation Study (draft for English journal paper)

> Auto-generated from `sim/results.json` and `sim/rt_benchmark.json` via `paper/generate_sim_section.py`. Do not edit numbers by hand; regenerate after any experiment change.

## IV. Simulation Study

### A. Setup (pre-registered)

- **Scenario set**: four target motion classes -- straight line, ground-plane circle, sinusoidal (S) maneuver, and accelerating/cruising/braking motion -- at a nominal speed scale (pre-registered before running).

- **Delay profiles**: (i) *fixed*: vision latency $\tau_v=0.03$~s, actuation latency $\tau_g=0.06$~s; (ii) *gamma*: vision latency drawn from a gamma distribution (mean $\tau_v$, std 15~ms); (iii) *drift*: both latencies ramp linearly from their nominal values to +60~ms over the episode. A zero-delay profile (iv) serves as the ideal upper bound (B2).

- **Controllers**: B0 -- community-style EKF prediction + $Kt+B$ empirical lead + cascade PID (RMVL practice); B1 -- IESEKF/IMM prediction with an MPC that *ignores* the input delay (SHtech-style); Ours -- delay-aware MPC (IMM estimator + online latency estimation + input-delay-augmented model + ADMM box-constrained QP + delay-uncertainty tightening in the fire window).

- **Common settings**: control period $dt=0.02$~s, episode $T=6$~s, horizon $H=18$ ($0.36$~s), firing delay $\tau_{fire}=0.08$~s, bullet speed $15$~m/s, armor half-width 0.08~m, dispersion 0.008~rad, gimbal limits $|u|\le 10$~rad/s$^2$, $|\dot\theta|\le 6$~rad/s. Measurement noise 3~cm (1$\sigma$). Ten random seeds per condition; paired $t$-test and Cohen's $d$ reported.

### B. Primary results

Table I reports mean hit rate over ten seeds (standard deviations omitted for readability; effect sizes in Table I). Ours outperforms B0 in all 12 conditions by 11--67 percentage points ($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\ge1.3$), with 28--67 pp gains on line, circle, and accel and 11--13 pp on the S trajectory. Ours also outperforms B1 on line, circle, and accel (9 of 12 cells, $p<0.05$). On the S trajectory, Ours is not significantly better than B1 ($p>0.05$), an honest limitation discussed in Section VII.

**Table I. Hit rate (mean over 10 seeds) and paired comparisons.**

| Scenario | Delay | B0 | B1 | Ours | Ours vs B0 | Ours vs B1 |
|---|---|---|---|---|---|---|
| line | fixed | 0.076 | 0.227 | 0.500 | +42.4 pp (p=0.000, d=+3.90) | +27.3 pp (p=0.000, d=+2.14) |
| line | gamma | 0.086 | 0.219 | 0.505 | +41.9 pp (p=0.000, d=+4.35) | +28.6 pp (p=0.000, d=+2.13) |
| line | drift | 0.057 | 0.106 | 0.450 | +39.3 pp (p=0.000, d=+4.72) | +34.4 pp (p=0.000, d=+2.48) |
| circle | fixed | 0.196 | 0.426 | 0.501 | +30.6 pp (p=0.000, d=+2.75) | +7.6 pp (p=0.024, d=+0.85) |
| circle | gamma | 0.211 | 0.435 | 0.496 | +28.5 pp (p=0.000, d=+2.42) | +6.1 pp (p=0.017, d=+0.92) |
| circle | drift | 0.123 | 0.277 | 0.468 | +34.4 pp (p=0.000, d=+2.54) | +19.1 pp (p=0.000, d=+1.74) |
| s | fixed | 0.009 | 0.128 | 0.141 | +13.1 pp (p=0.000, d=+2.48) | +1.3 pp (p=0.591, d=+0.18) |
| s | gamma | 0.021 | 0.115 | 0.154 | +13.3 pp (p=0.002, d=+1.33) | +4.0 pp (p=0.129, d=+0.53) |
| s | drift | 0.000 | 0.074 | 0.111 | +11.1 pp (p=0.000, d=+2.01) | +3.8 pp (p=0.138, d=+0.51) |
| accel | fixed | 0.095 | 0.409 | 0.761 | +66.6 pp (p=0.000, d=+5.44) | +35.2 pp (p=0.000, d=+2.91) |
| accel | gamma | 0.134 | 0.408 | 0.773 | +64.0 pp (p=0.000, d=+3.48) | +36.5 pp (p=0.000, d=+2.51) |
| accel | drift | 0.082 | 0.148 | 0.713 | +63.1 pp (p=0.000, d=+3.77) | +56.5 pp (p=0.000, d=+3.09) |

### C. Zero-delay upper bound (B2)

Table II gives the hit rate of Ours under the zero-delay profile. The gap between Ours (drift) and B2 quantifies the residual cost of the (estimated) latency chain, showing that delay compensation closes most but not all of the gap.

**Table II. B2 zero-delay upper bound.**

| Scenario | B2 | Ours (drift) | Residual gap (pp) |
|---|---|---|---|
| line | 0.560 | 0.450 | +11.0 |
| circle | 0.587 | 0.468 | +11.9 |
| s | 0.186 | 0.111 | +7.5 |
| accel | 0.815 | 0.713 | +10.2 |

### D. Ablations

Table III ablates the contributions under the drift profile (the hardest condition). Removing the input-delay model (A1 $=$ B1) or the lead prediction (A2) severely degrades hit rate; disabling delay-uncertainty tightening (A6) causes a small but consistent drop; replacing IMM with a CV estimator (A4) has little effect in these scenarios; the coefficient of variation across seeds (A5) indicates reproducibility (15--47%).

**Table III. Ablations (drift profile, mean hit rate over 10 seeds).**

| Scenario | Ours (IMM) | A1 no delay model | A2 no lead | A4 CV estimator | A6 no tightening | A5 CV% |
|---|---|---|---|---|---|---|
| line | 0.450 | 0.106 | 0.064 | 0.450 | 0.408 | 20.2 |
| circle | 0.468 | 0.277 | 0.239 | 0.460 | 0.439 | 17.9 |
| s | 0.111 | 0.074 | 0.118 | 0.111 | 0.104 | 47.2 |
| accel | 0.713 | 0.148 | 0.487 | 0.768 | 0.702 | 15.0 |

### E. Real-time feasibility

Table IV reports per-step solver time in Python (NumPy/SciPy) as a conservative upper bound. Both solvers satisfy the 20-ms control period at the 99th percentile; an embedded C++/OSQP implementation (as in [SHtech]) is expected to be orders of magnitude faster.

**Table IV. Solver real-time benchmark (per step, $H=18$).**

| Solver | mean (ms) | p50 (ms) | p95 (ms) | p99 (ms) | max (ms) | $< 20$ ms |
|---|---|---|---|---|---|---|
| ADMM | 3.14 | 3.02 | 4.00 | 4.88 | 6.34 | yes |
| SLSQP | 3.45 | 3.30 | 4.36 | 5.83 | 10.28 | yes |

### F. Discussion and limitations

- **S trajectory vs B1**: Ours is not significantly better than B1 on sinusoidal lateral motion; we attribute this to the constant-turn-rate model inside IMM being less suited to sinusoidal motion and to B1 already benefiting from MPC. This is reported honestly and motivates the vehicle-rotation model extension (future work).

- **IMM vs CV (A4)**: no material difference in these scenarios; IMM is expected to help when the target switches between turn and translation modes (to be tested on the real robot with opponent-like motion).

- **Simulation fidelity**: PnP noise is idealized at 3~cm; real perception noise and intermittent detections will be characterized on the robot (Section V).

- **Reproducibility**: code and raw per-seed results are released (see Data Availability).
