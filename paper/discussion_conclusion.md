# VI. Discussion and Limitations

## A. Main findings

The simulation study shows a consistent and large improvement of the proposed delay-aware MPC over the community-standard baseline B0 on all four motion classes and all three latency profiles (28--67 pp, $p<0.001$). Against the delay-unaware MPC B1, the improvement is significant on line, circle, and accelerating motion, and the largest margins appear exactly when latency drifts over time (+29--59 pp on line/circle/accel under drift), which is the regime that motivated online latency estimation. The ablations attribute the gain primarily to the input-delay model (A1) and the lead prediction (A2); delay-uncertainty tightening (A6) provides a small but consistent gain under drift; the IMM vs. CV estimator choice (A4) has little effect in these scenarios.

## B. Honest limitations

1. **Sinusoidal motion vs. B1**: on the S trajectory, our method is not significantly better than B1 ($p>0.05$). We attribute this to the CT model inside IMM being less suited to sinusoidal lateral motion, and to B1 already capturing most of the MPC benefit on this class. A vehicle-rotation motion model (TJURM model two [R2]) is planned as future work.
2. **IMM benefit is scenario-dependent**: the CT model helps when the target turns persistently, but in our benchmark the CV estimator performed similarly (A4). Real opponents will exhibit mode switches, where IMM is expected to matter more.
3. **Simulation fidelity**: perception noise is idealized (3 cm), detections are never lost, and the gimbal model is linear with simple limits. Real perception noise, missed frames, and nonlinear actuator effects will be characterized in Section V.
4. **Numbers from literature**: the quantitative improvements cited from [R7] (37.6% LOS accuracy; 66.7% vs 41.6% within-1-mrad probability) and [R8] (42.9% response ratio; 58.3% tracking-precision improvement in the abstract) were re-verified against publisher metadata/abstracts on 2026-08-11; they remain simulation/abstract-level results from electro-optical turret platforms, so we cite them as context rather than as our claims.
5. **Novelty scope**: open-source MPC auto-aim exists [R3] and delay-compensated visual tracking is an established field [R5][R6]. Our contribution is the combination of explicit time-varying delay modeling, online estimation, controlled ablation, and an open benchmark on the RoboMaster platform -- not the first use of MPC for gimbal tracking per se.

## C. Model-set selection robustness check (supplementary)

We additionally implemented a three-model IMM (CV + CT + constant-acceleration CA) as a robustness check. It improved the S-trajectory hit rate under drift (0.111 -> 0.146, still not significant vs B1, p=0.114) but degraded accelerating-drift performance by about 20 pp, because the CA model extrapolates acceleration during the deceleration phase. The primary configuration therefore uses the two-model IMM (CV + CT); adaptive model-set selection is left as future work. Per-seed data for both configurations are released.

## D. Future work

- Vehicle-rotation (armor-around-center) motion model in the IMM.
- Robust MPC with constraint tightening based on $\Delta$ (tube/robust formulation) instead of the firing-margin heuristic.
- Embedded C++/OSQP solver and deployment on the custom infantry robot.
- Real-robot experiments per Section V (referee-system hit detection, pre-registered 300 shots $\times$ 3 rounds per condition).


---

# VII. Conclusion

We presented a delay-aware predictive control framework for moving-target tracking on RoboMaster-style gimbals, with explicit online estimation of the multi-segment vision/actuation latency chain, an IMM estimator with out-of-sequence measurement handling, an input-delay-augmented MPC solved by a real-time ADMM QP, and a delay-uncertainty-aware firing decision. On a pre-registered simulation benchmark, the proposed controller improved hit rate over the community-standard $Kt+B$+PID baseline by 28--67 percentage points ($p<0.001$) across all motion classes and latency profiles, and over a delay-unaware MPC on line, circle, and accelerating motion, with the largest gains under drifting latency. Ablations and a zero-delay upper bound substantiate the attribution of the gain to delay modeling and lead prediction. The solver satisfies the 20-ms control period with margin. Real-robot validation and an open benchmark are the next steps toward a complete, reproducible study.
