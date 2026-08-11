# VI. Discussion and Limitations

## A. Main findings

The simulation study shows a consistent and large improvement of the proposed delay-aware MPC over the community-standard baseline B0 in all 12 conditions (four motion classes x three latency profiles): 12--42 pp, $p<0.01$ in all, $p<0.001$ in 11 of 12, with 29--42 pp gains on line and circle, 12--21 pp on accelerating motion, and 12--13 pp on the sinusoidal trajectory. Against the delay-unaware MPC B1, the improvement is significant on line, circle, and accelerating motion (9 of 12 cells, $p<0.05$), and the largest margins over B1 appear exactly when latency drifts over time (+34/+15/+18 pp on line/circle/accel under drift), the regime that motivated online latency estimation. The ablations attribute the gain primarily to the input-delay model (A1) and the lead prediction (A2); replacing online latency estimation with the constant nominal delay (A3) costs only 1--3 pp on line, circle, and accel in these slow-drift profiles, so online estimation provides a modest but real margin (expected to matter more under larger or faster drift, which the real-robot delay injection matches); delay-uncertainty tightening (A6) provides a small drop when disabled; the IMM vs. CV estimator choice (A4) has little effect in these scenarios.

## B. Honest limitations

1. **Sinusoidal motion**: on the S trajectory, our method is not significantly better than B1 ($p>0.05$), and the no-lead ablation A2 does not degrade hit rate there (0.129 vs. 0.121); the CT model inside the multi-model estimator is less suited to sinusoidal lateral motion. A vehicle-rotation motion model (TJURM model two [R2]) is planned as future work.
2. **IMM benefit is scenario-dependent**: the CT model helps when the target turns persistently, but in our benchmark the CV estimator performed similarly (A4). Real opponents will exhibit mode switches, where IMM is expected to matter more.
3. **Simulation fidelity**: perception noise is idealized (3 cm), detections are never lost, and the gimbal model is linear with simple limits. Real perception noise, missed frames, and nonlinear actuator effects will be characterized in Section V.
4. **Numbers from literature**: the quantitative improvements cited from [R7] (37.6% LOS accuracy; 66.7% vs 41.6% within-1-mrad probability) and [R8] (42.9% response ratio; 58.3% tracking-precision improvement in the abstract) were re-verified against publisher metadata/abstracts on 2026-08-11; they remain simulation/abstract-level results from electro-optical turret platforms, so we cite them as context rather than as our claims.
5. **Novelty scope**: open-source MPC auto-aim exists [R3] and delay-compensated visual tracking is an established field [R5][R6]. Our contribution is the combination of explicit time-varying delay modeling, online estimation, controlled ablation, and an open benchmark on the RoboMaster platform -- not the first use of MPC for gimbal tracking per se.

## C. Model-set selection robustness check (supplementary)

We additionally implemented a three-model IMM (CV + CT + constant-acceleration CA) as a robustness check. It improved the S-trajectory hit rate under drift (0.111 -> 0.146, still not significant vs B1, p=0.114) but degraded accelerating-drift performance by about 20 pp, because the CA model extrapolates acceleration during the deceleration phase. The primary configuration therefore uses the two-model IMM (CV + CT); adaptive model-set selection is left as future work. Per-seed data for both configurations are released.

### Speed-gear sensitivity (supplementary)

The real-robot protocol tests three target speed gears (0.5 / 1.2 / 2.0 m/s). To keep the simulation consistent with that protocol, we ran a supplementary speed sweep (same controllers, drifting latency, 10 seeds; Table S1). Across the 12 speed--scenario cells, Ours improves hit rate over B0 by +2.0 to +62.7 percentage points, significant ($p<0.05$) in 11/12 cells; the only exception is circle at 2.0 m/s, where all controllers collapse to near-zero hit rate (Ours 0.020, $+2.0$ pp, $p=0.343$). Versus B1 the gain is significant in 8/12 cells, with non-significant differences on circle at 0.5/1.2/2.0 m/s and S at 1.2 m/s -- consistent with the main benchmark, where circular motion is the hardest case for B1. The estimated gain over B0 is positive in all 12 cells; over B1 it is negative only at circle 2.0 m/s ($-1.7$ pp, $p=0.599$). All controllers degrade at 2.0 m/s, so the supplementary sweep also serves as a difficulty calibration for the real-robot speed gears.

### Detection-dropout robustness (supplementary)

Real vision pipelines occasionally lose detections. We therefore replayed the representative line and accelerating scenarios under 10% and 20% detection-update dropout (drift latency, 10 seeds; Table S2). On line, Ours remains significantly better than B1 at every dropout level (0.443/0.437/0.422 vs. 0.106/0.162/0.233, $p<0.01$), and its hit rate is approximately flat, consistent with the multi-model prediction absorbing missed frames. On accelerating motion the gain is significant at 0% and 10% dropout (0.214 vs. 0.032 and 0.158 vs. 0.054, $p<0.05$) but narrows to $+0.7$ pp at 20% ($p=0.85$), so robustness to missed detections degrades on the fastest trajectory. Notably B1's hit rate increases with dropout on both scenarios (line 0.106$\to$0.233, accel 0.032$\to$0.121); fewer, sparser updates occasionally prevent B1 from over-correcting, yet it remains below Ours.

## D. Future work

- Vehicle-rotation (armor-around-center) motion model in the IMM.
- Robust MPC with constraint tightening based on $\Delta$ (tube/robust formulation) instead of the firing-margin heuristic.
- Embedded C++/OSQP solver and deployment on the custom infantry robot.
- Real-robot experiments per Section V (referee-system hit detection, pre-registered 300 shots $\times$ 3 rounds per condition).


---

# VII. Conclusion

We presented a delay-aware predictive control framework for moving-target tracking on RoboMaster-style gimbals, with explicit online estimation of the multi-segment vision/actuation latency chain, an IMM estimator with out-of-sequence measurement handling, an input-delay-augmented MPC solved by a real-time ADMM QP, and a delay-uncertainty-aware firing decision. On a pre-registered simulation benchmark, the proposed controller improved hit rate over the community-standard $Kt+B$+PID baseline by 12--42 percentage points in all 12 conditions ($p<0.01$; 11 of 12 at $p<0.001$), and over a delay-unaware MPC on line, circle, and accelerating motion, with the largest margins over that baseline under drifting latency. Ablations and a zero-delay upper bound substantiate the attribution of the gain to delay modeling and lead prediction. The solver satisfies the 20-ms control period with margin. Real-robot validation and an open benchmark are the next steps toward a complete, reproducible study.
