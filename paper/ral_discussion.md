# VI. Discussion and Limitations

**Summary.** The proposed controller improves hit rate over B0 by 12--42 pp in all 12 conditions ($p<0.01$; 11 of 12 at $p<0.001$), and over B1 on line, circle, and accelerating motion (9 of 12 cells, $p<0.05$). Ablations attribute the gain to delay modeling and lead prediction; the zero-delay upper bound quantifies residual latency cost; the ADMM solver meets the 20 ms period (p99=5.0 ms).

**Limitations.** (1) On the sinusoidal trajectory our method is not significantly better than B1 ($p>0.05$); a vehicle-rotation motion model is future work. (2) IMM benefit is scenario-dependent (A4 shows CV is close in our benchmark). (3) Perception noise is idealized (3 cm, no missed detections); real perception and actuator nonlinearities will be characterized in Section V. (4) We do not claim the first MPC gimbal tracking [R3] or first delay-compensated visual tracking [R5][R6]; the contribution is the explicit time-varying delay modeling, online estimation, and a controlled ablation benchmark on RoboMaster. (5) TJURM mechanical delay magnitudes are single-team estimates; our own profiling (Section V) will replace them.

**Supplementary robustness.** Supplementary Tables S1--S3 report speed-gear sensitivity (0.5--2.0 m/s), detection-dropout robustness (0--20%), and online delay-estimator accuracy; the main conclusions hold across all of them.

**Future work.** Vehicle-rotation motion model; tube/robust MPC replacing the firing-margin heuristic; embedded deployment; real-robot validation (Section V).
