#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-benchmark ADMM/SLSQP solve time (after always-rebuild factorization fix)."""
import json, time, pathlib
import numpy as np
from controllers import ADMMSolver
from scipy.optimize import minimize

H = 18; n = 2 * H
rng = np.random.default_rng(0)
def rand_qp(d=3):
    A = np.eye(n) + 0.05 * rng.standard_normal((n, n))
    c = rng.standard_normal(n)
    lb = -np.full(n, 0.2); ub = np.full(n, 0.2)
    return A, c, lb, ub

def bench(fn, iters=2000):
    ts = []
    for _ in range(iters):
        A, c, lb, ub = rand_qp()
        t0 = time.perf_counter()
        fn(A, c, lb, ub)
        ts.append((time.perf_counter() - t0) * 1e3)
    ts = np.sort(ts)
    return {"mean_ms": float(ts.mean()), "p50": float(np.median(ts)),
            "p95": float(ts[int(0.95*len(ts))]), "p99": float(ts[int(0.99*len(ts))]),
            "max": float(ts[-1])}

solver = ADMMSolver()
def admm(A, c, lb, ub): solver.solve(A, c, lb, ub)
ad = bench(admm)
def slsqp(A, c, lb, ub):
    def obj(u): return 0.5*np.sum((A@u - c)**2)
    def jac(u): return A.T@(A@u - c)
    cons = [{"type":"ineq","fun":lambda u, i=i: u[i]-lb[i]} for i in range(n)] + \
           [{"type":"ineq","fun":lambda u, i=i: ub[i]-u[i]} for i in range(n)]
    minimize(obj, np.zeros(n), jac=jac, method="SLSQP", bounds=list(zip(lb, ub)), options={"maxiter":60, "ftol":1e-6})
sl = bench(slsqp, iters=300)
out = {"platform": "Python 3 / numpy / scipy (conservative upper bound; C++/OSQP expected much faster)",
       "H": H,
       "admm": {**ad, "control_period_ms": 20.0, "p99_lt_period": ad["p99"] < 20.0},
       "slsqp": {**sl, "control_period_ms": 20.0, "p99_lt_period": sl["p99"] < 20.0}}
pathlib.Path('rt_benchmark.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print("rt_benchmark.json:", out["admm"]["p99"], "ms (ADMM p99)")
