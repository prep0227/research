# Online Delay-Estimator Accuracy (protocol secondary metric)

Sliding-window (W=50) estimator vs. true latency; per-step feed as in run_once.
Steady-state window t in [1,6] s; 'lag-1' = causal (samples before current step).

| mode | segment | true mean (ms) | bias (ms) | MAE (ms) | RMSE (ms) | P95 abs err (ms) | warm-up to 5 ms (s) |
|---|---|---|---|---|---|---|---|
| fixed | vision | 30.0 | -0.19 | 0.24 | 0.29 | 0.56 | 0.02 |
| fixed | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.02 |
| gamma | vision | 26.4 | -0.13 | 10.16 | 13.02 | 26.53 | 0.02 |
| gamma | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.02 |
| drift | vision | 59.9 | -5.29 | 5.29 | 5.29 | 5.66 | 0.02 |
| drift | gimbal | 89.9 | -4.96 | 4.96 | 4.97 | 5.56 | 0.02 |
