### S.2 Detection-dropout robustness (supplementary)

Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. Ours remains significantly better than B1 at every dropout level ($p<0.001$); its hit rate is approximately flat across dropout, consistent with IMM prediction absorbing missed frames.

| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |
|---|---|---|---|---|
| line | 0% | 0.106 | 0.443 | +33.7 (p<0.001) |
| line | 10% | 0.162 | 0.437 | +27.5 (p<0.001) |
| line | 20% | 0.233 | 0.422 | +19.0 (0.009) |
| accel | 0% | 0.148 | 0.755 | +60.7 (p<0.001) |
| accel | 10% | 0.245 | 0.600 | +35.4 (p<0.001) |
| accel | 20% | 0.371 | 0.624 | +25.2 (p<0.001) |
