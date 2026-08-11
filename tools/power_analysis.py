#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statistical power analysis for the real-robot paired hit-rate comparison.

Design (preregistered, project/experiment_protocol.md):
  - 3 methods x S scenarios; per method: N shots/round x M rounds (blocked, randomized order).
  - Primary test: one-sided comparison of hit rate Ours vs B0 on paired shots
    (same target-state sequence within a round), using McNemar's exact test.
  - Success criterion (user-approved): observed improvement >= 5 pp AND p < 0.05.

We simulate paired binary outcomes with a latent bivariate-normal model to control
the within-round pairing correlation rho, then estimate:
  power = P(obs_improve >= 5pp and p < 0.05 | true delta = 5pp)
across baseline hit rates p0 and design sizes.
"""
import json, math, pathlib
import numpy as np

RNG = np.random.default_rng(20260811)

def simulate_paired(N, p0, delta, rho, n_mc=20000, seed=0):
    rng = np.random.default_rng(seed)
    # latent normal thresholds for p0 and p1=p0+delta
    z0 = -np.sqrt(2) * np.ones(N)  # placeholder, replaced below
    def thresholds(p):
        return [np.quantile(np.random.default_rng(1).normal(size=400000), 1 - p)] if False else None
    # analytic: standard normal quantile
    from scipy import stats
    t0 = stats.norm.ppf(1 - p0)
    t1 = stats.norm.ppf(1 - (p0 + delta))
    cov = np.array([[1.0, rho], [rho, 1.0]])
    hits = np.zeros(n_mc)
    ps = np.zeros(n_mc)
    for i in range(n_mc):
        x = rng.multivariate_normal([0, 0], cov, size=N)  # N x 2
        a = x[:, 0] > t0
        b = x[:, 1] > t1
        discordant = a != b
        nd = discordant.sum()
        if nd == 0:
            ps[i] = 1.0
        else:
            n01 = int((~a & b).sum())  # B0 miss, Ours hit
            # McNemar exact one-sided: P(Bin(nd,0.5) >= n01)
            ps[i] = stats.binom.sf(n01 - 1, nd, 0.5)
        hits[i] = (b.mean() - a.mean()) * 100.0
    # success: observed >= 5pp and p < 0.05
    return float(((hits >= 5.0) & (ps < 0.05)).sum()) / n_mc, float((ps < 0.05).mean()), float(np.mean(hits))

def main():
    out = {}
    rows = []
    for p0 in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        for N in [200, 300, 400]:
            for rho in [0.5, 0.8]:
                power, rej, mean_imp = simulate_paired(N, p0, 0.05, rho, n_mc=10000, seed=int(p0*1000)+N)
                out[f"p0={p0:.2f},N={N},rho={rho}"] = {
                    "power_ge5pp_and_p05": round(power, 3),
                    "rejection_rate": round(rej, 3),
                    "mean_obs_improve_pp": round(mean_imp, 2),
                }
                rows.append((p0, N, rho, power, rej, mean_imp))
    # also: aggregate M rounds => total shots per method = N*M; report the recommended
    path = pathlib.Path(__file__).resolve().parent.parent / "project" / "real_power_analysis.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"{'p0':>5} {'N':>4} {'rho':>4} {'power>=5pp&p<.05':>17} {'rej':>6} {'mean_imp':>8}")
    for p0, N, rho, power, rej, mean_imp in rows:
        print(f"{p0:5.2f} {N:4d} {rho:4.1f} {power:17.3f} {rej:6.3f} {mean_imp:8.2f}")

if __name__ == "__main__":
    main()
