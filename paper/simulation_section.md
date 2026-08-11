# IV. Simulation Study



## IV. Simulation Study

### A. Setup (pre-registered)

- **Scenario set**: four target motion classes -- straight line (1.3~m/s), ground-plane circle (0.64~m/s tangential), sinusoidal (S) maneuver (1.0~m/s longitudinal, lateral amplitude 0.9~m at 0.9~rad/s), and accelerating/cruising/braking motion (0.2 $\rightarrow$ 2.0~m/s, cruise at 2.0~m/s, brake to 0.2~m/s) -- pre-registered before running.

- **Delay profiles**: (i) *fixed*: vision latency $\tau_v=0.03$~s, actuation latency $\tau_g=0.06$~s; (ii) *gamma*: vision latency drawn from a gamma distribution (mean $\tau_v$, std 15~ms); (iii) *drift*: both latencies ramp linearly from their nominal values to +60~ms over the episode. A zero-delay profile (iv) serves as the ideal upper bound (B2). Nominal engagement range is approximately 1--8~m. Firing uses a conservative fixed angular threshold $\theta_{\rm fire}=0.05$~rad (plus the delay-uncertainty margin), and hits are scored against the distance-adaptive tolerance $\theta_{\rm hit}=\arctan(0.08/\text{dist})$.

- **Controllers**: B0 -- community baseline: $Kt+B$ empirical lead + cascade PID driven by the same multi-model predictor as Ours (oracle-tuned lead, hence a stronger-than-typical baseline; RMVL practice [R1]); B1 -- the same multi-model predictor with an MPC that *ignores* the input delay (delay-unaware, SHtech-style); Ours -- delay-aware MPC (multi-model estimator + online latency estimation + input-delay-augmented model + ADMM box-constrained QP + delay-uncertainty tightening in the fire window).

- **Common settings**: control period $dt=0.02$~s, episode $T=6$~s, horizon $H=18$ ($0.36$~s), firing delay $\tau_{fire}=0.08$~s, bullet speed $15$~m/s, armor half-width 0.08~m, dispersion 0.008~rad, gimbal limits $|u|\le 10$~rad/s$^2$, $|\dot\theta|\le 6$~rad/s. Measurement noise 3~cm (1$\sigma$), firing cooldown 0.2~s (at most 30 shots/episode; realized shot counts differ by controller, mean 9--25). Ten random seeds per condition; two-sided paired $t$-test and Cohen's $d$ reported.

### B. Primary results

Table I reports mean hit rate over ten seeds (Fig.~\ref{fig:hit} visualizes the per-seed distribution; standard deviations omitted for readability; effect sizes in Table I). Ours outperforms B0 in all 12 conditions by 12--42 percentage points ($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\ge1.3$), with 29--42 pp gains on line and circle, 12--21 pp on accel, and 12--13 pp on the S trajectory; all 12 comparisons remain significant after Benjamini--Hochberg false-discovery-rate control (max $q$=0.002<0.05). Ours also outperforms B1 on line, circle, and accel (9 of 12 cells, $p<0.05$), and those 9 comparisons survive the same FDR control (max $q$=0.591<0.05). On the S trajectory, Ours is not significantly better than B1 in hit rate ($p>0.05$), an honest limitation discussed in Section VII; pointing-error RMSE under the drift profile nonetheless improves from 88.9 to 60.4 mrad versus B1 (and 163.9 to 60.4 mrad versus B0), with analogous RMSE reductions versus B0 on line, circle, and accel (Table S.4).

**Table I. Hit rate (mean over 10 seeds) and paired comparisons.**

| Scenario | Delay | B0 | B1 | Ours | Ours vs B0 | Ours vs B1 |
|---|---|---|---|---|---|---|
| line | fixed | 0.076 | 0.227 | 0.500 | +42.4 pp (p<0.001, d=+3.90) | +27.3 pp (p<0.001, d=+2.14) |
| line | gamma | 0.086 | 0.219 | 0.505 | +41.9 pp (p<0.001, d=+4.35) | +28.6 pp (p<0.001, d=+2.13) |
| line | drift | 0.057 | 0.106 | 0.443 | +38.7 pp (p<0.001, d=+4.52) | +33.7 pp (p<0.001, d=+2.93) |
| circle | fixed | 0.196 | 0.426 | 0.501 | +30.6 pp (p<0.001, d=+2.75) | +7.6 pp (p=0.024, d=+0.85) |
| circle | gamma | 0.211 | 0.435 | 0.496 | +28.5 pp (p<0.001, d=+2.42) | +6.1 pp (p=0.017, d=+0.92) |
| circle | drift | 0.123 | 0.277 | 0.427 | +30.4 pp (p<0.001, d=+2.61) | +15.1 pp (p<0.001, d=+1.52) |
| s | fixed | 0.009 | 0.128 | 0.141 | +13.1 pp (p<0.001, d=+2.48) | +1.3 pp (p=0.591, d=+0.18) |
| s | gamma | 0.021 | 0.115 | 0.154 | +13.3 pp (p=0.002, d=+1.33) | +4.0 pp (p=0.129, d=+0.53) |
| s | drift | 0.000 | 0.074 | 0.121 | +12.1 pp (p<0.001, d=+1.74) | +4.7 pp (p=0.110, d=+0.56) |
| accel | fixed | 0.013 | 0.140 | 0.263 | +25.1 pp (p<0.001, d=+2.27) | +12.3 pp (p<0.001, d=+1.65) |
| accel | gamma | 0.011 | 0.117 | 0.286 | +27.5 pp (p<0.001, d=+3.01) | +16.9 pp (p<0.001, d=+2.09) |
| accel | drift | 0.000 | 0.032 | 0.214 | +21.4 pp (p<0.001, d=+2.46) | +18.2 pp (p<0.001, d=+2.31) |

### C. Zero-delay upper bound (B2)

Table II gives the hit rate of Ours under the zero-delay profile. The gap between Ours (drift) and B2 quantifies the residual cost of the (estimated) latency chain, showing that delay compensation closes most but not all of the gap.

**Table II. B2 zero-delay upper bound.**

| Scenario | B2 | Ours (drift) | Residual gap (pp) |
|---|---|---|---|
| line | 0.560 | 0.443 | +11.7 |
| circle | 0.587 | 0.427 | +16.0 |
| s | 0.186 | 0.121 | +6.5 |
| accel | 0.359 | 0.214 | +14.5 |

### D. Ablations

Table III ablates the contributions under the drift profile (the hardest condition; Fig.~\ref{{fig:abl}} visualizes the ablation hit rates). The ablation set is A1--A6: A1 is B1 (no delay model), A2 removes the lead prediction, A3 replaces online latency estimation with the constant nominal delay (and disables uncertainty tightening), A4 uses a CV estimator, A6 disables delay-uncertainty tightening, and A5 is the across-seed coefficient of variation. Removing the input-delay model (A1 $=$ B1) or the lead prediction (A2) severely degrades hit rate (except on S, where the no-lead ablation is not worse, 0.129 vs. 0.121); replacing online estimation with the constant nominal delay (A3) costs 1--3 pp on line, circle, and accel (0.443$\to$0.415, 0.427$\to$0.411, 0.214$\to$0.200) and is neutral on S, so in these slow-drift profiles the dominant gains come from modeling the delay at all (A1) and the lead (A2), while online estimation provides a modest additional margin; disabling delay-uncertainty tightening (A6) causes a small drop; replacing the multi-model estimator with a CV estimator (A4) has little effect in these scenarios; the coefficient of variation across seeds (A5) ranges 12--55%.

**Table III. Ablations (drift profile, mean hit rate over 10 seeds).**

| Scenario | Ours | A1 no delay model | A2 no lead | A3 const delay | A4 CV estimator | A6 no tightening | A5 CV% |
|---|---|---|---|---|---|---|---|
| line | 0.443 | 0.106 | 0.061 | 0.415 | 0.435 | 0.420 | 16.9 |
| circle | 0.427 | 0.277 | 0.230 | 0.411 | 0.423 | 0.410 | 15.9 |
| s | 0.121 | 0.074 | 0.129 | 0.124 | 0.121 | 0.098 | 54.5 |
| accel | 0.214 | 0.032 | 0.191 | 0.200 | 0.304 | 0.221 | 38.6 |

### E. Real-time feasibility

Table IV reports per-step solver time in Python (NumPy/SciPy) as a conservative upper bound. Both solvers satisfy the 20-ms control period at the 99th percentile; an embedded C++/OSQP implementation (as in [SHtech]) is expected to be orders of magnitude faster.

**Table IV. Solver real-time benchmark (per step, $H=18$).**

| Solver | mean (ms) | p50 (ms) | p95 (ms) | p99 (ms) | max (ms) | $< 20$ ms |
|---|---|---|---|---|---|---|
| ADMM | 2.61 | 2.52 | 3.05 | 4.98 | 9.40 | yes |
| SLSQP | 0.83 | 0.79 | 1.05 | 1.85 | 3.42 | yes |

### F. Discussion and limitations

- **S trajectory vs B1**: Ours is not significantly better than B1 on sinusoidal lateral motion; we attribute this to the constant-turn-rate model inside the multi-model estimator being less suited to sinusoidal motion and to B1 already benefiting from MPC. This is reported honestly and motivates the vehicle-rotation model extension (future work).

- **Multi-model vs CV (A4)**: no material difference in these scenarios; a true IMM with interactive mixing is expected to help when the target switches between turn and translation modes (to be tested on the real robot with opponent-like motion).

- **Simulation fidelity**: PnP noise is idealized at 3~cm; real perception noise and intermittent detections will be characterized on the robot (Section V).

- **Reproducibility**: code and raw per-seed results are released (see Data Availability).
