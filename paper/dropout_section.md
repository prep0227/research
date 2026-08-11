### S.2 Detection-dropout robustness (supplementary)

Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. Ours remains significantly better than B1 at every dropout level ($p<0.001$); its hit rate is approximately flat across dropout, consistent with IMM prediction absorbing missed frames.

| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |
|---|---|---|---|---|
| line | 0% | 0.123 | 0.400 | +27.7 (0.000) |
| line | 10% | 0.124 | 0.462 | +33.8 (0.000) |
| line | 20% | 0.194 | 0.406 | +21.2 (0.000) |
| accel | 0% | 0.124 | 0.513 | +38.8 (0.000) |
| accel | 10% | 0.185 | 0.456 | +27.1 (0.000) |
| accel | 20% | 0.289 | 0.519 | +23.0 (0.001) |
