# V. Real-Robot Experiments (Pre-registered Protocol)

**Status**: protocol v1.1 finalized (see `project/experiment_protocol.md`); hardware bring-up and data collection are scheduled after robot hardware becomes available (P3/P4). This section specifies the pre-registered protocol and will report results:

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
