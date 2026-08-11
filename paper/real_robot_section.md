# V. Real-Robot Experiments (Protocol; data pending hardware)

**Status**: protocol finalized; hardware bring-up in progress (P3). This section will report:

- **Platform**: custom RoboMaster infantry robot -- omnidirectional chassis, two-axis gimbal, industrial camera, onboard compute.
- **Ground truth**: referee-system hit detection; gimbal encoders for angular error.
- **Calibration**: camera intrinsics/extrinsics, PnP, ballistic model, gimbal step-response, hit tolerance.
- **Latency profile**: per-segment measurement per the protocol in `tools/delay_profiler/` (>=200 samples/segment), producing `latency_profile.yaml` that is injected into the simulation for fidelity checks.
- **Controlled comparison**: B0 / B1 / Ours, 4 motion classes (line/circle/S/accelerating), 300 shots x 3 rounds per condition, randomized round order; pre-registered primary metric: hit rate; threshold: >=5 pp improvement with p<0.05 (paired).
- **Failure conditions**: latency measurement below 1 ms precision required; otherwise simulation+hardware-in-the-loop fallback.

Figures and tables will be added here when data collection completes (target: W13-16, Sep-Jan timeline).
