# Cover Letter（RA-L 模板；投 JINT/CEP 时替换期刊名与段落）

Dear Editor,

We are pleased to submit our manuscript, **"Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation: A RoboMaster Gimbal Case Study,"** for consideration as a Regular Paper in *IEEE Robotics and Automation Letters*.

**What the paper does.** Autonomous aiming on RoboMaster-style combat robots is a closed-loop problem whose performance is dominated by a multi-segment latency chain -- camera exposure/readout, detection and pose estimation, serial communication, gimbal actuation, firing delay, and projectile flight. Current practice compensates these latencies with hand-tuned empirical lead parameters around a Kalman predictor; recent open-source MPC designs treat delays as constants and lack controlled evaluation. We propose a delay-aware predictive control framework that: (1) models the latency chain as time-varying and uncertain and estimates it online with a sliding-window estimator; (2) embeds the estimated input delay into an MPC solved by a warm-started ADMM box-constrained QP at a 20-ms control period; and (3) uses an IMM (CV+CT) estimator with out-of-sequence measurement handling for lead references, plus a delay-uncertainty margin in the firing decision.

**Results.** On a pre-registered simulation benchmark (four motion classes x three latency profiles x ten seeds), the proposed controller improves hit rate over the community-standard $Kt+B$+PID baseline by 12--67 percentage points, significant in all 12 conditions ($p<0.01$; 11 of 12 at $p<0.001$; Cohen's $d\ge1.3$), with 28--67 pp gains on line, circular, and accelerating motion and 12--13 pp on the sinusoidal trajectory; it also outperforms a delay-unaware MPC on line, circular, and accelerating motion, with the largest margins under drifting latency (up to $+61$ pp). Six ablations and a zero-delay upper bound substantiate the attribution of the gain. Real-robot validation on a custom RoboMaster infantry robot with referee-system hit detection is in progress and will be included in the final version.

**Why this journal.** RA-L's scope covers robot control, visual servoing, and real-time systems, and its emphasis on concise, well-validated contributions matches our paper. The robotic-competition platform makes the work accessible and reproducible; we release simulation code, per-seed data, latency-profiling tooling, an offline replay harness, and an embedded-ready C++17 MPC solver.

**Honest positioning.** We do not claim the first use of MPC for gimbal tracking (see [5], [11]) nor the first delay-compensated visual tracking (see [5], [6]); our contribution is the explicit time-varying delay-chain modeling with online estimation, its integration into delay-aware MPC, and the first controlled ablation benchmark on the RoboMaster platform.

**Manuscript elements.** The submission includes the manuscript (6-page letter format), 4 figures (architecture, latency chain, main results, ablations), 4 main tables plus 3 supplementary robustness tables (speed-gear sensitivity, detection-dropout robustness, online delay-estimator accuracy), a supplementary video (to be added with real-robot footage), and open code/data.

**Supplementary robustness.** Beyond the main benchmark, we verified that the advantage persists across target speed gears (0.5--2.0 m/s) and under 0--20% detection dropout, and we quantify the online delay estimator's accuracy (MAE < 0.4 ms under fixed latency; jitter covered by the uncertainty margin).

We confirm that the manuscript is original, has not been published elsewhere, and is not under consideration by another journal. All authors approve the submission and declare no conflict of interest.

Thank you for your consideration.

Sincerely,
<Author Names>
<Affiliation>, <Email>
