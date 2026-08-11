# Detection-Dropout Robustness (Supplementary, drift delay)

Dropout probability applied to detection updates; 10 seeds.

| scenario | dropout | B1 | Ours | Ours-B1 (pp, p) |
|---|---|---|---|---|
| line | 0% | 0.106 | 0.443 | +33.7 (0.000) |
| line | 10% | 0.162 | 0.437 | +27.5 (0.000) |
| line | 20% | 0.233 | 0.422 | +19.0 (0.009) |
| accel | 0% | 0.032 | 0.214 | +18.2 (0.000) |
| accel | 10% | 0.054 | 0.158 | +10.5 (0.010) |
| accel | 20% | 0.121 | 0.129 | +0.7 (0.852) |
