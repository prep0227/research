#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replay an event log for two controllers and run the pre-registered paired
statistics (protocol v1.1) in one command.

Pipeline: event log -> replay B0/B1/Ours on the SAME detection stream (per-shot
outcomes with the same dispersion noise draw) -> pair by shot ordinal within the
round (protocol pairing) -> real_robot_stats.analyze (paired one-sided McNemar
exact, >=5pp & p<0.05 gate, one-sided 95% CI lower bound, escalation rule).

Usage:
  python3 tools/make_synthetic_log.py --scenario line --delay drift --out /tmp/r1.jsonl   # (optional, no HW)
  python3 tools/replay_to_stats.py --log /tmp/r1.jsonl --method_a Ours --method_b B0 --seed 0 --round line/drift
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "replay"))
from replay import load_log, replay            # noqa: E402
from real_robot_stats import analyze           # noqa: E402

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, type=pathlib.Path, help="event log JSONL (EVENT_LOG_SCHEMA.md)")
    ap.add_argument("--method_a", default="Ours")
    ap.add_argument("--method_b", default="B0")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--round", default="round1")
    ap.add_argument("--out", type=pathlib.Path, default=None, help="optional JSON output")
    args = ap.parse_args()

    events = load_log(args.log)
    ma = replay(events, args.method_a, seed=args.seed)
    mb = replay(events, args.method_b, seed=args.seed)
    oa, ob = ma["shot_outcomes"], mb["shot_outcomes"]
    n = min(len(oa), len(ob))
    if n == 0:
        raise SystemExit("no paired shots (one controller fired 0 shots)")
    pairs = [[oa[i], ob[i]] for i in range(n)]
    res = analyze(args.round, args.method_a, args.method_b,
                  [{"name": args.round, "shots": pairs}])
    res["shots_a"] = len(oa); res["shots_b"] = len(ob); res["paired_n"] = n
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.out:
        args.out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
