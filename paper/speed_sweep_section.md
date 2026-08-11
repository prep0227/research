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
| accel | 0.5 | 0.296 | 0.362 | 0.831 | +53.6 (p<0.001) | +46.9 (p<0.001) |
| accel | 1.2 | 0.130 | 0.116 | 0.480 | +35.0 (p<0.001) | +36.4 (p<0.001) |
| accel | 2.0 | 0.000 | 0.032 | 0.214 | +21.4 (p<0.001) | +18.2 (p<0.001) |
