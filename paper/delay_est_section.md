### S.3 Online delay-estimator accuracy (protocol secondary metric)

Sliding-window ($W=50$) estimator vs. true latency, same per-step feed as the controller loop; causal 'lag-1' estimate (samples before the current step), steady-state window $t\in[1,6]$~s.
Under fixed delay the estimator is accurate to <0.4 ms MAE; under $\pm15$~ms jitter the per-step error is dominated by the jitter itself (MAE $\approx10$ ms), which the uncertainty bound $\Delta_i$ (P95 $\approx27$ ms) is designed to cover in the firing tightening; under drift the lag-1 estimate lags by $\approx-5$ ms (half the sliding window times the drift rate).

| mode | segment | true mean (ms) | bias (ms) | MAE (ms) | RMSE (ms) | P95 abs err (ms) | warm-up to 5 ms (s) |
|---|---|---|---|---|---|---|---|
| fixed | vision | 30.0 | -0.19 | 0.24 | 0.29 | 0.56 | 0.02 |
| fixed | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.02 |
| gamma | vision | 26.4 | -0.13 | 10.16 | 13.02 | 26.53 | 0.02 |
| gamma | gimbal | 60.0 | +0.14 | 0.32 | 0.38 | 0.66 | 0.02 |
| drift | vision | 59.9 | -5.29 | 5.29 | 5.29 | 5.66 | 0.02 |
| drift | gimbal | 89.9 | -4.96 | 4.96 | 4.97 | 5.56 | 0.02 |
