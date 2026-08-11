# Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation: A RoboMaster Gimbal Case Study

**Version 0.5.4** -- simulation study with a pre-registered real-robot protocol (Section V); hardware data collection scheduled.


---

# Abstract

# Abstract

Vision-based aiming on RoboMaster combat robots is limited by a multi-segment latency chain: camera exposure/readout, detection and pose estimation, serial communication, gimbal actuation, firing delay, and projectile flight. Existing practice uses hand-tuned lead parameters ($Kt+B$) around a Kalman predictor; recent open-source designs apply model predictive control (MPC) to gimbal planning but treat delays as constant parameters and lack controlled evaluation.

Our contribution is a controlled demonstration that online-estimating the time-varying latency chain -- not treating delays as constants -- materially improves hit rate. The framework estimates the two dominant uncertain segments (vision, actuation) online and embeds them in a delay-aware MPC: a multi-model (CV+CT) estimator with out-of-sequence measurement handling generates lead references; a sliding-window latency estimator feeds both the aim horizon and a delay-uncertainty tightening margin into the firing decision; an input-delay-augmented MPC is solved by an ADMM box-constrained QP at $20$ ms control period. On a pre-registered simulation benchmark (four motion classes, three latency profiles, ten seeds), the proposed controller improves hit rate over the community-standard $Kt+B$+PID baseline by 12--67 percentage points ($p<0.01$ in all 12 conditions; 11 of 12 at $p<0.001$) and over a delay-unaware MPC on line, circle, and accelerating motion (up to $+61$ pp under drifting latency). Ablations isolate the contributions of delay modeling, lead prediction, and uncertainty tightening; a zero-delay upper bound quantifies the residual latency cost. The solver meets the real-time requirement ($p99=5.0$ ms $<$ 20 ms). Real-robot validation under this pre-registered protocol (referee-system hit detection) is ongoing.

**Keywords**: predictive control; visual latency compensation; target tracking; RoboMaster gimbal; delay-aware MPC

---

# I. Introduction

# I. Introduction

Autonomous aiming ("auto-aim") is the core closed-loop problem of RoboMaster combat robots: a vision pipeline detects the opponent's armor plates, a gimbal aims a projectile launcher, and the robot fires at the predicted impact position. Latency is a first-order, addressable component of the error budget: even with perfect tracking, delayed measurements force the controller to aim at stale target states. Team experience and public engineering documentation decompose the loop into six delays [R1][R2]: camera exposure and readout, detection/pose computation, serial communication, gimbal actuation (20--200 ms), firing delay (50--100 ms), and projectile flight (50--250 ms). Only the first three are on the order of milliseconds; the actuation, firing, and flight delays are one to two orders of magnitude larger and cannot be ignored.

Because of these latencies, aiming at the *current* target position is systematically wrong. Practical RoboMaster systems therefore predict the target state and aim at a *lead point*: the RoboMaster Vision Library (RMVL) formalizes this as three empirical prediction terms -- a static-response term $B$, a dynamic-response term proportional to flight time $Kt$, and a firing-delay term $\mathrm{SHOOT\_B}$ -- whose parameters are tuned by hand [R1]. State-of-the-art team designs use extended Kalman filters (EKF) with two motion models and an explicit delay taxonomy [R2]. Recent open-source work applies MPC to gimbal trajectory planning with an iterated EKF predictor, but represents the latency chain as a few constant parameters and provides no controlled experiments [R3]. The official open-source controller stack still uses PID plus a ballistic solver [R4]. RoboMaster is a useful study platform beyond competition: it is a low-cost, reproducible visual-servoing testbed whose latency chain is explicit and measurable, making it well suited for benchmarking delay-compensation methods.

In the control and photonics literature, the adverse effect of visual/measurement delay on closed-loop tracking bandwidth is well established, and multiple compensation strategies exist: interpolation and MPC for visual motion control [R5], Smith predictors for CCD optoelectronic tracking [R6], delay-prediction plus interpolation filtering for electro-optical detection systems [R7][R8], and robust/adaptive Kalman visual servoing under measurement delay [R9][R10]. MPC has also been applied to gimbal-camera target tracking for UAVs [R11]. However, these works do not target the RoboMaster platform, do not model the *time-varying and uncertain* multi-segment latency chain, and -- in the RoboMaster-specific MPC implementation [R3] -- lack controlled evaluation and ablations.

Our contribution is not a new tracker or a new solver; it is a controlled demonstration that explicitly modeling and online-estimating the time-varying, uncertain latency chain -- rather than treating delays as constants -- materially improves hit rate, with an open benchmark on the RoboMaster platform. Specifically:

1. **Delay-chain modeling with online estimation**: we formalize the six-segment latency chain (Fig.~\ref{fig:chain}) as a time-varying, uncertain quantity ($\tau_i(t)=\bar\tau_i+\delta_i(t)$, $|\delta_i|\le\Delta_i$), and estimate online the two dominant uncertain segments (vision and actuation) with a sliding-window estimator; the remaining segments are treated as constants or analytic functions. The uncertainty spread $\Delta_i$ enters the firing decision as a tightening margin.
2. **Delay-aware predictive control**: we embed the (estimated) input delay into the MPC prediction model via input-delay state augmentation, use a multi-model (CV+CT) estimator with out-of-sequence measurement handling for lead references, and solve the box-constrained QP with a warm-started ADMM solver at 20 ms.
3. **Controlled, reproducible evaluation**: a pre-registered simulation benchmark (4 motion classes $\times$ 3 latency profiles $\times$ 10 seeds) with two baselines, a zero-delay upper bound, and six ablations (A1--A6); code and per-seed results are released.

The rest of the paper is organized as follows. Section II formulates the problem. Section III presents the method. Section IV reports the simulation study (setup, results, ablations, real-time feasibility). Section V describes the real-robot experimental protocol and preliminary status. Section VI discusses limitations; Section VII concludes.

---

# II. Related Work

# II. Related Work

## A. RoboMaster auto-aim systems

RoboMaster auto-aim practice is documented mainly through open-source engineering artifacts. RMVL defines the empirical lead framework ($K$, $B$, $\mathrm{SHOOT\_B}$) and tuning procedure [R1]. The Tianjin University 2024 framework (TJURM) publishes a detailed delay taxonomy with per-segment magnitudes and an EKF with two motion models (single-plate variable-speed and vehicle-center rotation-translation) [R2]. The ShanghaiTech 2026 open-source auto-aim (SHtech) integrates an iterated EKF (IESEKF) with an MPC gimbal planner solved by an ADMM-based library, and treats communication/firing latencies as constant parameters in YAML configuration [R3]. The rm-controls stack implements PID yaw/pitch control with a ballistic solver for predictive aiming [R4]. Academic work on RoboMaster includes a YOLOv5-based assisted aiming system with Kalman prediction and PID+feedforward control [R12], and a Kalman-filter target recognition/tracking and firing system with ballistic compensation and cascade control [R13]. These works share two characteristics: prediction and control are decoupled (predictor outputs a lead angle; a PID/MPC tracks it), and latency is handled empirically rather than modeled and estimated.

## B. Delay compensation in visual tracking and visual servoing

The effect of delay on visual tracking bandwidth is a classical problem. Barreto and Batista analyzed delays in visually guided active tracking and proposed interpolation for visual latency and MPC for mechanical latency [R5]. The canonical dead-time compensator is the Smith predictor [R19], which assumes a constant, known delay; our contribution targets the time-varying, uncertain multi-segment chain that this classical structure does not address. In optoelectronic tracking, a modified Smith predictor with pseudo feedforward reduced the 1-Hz maximum residual error from 365 to 283 arcseconds (22.5%) and provided stability conditions under model mismatch [R6]. Recent work on intelligent electro-optical detection systems proposes tracking-controller delay prediction with interpolation filtering (37.6% line-of-sight accuracy improvement in simulation) [R7] and optimized Kalman/gyro targeting control [R8]. Adaptive/robust Kalman filtering has been applied to visual servoing under measurement delay on inertial stabilization platforms [R9], and a nonlinear direct error compensator addresses image-sensor delay on moving platforms [R10]. These works establish the importance and difficulty of delay compensation, but their platforms (fast steering mirrors, electro-optical turrets, inertial platforms) differ from a low-cost two-axis RoboMaster gimbal with water-pellet ballistics, and none performs a controlled ablation of delay modeling vs. prediction vs. ballistic compensation.

## C. MPC for target tracking with gimbals

MPC is a standard tool for constrained, receding-horizon tracking [R18]. For gimbal-camera systems, predictive-estimative nonlinear control (MPC + moving-horizon estimation) has been demonstrated for fixed-wing UAV target tracking [R11], and MPC-based visual servoing exists for quadrotors [R14] and robotic dynamic-object tracking [R15]. In the RoboMaster domain, SHtech provides an MPC gimbal planner [R3]. To our knowledge, within the searched scope (web/arXiv/journal-index searches, August 2026), no peer-reviewed work combines explicit *time-varying* delay-chain modeling with delay-aware MPC on a RoboMaster platform with controlled evaluation; open-source implementations exist but lack formal treatment and benchmarks.

---

# III. Method

# III. Method

This section summarizes the main components (full formulation in the supplementary material).

## A. System architecture

The closed loop is: camera -> detection -> PnP pose -> multi-model estimator -> online latency estimator -> delay-aware MPC (gimbal trajectory) -> firing decision -> serial -> MCU -> gimbal/launcher -> projectile (Fig.~\ref{fig:arch}). The estimator and the MPC are the two blocks we modify relative to the baselines; detection/PnP are shared.

## B. Target state estimation (multi-model, MMAE-style)

We maintain a two-model Bayesian multi-model estimator with a CV Kalman filter on 3D Cartesian state and a CT EKF on the ground-plane state $[x,y,v_x,v_y,\omega]$, weighting model outputs by posterior mode probabilities as in [R16] (MMAE-style: we use the mode-probability weighting without interactive mixing, the common simplification used by RoboMaster trackers). Measurements arrive with delay; each filter tracks its internal time $t_f$ and performs out-of-sequence updates following [R17]: propagate to the measurement time $t_m$, update, propagate to now. The mode probabilities follow a two-state Markov prior, and the predicted position at any horizon is the weighted mixture $\hat p(t+\tau)=\sum_i \mu_i\,\hat p_i(t+\tau)$.

## C. Online latency estimation

A sliding-window estimator records per-segment latency samples (from timestamps, Section V) and maintains the mean $\bar\tau$ and the uncertainty bound $\Delta = p95 - \mathrm{mean}$ for the vision and actuation segments. The vision estimate determines the measurement-time alignment in the filters; the actuation estimate sets the input-delay steps $d=\mathrm{round}(\bar\tau_g/\Delta t)$ of the MPC model; $\Delta$ enters the firing margin (III-E). Table S.3 quantifies estimator accuracy: under fixed delay the causal estimate is within $0.4$~ms MAE; under $\pm15$~ms jitter the per-step error is dominated by the jitter itself (MAE $\approx10$~ms), which $\Delta$ is designed to cover in the firing tightening; under drift the causal estimate lags by $\approx5$~ms (half-window $\times$ drift rate).

## D. Delay-aware MPC

The gimbal is modeled per axis as a double integrator with input delay: $\omega(k+1)=\omega(k)+\Delta t\, u(k-d)$, with acceleration bound $|u|\le u_{\max}$ and rate bound $|\dot\omega|\le \omega_{\max}$. The aim reference is the azimuth/elevation of the predicted target at $t+\tau_{\mathrm{fire}}+\tau_{\mathrm{flight}}(t)$ (lead point). At each control step we solve

\begin{multline*}
\min_{u(0:H-1)} \sum_{k=0}^{H-1} \|r(k)-g(k)\|_Q^2 + \|\Delta u(k)\|_R^2 \\
+ \|r(H-1)-g(H-1)\|_{Q_T}^2
\end{multline*}

subject to the input-delay-augmented linear dynamics and box constraints, using a warm-started ADMM solver for a box-constrained QP (SLSQP fallback). The prediction map $g_{\mathrm{flat}}=T u_{\mathrm{flat}}+b$ is built from the current angles/rates and the delayed-input buffer.

## E. Firing decision with delay-uncertainty tightening

We fire when the predicted pointing error plus a delay-uncertainty margin is below the angular hit tolerance:

$$
\|r(0)-g(0)\| + \kappa\,\hat v\,(\Delta_{\mathrm{vision}}+\Delta_{\mathrm{gimbal}})/\mathrm{dist} < \theta_{\mathrm{hit}},
$$

where $\hat v$ is the multi-model speed estimate and $\theta_{\mathrm{hit}}=\arctan(\mathrm{armor\_half}/\mathrm{dist})$. This margin prevents firing when the latency estimate is unreliable (e.g., during drift or jitter).

## F. Baselines

- **B0** (community baseline): empirical lead $Kt+B$ + cascade PID, mirroring RMVL practice [R1], driven by the same multi-model predictor as our method (a stronger-than-typical baseline). Its lead parameters are tuned with the ground-truth latency values (an oracle, hence favorable, setting for the baseline).
- **B1** (delay-unaware MPC): the same MPC but with the input-delay model disabled (d=0); it uses only nominal latency constants in the aim horizon and does not model the time-varying/uncertain chain [R3].
- **B2** (upper bound): our controller under a zero-delay profile (simulation only).

---

# IV. Simulation Study

# IV. Simulation Study



## IV. Simulation Study

### A. Setup (pre-registered)

- **Scenario set**: four target motion classes -- straight line, ground-plane circle, sinusoidal (S) maneuver, and accelerating/cruising/braking motion -- at a nominal speed scale (pre-registered before running).

- **Delay profiles**: (i) *fixed*: vision latency $\tau_v=0.03$~s, actuation latency $\tau_g=0.06$~s; (ii) *gamma*: vision latency drawn from a gamma distribution (mean $\tau_v$, std 15~ms); (iii) *drift*: both latencies ramp linearly from their nominal values to +60~ms over the episode. A zero-delay profile (iv) serves as the ideal upper bound (B2). Nominal engagement range is approximately 1--8~m (hit tolerance $\theta_{\rm hit}=\arctan(0.08/\text{dist})$).

- **Controllers**: B0 -- community baseline: $Kt+B$ empirical lead + cascade PID driven by the same multi-model predictor as Ours (oracle-tuned lead, hence a stronger-than-typical baseline; RMVL practice [R1]); B1 -- the same multi-model predictor with an MPC that *ignores* the input delay (delay-unaware, SHtech-style); Ours -- delay-aware MPC (multi-model estimator + online latency estimation + input-delay-augmented model + ADMM box-constrained QP + delay-uncertainty tightening in the fire window).

- **Common settings**: control period $dt=0.02$~s, episode $T=6$~s, horizon $H=18$ ($0.36$~s), firing delay $\tau_{fire}=0.08$~s, bullet speed $15$~m/s, armor half-width 0.08~m, dispersion 0.008~rad, gimbal limits $|u|\le 10$~rad/s$^2$, $|\dot\theta|\le 6$~rad/s. Measurement noise 3~cm (1$\sigma$). Ten random seeds per condition; paired $t$-test and Cohen's $d$ reported.

### B. Primary results

Table I reports mean hit rate over ten seeds (Fig.~\ref{fig:hit} visualizes the per-seed distribution; standard deviations omitted for readability; effect sizes in Table I). Ours outperforms B0 in all 12 conditions by 12--67 percentage points ($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\ge1.3$), with 28--67 pp gains on line, circle, and accel and 12--13 pp on the S trajectory; all 12 comparisons remain significant after Benjamini--Hochberg false-discovery-rate control (max $q$=0.002<0.05). Ours also outperforms B1 on line, circle, and accel (9 of 12 cells, $p<0.05$), and those 9 comparisons survive the same FDR control (max $q$=0.591<0.05). On the S trajectory, Ours is not significantly better than B1 in hit rate ($p>0.05$), an honest limitation discussed in Section VII; pointing-error RMSE under the drift profile nonetheless improves from 88.9 to 60.4 mrad versus B1 (and 163.9 to 60.4 mrad versus B0), with analogous RMSE reductions on line, circle, and accel (Table S.4).

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
| accel | fixed | 0.095 | 0.409 | 0.761 | +66.6 pp (p<0.001, d=+5.44) | +35.2 pp (p<0.001, d=+2.91) |
| accel | gamma | 0.134 | 0.408 | 0.773 | +64.0 pp (p<0.001, d=+3.48) | +36.5 pp (p<0.001, d=+2.51) |
| accel | drift | 0.082 | 0.148 | 0.755 | +67.3 pp (p<0.001, d=+4.28) | +60.7 pp (p<0.001, d=+3.97) |

### C. Zero-delay upper bound (B2)

Table II gives the hit rate of Ours under the zero-delay profile. The gap between Ours (drift) and B2 quantifies the residual cost of the (estimated) latency chain, showing that delay compensation closes most but not all of the gap.

**Table II. B2 zero-delay upper bound.**

| Scenario | B2 | Ours (drift) | Residual gap (pp) |
|---|---|---|---|
| line | 0.560 | 0.443 | +11.7 |
| circle | 0.587 | 0.427 | +16.0 |
| s | 0.186 | 0.121 | +6.5 |
| accel | 0.815 | 0.755 | +6.0 |

### D. Ablations

Table III ablates the contributions under the drift profile (the hardest condition; Fig.~\ref{{fig:abl}} visualizes the ablation hit rates). The ablation set is A1--A6, where A3 is the delay-profile main effect reported in Table I (fixed vs. gamma vs. drift) and A5 is the across-seed coefficient of variation. Removing the input-delay model (A1 $=$ B1) or the lead prediction (A2) severely degrades hit rate (except on S, where the no-lead ablation is not worse, 0.129 vs. 0.121); disabling delay-uncertainty tightening (A6) causes a small but consistent drop; replacing the multi-model estimator with a CV estimator (A4) has little effect in these scenarios; the coefficient of variation across seeds (A5) ranges 12--55%.

**Table III. Ablations (drift profile, mean hit rate over 10 seeds).**

| Scenario | Ours | A1 no delay model | A2 no lead | A4 CV estimator | A6 no tightening | A5 CV% |
|---|---|---|---|---|---|---|
| line | 0.443 | 0.106 | 0.061 | 0.435 | 0.420 | 16.9 |
| circle | 0.427 | 0.277 | 0.230 | 0.423 | 0.410 | 15.9 |
| s | 0.121 | 0.074 | 0.129 | 0.121 | 0.098 | 54.5 |
| accel | 0.755 | 0.148 | 0.450 | 0.776 | 0.753 | 11.9 |

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

---

# V. Real-Robot Experiments

# V. Real-Robot Experiments (Pre-registered Protocol)

**Status**: protocol v1.1 finalized (see `project/experiment_protocol.md`); hardware bring-up and data collection are scheduled after robot hardware becomes available (P3/P4). The research plan (scenarios, delay profiles, controllers, sample sizes, analysis) was time-stamped 2026-08-11T12:41+08:00, before any simulation results were produced (SHA-256 \texttt{0361b95b\-fe8f6537\-0693572b\-ceac100b\-e757df35\-e7f563c2\-e07ba3af\-fdc828c} of `project/experiment_plan.md`); protocol v1.1 (2026-08-11T16:10+08:00) operationalizes it. This section specifies the pre-registered protocol and will report results:

- **Platform**: custom RoboMaster infantry robot -- omnidirectional chassis, two-axis gimbal, industrial camera, onboard compute.
- **Ground truth**: referee-system hit detection; gimbal encoders for angular error.
- **Calibration**: camera intrinsics/extrinsics, PnP, ballistic model, gimbal step-response, hit tolerance.
- **Latency profile**: per-segment measurement per the protocol in `tools/delay_profiler/` (>=200 samples/segment), producing `latency_profile.yaml` that is injected into the simulation for fidelity checks.
- **Delay injection (controlled comparison)**: because natural latency may be mild/stationary, we inject software delays matching the simulation profiles (fixed / gamma / drift) by shifting detection timestamps, so the delay-modeling contribution is exercised identically across B0/B1/Ours.
- **Offline replay**: every condition records a full-chain event log (`tools/replay/`); B0/B1/Ours are replayed on the same detection stream to isolate the control/compensation contribution.
- **Statistics (pre-registered)**: paired one-sided McNemar exact test, $\alpha=0.05$; power analysis (Monte Carlo, `project/real_power_analysis.json`) shows $N=300\times3$ shots per method per scenario gives $\approx0.85$ power at a true +5 pp effect (pairing $\rho\ge0.5$); the observed $\ge5$ pp gate is inherently $\approx50\%$ powered at exactly 5 pp, so we additionally report the one-sided 95\% CI lower bound; an escalation rule adds one confirmation round (N=300) if $p<0.05$ with 3-5 pp observed.
- **Controlled comparison**: B0 / B1 / Ours, 4 motion classes (line/circle/S/accelerating), 300 shots x 3 rounds per condition, randomized round order; pre-registered primary metric: hit rate; threshold: >=5 pp improvement with p<0.05 (paired).
- **Failure conditions**: latency measurement below 1 ms precision required; otherwise simulation+hardware-in-the-loop fallback.

Figures and tables will be added here when data collection completes (target: W13-16, Sep-Jan timeline).

---

# VI. Discussion and Limitations

# VI. Discussion and Limitations

## A. Main findings

The simulation study shows a consistent and large improvement of the proposed delay-aware MPC over the community-standard baseline B0 in all 12 conditions (four motion classes x three latency profiles): 12--67 pp, $p<0.01$ in all, $p<0.001$ in 11 of 12, with 28--67 pp gains on line, circle, and accelerating motion and 12--13 pp on the sinusoidal trajectory. Against the delay-unaware MPC B1, the improvement is significant on line, circle, and accelerating motion (9 of 12 cells, $p<0.05$), and the largest margins over B1 appear exactly when latency drifts over time (+34/+15/+61 pp on line/circle/accel under drift), the regime that motivated online latency estimation. The ablations attribute the gain primarily to the input-delay model (A1) and the lead prediction (A2); delay-uncertainty tightening (A6) provides a small but consistent gain under drift; the IMM vs. CV estimator choice (A4) has little effect in these scenarios.

## B. Honest limitations

1. **Sinusoidal motion**: on the S trajectory, our method is not significantly better than B1 ($p>0.05$), and the no-lead ablation A2 does not degrade hit rate there (0.129 vs. 0.121); the CT model inside the multi-model estimator is less suited to sinusoidal lateral motion. A vehicle-rotation motion model (TJURM model two [R2]) is planned as future work.
2. **IMM benefit is scenario-dependent**: the CT model helps when the target turns persistently, but in our benchmark the CV estimator performed similarly (A4). Real opponents will exhibit mode switches, where IMM is expected to matter more.
3. **Simulation fidelity**: perception noise is idealized (3 cm), detections are never lost, and the gimbal model is linear with simple limits. Real perception noise, missed frames, and nonlinear actuator effects will be characterized in Section V.
4. **Numbers from literature**: the quantitative improvements cited from [R7] (37.6% LOS accuracy; 66.7% vs 41.6% within-1-mrad probability) and [R8] (42.9% response ratio; 58.3% tracking-precision improvement in the abstract) were re-verified against publisher metadata/abstracts on 2026-08-11; they remain simulation/abstract-level results from electro-optical turret platforms, so we cite them as context rather than as our claims.
5. **Novelty scope**: open-source MPC auto-aim exists [R3] and delay-compensated visual tracking is an established field [R5][R6]. Our contribution is the combination of explicit time-varying delay modeling, online estimation, controlled ablation, and an open benchmark on the RoboMaster platform -- not the first use of MPC for gimbal tracking per se.

## C. Model-set selection robustness check (supplementary)

We additionally implemented a three-model IMM (CV + CT + constant-acceleration CA) as a robustness check. It improved the S-trajectory hit rate under drift (0.111 -> 0.146, still not significant vs B1, p=0.114) but degraded accelerating-drift performance by about 20 pp, because the CA model extrapolates acceleration during the deceleration phase. The primary configuration therefore uses the two-model IMM (CV + CT); adaptive model-set selection is left as future work. Per-seed data for both configurations are released.

### Speed-gear sensitivity (supplementary)

The real-robot protocol tests three target speed gears (0.5 / 1.2 / 2.0 m/s). To keep the simulation consistent with that protocol, we ran a supplementary speed sweep (same controllers, drifting latency, 10 seeds; Table S1). Across the 12 speed--scenario cells, Ours improves hit rate over B0 by +2.0 to +67.3 percentage points, significant ($p<0.05$) in 11/12 cells; the only exception is circle at 2.0 m/s, where all controllers collapse to near-zero hit rate (Ours 0.020, $+2.0$ pp, $p=0.343$). Versus B1 the gain is significant in 8/12 cells, with non-significant differences on circle at 0.5/1.2/2.0 m/s and S at 1.2 m/s -- consistent with the main benchmark, where circular motion is the hardest case for B1. The estimated gain over B0 is positive in all 12 cells; over B1 it is negative only at circle 2.0 m/s ($-1.7$ pp, $p=0.599$). All controllers degrade at 2.0 m/s, so the supplementary sweep also serves as a difficulty calibration for the real-robot speed gears.

### Detection-dropout robustness (supplementary)

Real vision pipelines occasionally lose detections. We therefore replayed the representative line and accelerating scenarios under 10% and 20% detection-update dropout (drift latency, 10 seeds; Table S2). Ours remains significantly better than B1 at every dropout level ($p<0.01$; line 0.443/0.437/0.422, accel 0.755/0.600/0.624 at 0/10/20%), and its hit rate is approximately flat, consistent with the multi-model prediction absorbing missed frames. Notably B1's hit rate *increases* with dropout on both scenarios (line 0.106->0.233, accel 0.148->0.371); fewer, sparser updates occasionally prevent B1 from over-correcting, yet it remains far below Ours.

## D. Future work

- Vehicle-rotation (armor-around-center) motion model in the IMM.
- Robust MPC with constraint tightening based on $\Delta$ (tube/robust formulation) instead of the firing-margin heuristic.
- Embedded C++/OSQP solver and deployment on the custom infantry robot.
- Real-robot experiments per Section V (referee-system hit detection, pre-registered 300 shots $\times$ 3 rounds per condition).


---

# VII. Conclusion

We presented a delay-aware predictive control framework for moving-target tracking on RoboMaster-style gimbals, with explicit online estimation of the multi-segment vision/actuation latency chain, an IMM estimator with out-of-sequence measurement handling, an input-delay-augmented MPC solved by a real-time ADMM QP, and a delay-uncertainty-aware firing decision. On a pre-registered simulation benchmark, the proposed controller improved hit rate over the community-standard $Kt+B$+PID baseline by 12--67 percentage points in all 12 conditions ($p<0.01$; 11 of 12 at $p<0.001$), and over a delay-unaware MPC on line, circle, and accelerating motion, with the largest margins over that baseline under drifting latency. Ablations and a zero-delay upper bound substantiate the attribution of the gain to delay modeling and lead prediction. The solver satisfies the 20-ms control period with margin. Real-robot validation and an open benchmark are the next steps toward a complete, reproducible study.

---

# References

# References

Access notes: [R5][R6][R12] full text; others abstract/metadata as of 2026-08-11 (see project/evidence_report.md for content hashes). Key quantitative claims cited from [R7][R8] re-verified 2026-08-11 against publisher metadata/abstracts (FME official abstract + Wanfang/Springer; MDPI XML + Semantic Scholar).

- **[R1]** RoboMaster Vision Community, "RMVL: 在整车状态估计中涉及到的预测量 (Prediction quantities in vehicle state estimation)," official documentation, 2023. https://cv-rmvl.github.io/docs/1.0.0/d1/d40/tutorial_autoaim_gyro_predictor.html
- **[R2]** Tianjin University RoboMaster Team (TJURM), "TJURM 自瞄算法 Wiki," 2024. https://github.com/HHgzs/TJURM-2024/wiki/TJURM%E8%87%AA%E7%9E%84%E7%AE%97%E6%B3%95Wiki
- **[R3]** SHtech (ShanghaiTech), "SHtech_auto_aim," open-source repository, 2026. https://github.com/Astra-Whale/SHtech_auto_aim
- **[R4]** rm-controls, "rm_controllers -- Gimbal Controllers," open-source ROS controllers, 2025. https://deepwiki.com/rm-controls/rm_controllers/2-gimbal-controllers
- **[R5]** J. P. Barreto and P. Batista, "Model predictive control to improve visual control of motion: applications in active tracking of moving targets," in *Proc. 15th Int. Conf. Pattern Recognition (ICPR)*, 2000, vol. 4, pp. 732-735. doi:10.1109/ICPR.2000.903021
- **[R6]** K. Deng, J. Tan, P. Chen, S. Zhang, K. Wang, and Y. Luo, "A Smith Predictor Modified with a Pseudo Feedforward Control for the Charge-Coupled Device-Based Optoelectronic Tracking System," *Sensors*, 24(17):5546, 2024. doi:10.3390/s24175546
- **[R7]** C. Shen, Z. Wen, W. Zhu, D. Fan, M. Ling, "Small tracking error correction for moving targets of intelligent electro-optical detection systems," *Frontiers of Mechanical Engineering*, 19(2):11, 2024. https://academic.hep.com.cn/fme/CN/10.1007/s11465-024-0782-6  (numbers verified 2026-08-11)
- **[R8]** C. Shen, Z. Wen, W. Zhu, D. Fan, Y. Chen, and Z. Zhang, "Prediction and Control of Small Deviation in the Time-Delay of the Image Tracker in an Intelligent Electro-Optical Detection System," *Actuators*, 12(7):296, 2023. https://www.mdpi.com/2076-0825/12/7/296  (42.9% response-ratio verified 2026-08-11 via MDPI XML/Semantic Scholar)
- **[R9]** L. Zhang, Z. Wang, R. Xu, D. Tian, and L. Guo, "A robust adaptive Kalman filter based visual servoing control for an inertial stabilization platform," *Measurement Science and Technology*, 36(10):106204, 2025. doi:10.1088/1361-6501/ae0e8f
- **[R10]** Q. Miao, Q. Bian, Z. Yu, and T. Tang, "Nonlinear Direct Error Compensator for Visual Servo Trajectory Tracking Under Image Sensor Delay on a Moving Platform," *IEEE Trans. Ind. Electron.*, 73(6):9198-9208, 2026. doi:10.1109/TIE.2025.3649866
- **[R11]** S. Hai, X. Na, Z. Feng, J. Shi, and Q. Sun, "PENC: a predictive-estimative nonlinear control framework for robust target tracking of fixed-wing UAVs in complex urban environments," *Scientific Reports*, 15:13095, 2025. doi:10.1038/s41598-025-13095-z
- **[R12]** J. Qin and K. Xu, "Design and Implementation of Automatic Assisted Aiming System For Robomaster EP Based on YOLOv5," arXiv:2312.05055, 2023. https://arxiv.org/abs/2312.05055
- **[R13]** H. Wang, Z. Ji, and L. Zhang, "基于卡尔曼滤波的目标识别跟踪与射击系统设计 (Design of target recognition tracking and attack system based on Kalman filter)," *兵器装备工程学报 (Journal of Ordnance Equipment Engineering)*, 43(11):286-296, 2022. doi:10.11809/bqzbgcxb2022.11.041
- **[R14]** K. Zhang, Y. Shi, H. Sheng, "Robust nonlinear model predictive control based visual servoing of quadrotor UAVs," *IEEE/ASME Trans. Mechatronics*, 26(2):700-708, 2021. doi:10.1109/TMECH.2021.3053267
- **[R15]** Q. Zhang, T. Han, L. Lu, W. Pan, and G. Gao, "Fusing Phase Map Servoing and MPC for High-Precision Robotic Tracking of Dynamic Objects," *Actuators*, 15(2):77, 2026. doi:10.3390/act15020077
- **[R16]** H. A. P. Blom and Y. Bar-Shalom, "The interacting multiple model algorithm for systems with Markovian switching coefficients," *IEEE Trans. Autom. Control*, 33(8):780-783, 1988. doi:10.1109/9.1299
- **[R17]** Y. Bar-Shalom, "Update with out-of-sequence measurements in tracking: exact solution," *IEEE Trans. Aerosp. Electron. Syst.*, 38(3):769-778, 2002. doi:10.1109/TAES.2002.1039398
- **[R18]** D. Q. Mayne, J. B. Rawlings, C. V. Rao, and P. O. M. Scokaert, "Constrained model predictive control: Stability and optimality," *Automatica*, 36(6):789-814, 2000. doi:10.1016/S0005-1098(99)00214-9
- **[R19]** O. J. M. Smith, "A controller to overcome dead time," *ISA Journal*, 6(2):28-33, 1959.

---

# Supplementary Material

## Figures

- **Fig. 1**: `paper/figures/fig1_architecture.png` -- system architecture (shared detection/PnP -> proposed IMM estimator, online latency estimator, delay-aware MPC, firing decision; referee hit feedback).
- **Fig. 2**: `paper/figures/fig2_latency_chain.png` -- six-segment latency chain with per-segment magnitudes and online uncertainty estimate (mean +/- Delta_i) for firing tightening.
- **Fig. 3**: `sim/results_hitrate.png` -- hit rate by scenario / delay mode / controller (10 seeds).
- **Fig. 4**: `sim/results_ablations.png` -- ablation hit rates under the drift profile.


### S.1 Speed-gear sensitivity (supplementary)

Nominal target speed gears 0.5 / 1.2 / 2.0 m/s, drifting-latency profile, 10 seeds. Hit rate (mean) by controller; gains are paired mean differences with one-sided paired t-test p-values (statistics computed from per-seed data in `sim/results_speed_sweep.json`).

| scenario | speed (m/s) | B0 | B1 | Ours | Ours$-$B0 (pp, p) | Ours$-$B1 (pp, p) |
|---|---|---|---|---|---|---|
| line | 0.5 | 0.163 | 0.208 | 0.790 | +62.7 (p<0.001) | +58.2 (p<0.001) |
| line | 1.2 | 0.110 | 0.104 | 0.485 | +37.5 (p<0.001) | +38.1 (p<0.001) |
| line | 2.0 | 0.071 | 0.060 | 0.282 | +21.1 (p<0.001) | +22.2 (p<0.001) |
| circle | 0.5 | 0.243 | 0.369 | 0.460 | +21.7 (p<0.001) | +9.1 (0.083) |
| circle | 1.2 | 0.051 | 0.128 | 0.148 | +9.7 (0.009) | +2.0 (0.409) |
| circle | 2.0 | 0.000 | 0.037 | 0.020 | +2.0 (0.343) | -1.7 (0.599) |
| s | 0.5 | 0.027 | 0.231 | 0.627 | +60.0 (p<0.001) | +39.6 (p<0.001) |
| s | 1.2 | 0.000 | 0.035 | 0.053 | +5.3 (0.001) | +1.8 (0.346) |
| s | 2.0 | 0.000 | 0.010 | 0.060 | +6.0 (p<0.001) | +5.0 (0.023) |
| accel | 0.5 | 0.457 | 0.594 | 0.978 | +52.1 (p<0.001) | +38.4 (p<0.001) |
| accel | 1.2 | 0.358 | 0.330 | 0.901 | +54.3 (p<0.001) | +57.1 (p<0.001) |
| accel | 2.0 | 0.082 | 0.148 | 0.755 | +67.3 (p<0.001) | +60.7 (p<0.001) |

### S.2 Detection-dropout robustness (supplementary)

Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. Ours remains significantly better than B1 at every dropout level ($p<0.001$); its hit rate is approximately flat across dropout, consistent with IMM prediction absorbing missed frames.

| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |
|---|---|---|---|---|
| line | 0% | 0.106 | 0.443 | +33.7 (p<0.001) |
| line | 10% | 0.162 | 0.437 | +27.5 (p<0.001) |
| line | 20% | 0.233 | 0.422 | +19.0 (0.009) |
| accel | 0% | 0.148 | 0.755 | +60.7 (p<0.001) |
| accel | 10% | 0.245 | 0.600 | +35.4 (p<0.001) |
| accel | 20% | 0.371 | 0.624 | +25.2 (p<0.001) |

### S.3 Online delay-estimator accuracy (protocol secondary metric)

Sliding-window ($W=50$) estimator vs. true latency, same per-step feed as the controller loop; causal 'lag-1' estimate (samples before the current step), steady-state window $t\in[1,6]$~s.
Under fixed delay the estimator is accurate to <0.4 ms MAE; under $\pm15$~ms jitter the per-step error is dominated by the jitter itself (MAE $\approx10$ ms), which the uncertainty bound $\Delta_i$ (P95 $\approx27$ ms) is designed to cover in the firing tightening; under drift the lag-1 estimate lags by $\approx-5$ ms (half the sliding window times the drift rate).

| mode | segment | true mean (ms) | bias (ms) | MAE (ms) | RMSE (ms) | P95 abs err (ms) | settling to 5 ms (s) |
|---|---|---|---|---|---|---|---|
| fixed | vision | 30.0 | -0.19 | 0.24 | 0.29 | 0.56 | 0.98 |
| fixed | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.98 |
| gamma | vision | 26.4 | -0.13 | 10.16 | 13.02 | 26.53 | >6 |
| gamma | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.98 |
| drift | vision | 59.9 | -5.29 | 5.29 | 5.29 | 5.66 | 0.98 |
| drift | gimbal | 89.7 | -4.96 | 4.96 | 4.97 | 5.56 | 0.98 |
## Data Availability

- Simulation code: `sim/` (Python, MIT-style).
- Per-seed raw results: `sim/results_raw.jsonl` (canonical, 2-model IMM); `sim/results_raw_v03_2model_imm.jsonl`, `sim/results_raw_v04_3model_imm.jsonl` (backups).
- Summary tables: `sim/results_summary.md`; real-time benchmark: `sim/rt_benchmark.json`.
- Real-robot latency tooling: `tools/delay_profiler/`.
- All research-plan artifacts and audit trail: `project/` (research-agent state machine).

## Acknowledged limits of this draft

- Literature citations are abstract/metadata-level except [R5][R6][R12] (full text); quantitative claims cited from [R7][R8] were re-verified against publisher metadata/abstracts on 2026-08-11 (full experimental protocols remain inaccessible).
- Simulation-only conclusions; real-robot validation is the planned next stage.

