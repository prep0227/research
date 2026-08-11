#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-registered real-robot statistics (protocol v1.1).

Implements the Gate-4 analysis for the real-robot phase:
  - primary test: Ours vs B0 (and Ours vs B1) PAIRED ONE-SIDED McNemar exact
    test (paired within round by shot index, alpha=0.05);
  - decision rule: observed improvement >= 5 pp AND p < 0.05;
  - additionally reports the one-sided 95% CI lower bound (normal approx,
    conservative, labeled) and Cohen's-h-like effect size (pp);
  - escalation rule: if p<0.05 but observed 3-5 pp -> one extra confirmation
    round (N=300), budget cap N=1200 per method per scenario.

Input JSON (per condition):
{
  "condition": "line/fixed",
  "method_a": "Ours", "method_b": "B0",
  "rounds": [
    {"shots": [["hit","miss"], ...] or [[1,0], ...], "name": "r1"},
    ...
  ]
}
Each pair [a,b] is the outcome of the same shot index (a=method_a, b=method_b).

Usage:
  python3 tools/real_robot_stats.py --input data.json
  python3 tools/real_robot_stats.py --input tools/real_robot_stats_example.json   # synthetic example
  python3 tools/real_robot_stats.py --selftest

See tools/real_robot_stats_example.json for the exact input schema (3 rounds x 300 paired shots).
"""
import argparse, json, math, pathlib, sys

def mcnemar_exact_one_sided(a, b):
    """a/b: arrays of 0/1 paired outcomes. One-sided p for a>b."""
    b_disc = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)   # favours a
    c_disc = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)   # favours b
    n_d = b_disc + c_disc
    if n_d == 0:
        return 1.0, b_disc, c_disc
    # P(B >= b_disc | B ~ Binomial(n_d, 0.5)) one-sided
    p = 0.0
    for k in range(b_disc, n_d + 1):
        p += math.comb(n_d, k) * 0.5 ** n_d
    return min(1.0, p), b_disc, c_disc

def hit_rate(x):
    return sum(x) / len(x) if x else 0.0

def ci_lower_one_sided(a, b, z=1.6448536269514722):
    """One-sided 95% CI lower bound for diff = p_a - p_b (normal approx, paired n)."""
    n = len(a)
    if n == 0:
        return None
    pa, pb = hit_rate(a), hit_rate(b)
    d = pa - pb
    se = math.sqrt(pa * (1 - pa) / n + pb * (1 - pb) / n) if n > 1 else 0.0
    return d - z * se

def analyze(condition, method_a, method_b, rounds, alpha=0.05, gate_pp=5.0,
            escalation_lo=3.0, escalation_hi=5.0, cap_shots=1200):
    a_all, b_all = [], []
    per_round = []
    for r in rounds:
        pairs = r["shots"]
        a = [1 if p[0] in ("hit", 1, True) else 0 for p in pairs]
        b = [1 if p[1] in ("hit", 1, True) else 0 for p in pairs]
        assert len(a) == len(b), "paired shots must have equal length"
        a_all += a; b_all += b
        per_round.append({"name": r.get("name", "?"), "n": len(a),
                          "a_hits": sum(a), "b_hits": sum(b),
                          "a_rate": hit_rate(a), "b_rate": hit_rate(b)})
    n = len(a_all)
    pa, pb = hit_rate(a_all), hit_rate(b_all)
    obs_pp = (pa - pb) * 100.0
    p, b_disc, c_disc = mcnemar_exact_one_sided(a_all, b_all)
    ci_lo = ci_lower_one_sided(a_all, b_all)
    # decision per Gate 4
    gate = (obs_pp >= gate_pp) and (p < alpha)
    escalate = (p < alpha) and (escalation_lo <= obs_pp < escalation_hi)
    cap_ok = n <= cap_shots  # budget cap is per method per scenario (N=1200)
    return {
        "condition": condition, "method_a": method_a, "method_b": method_b,
        "rounds": per_round,
        "n_paired": n, "shots_per_method": n,
        "hit_rate_a": pa, "hit_rate_b": pb, "observed_pp": round(obs_pp, 2),
        "mcnemar_discordant_a_over_b": b_disc, "mcnemar_discordant_b_over_a": c_disc,
        "mcnemar_exact_one_sided_p": p,
        "ci95_lower_one_sided_pp": round(ci_lo * 100, 2) if ci_lo is not None else None,
        "alpha": alpha, "gate_pp": gate_pp,
        "gate_met": gate,
        "escalation_recommended": escalate,
        "budget_cap_ok": cap_ok,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, help="condition JSON (see module docstring)")
    ap.add_argument("--selftest", action="store_true", help="run built-in synthetic validation")
    args = ap.parse_args()

    if args.selftest:
        # synthetic: ours 60% vs B0 40% on 900 pairs -> strongly significant
        import random
        rng = random.Random(0)
        pairs = [[1 if rng.random() < 0.60 else 0, 1 if rng.random() < 0.40 else 0] for _ in range(900)]
        res = analyze("selftest", "Ours", "B0", [{"name": "r1", "shots": pairs}])
        print(json.dumps(res, indent=2, ensure_ascii=False))
        assert res["observed_pp"] > 5 and res["mcnemar_exact_one_sided_p"] < 1e-6, "selftest failed"
        assert res["gate_met"] is True, "selftest gate failed"
        # null case: equal rates -> p >= 0.5, gate not met
        pairs0 = [[1 if rng.random() < 0.4 else 0, 1 if rng.random() < 0.4 else 0] for _ in range(900)]
        res0 = analyze("null", "Ours", "B0", [{"name": "r1", "shots": pairs0}])
        assert res0["mcnemar_exact_one_sided_p"] >= 0.5 and res0["gate_met"] is False, "null selftest failed"
        print("SELFTEST OK")
        return 0

    data = json.loads(args.input.read_text(encoding="utf-8"))
    res = analyze(data.get("condition", "?"), data.get("method_a", "A"),
                  data.get("method_b", "B"), data["rounds"])
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
