### S.1 Speed-gear sensitivity (supplementary)

Nominal target speed gears 0.5 / 1.2 / 2.0 m/s, drifting-latency profile, 10 seeds. Hit rate (mean) by controller; gains are paired mean differences with one-sided paired t-test p-values (statistics computed from per-seed data in `sim/results_speed_sweep.json`).

| scenario | speed (m/s) | B0 | B1 | Ours | Ours$-$B0 (pp, p) | Ours$-$B1 (pp, p) |
|---|---|---|---|---|---|---|
| line | 0.5 | 0.247 | 0.227 | 0.698 | +45.1 (0.000) | +47.1 (0.000) |
| line | 1.2 | 0.088 | 0.106 | 0.402 | +31.4 (0.000) | +29.6 (0.000) |
| line | 2.0 | 0.072 | 0.065 | 0.273 | +20.2 (0.000) | +20.8 (0.000) |
| circle | 0.5 | 0.252 | 0.254 | 0.560 | +30.8 (0.000) | +30.5 (0.000) |
| circle | 1.2 | 0.048 | 0.119 | 0.145 | +9.8 (0.005) | +2.6 (0.347) |
| circle | 2.0 | 0.000 | 0.025 | 0.014 | +1.4 (0.343) | -1.1 (0.655) |
| s | 0.5 | 0.009 | 0.198 | 0.638 | +62.9 (0.000) | +44.0 (0.000) |
| s | 1.2 | 0.000 | 0.074 | 0.070 | +7.0 (0.000) | -0.4 (0.806) |
| s | 2.0 | 0.000 | 0.014 | 0.062 | +6.2 (0.001) | +4.8 (0.002) |
| accel | 0.5 | 0.629 | 0.628 | 0.927 | +29.8 (0.000) | +29.9 (0.001) |
| accel | 1.2 | 0.424 | 0.305 | 0.774 | +35.0 (0.004) | +46.9 (0.000) |
| accel | 2.0 | 0.143 | 0.124 | 0.513 | +37.0 (0.000) | +38.8 (0.000) |
