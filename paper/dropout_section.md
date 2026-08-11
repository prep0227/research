### S.2 Detection-dropout robustness (supplementary)

Detection-update dropout 0% / 10% / 20%, drifting-latency profile, 10 seeds. Ours is significantly better than B1 at 0% and 10% dropout in both scenarios ($p<0.05$: line +33.7/+27.5 pp, accel +18.2/+10.5 pp). At 20% dropout the line gain remains significant (+19.0 pp, 0.009) but the accel gain narrows to +0.7 pp (0.852), so the benefit degrades as detections are lost on the fastest trajectory; multi-model prediction absorbs missed frames on line but not fully on accelerating motion.

| scenario | dropout | B1 | Ours | Ours$-$B1 (pp, p) |
|---|---|---|---|---|
| line | 0% | 0.106 | 0.443 | +33.7 (p<0.001) |
| line | 10% | 0.162 | 0.437 | +27.5 (p<0.001) |
| line | 20% | 0.233 | 0.422 | +19.0 (0.009) |
| accel | 0% | 0.032 | 0.214 | +18.2 (p<0.001) |
| accel | 10% | 0.054 | 0.158 | +10.5 (0.010) |
| accel | 20% | 0.121 | 0.129 | +0.7 (0.852) |
