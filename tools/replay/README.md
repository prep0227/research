# tools/replay/ — Offline Replay Harness (real-robot log replay)

Fulfils protocol §5: *"任意方案可在同一日志上重放控制律（同前级检测/解算输出）→ 隔离'控制/补偿'贡献"*.

## What it does

Given a recorded event log (schema in `EVENT_LOG_SCHEMA.md`), replays the three control
laws — B0 (RMVL-style Kt+B+PID), B1 (delay-unaware MPC), Ours (delay-aware MPC) — on the
**same detection stream** and latency measurements, and evaluates each offline against
`target_truth` (encoder/motion-capture ground truth). Detection/PnP front end is shared,
so differences isolate the prediction/control/firing-decision contribution.

## Usage

```bash
# 1) generate a synthetic log (no hardware needed)
python3 make_synthetic_log.py --scenario accel --delay drift --out log.jsonl

# 2) replay all controllers on the same log
python3 replay.py --log log.jsonl --all
#    -> B0 / B1 / Ours hit_rate + angular RMSE + shot counts

# single controller:
python3 replay.py --log log.jsonl --controller Ours --seed 0
```

## Inputs

- `detection` events -> measurement stream `(t_meas, pos)` (out-of-sequence updates).
- `latency_measure` events -> online latency estimator (Ours only).
- `target_truth` events -> ground-truth `position(t)` for offline hit evaluation.
- `fire` events (optional) -> per-shot aim comparison vs recorded decisions.

## Synthetic test (no hardware)

`make_synthetic_log.py` emits the full event stream from `sim/` trajectories + the same
drift/gamma/fixed delay profiles used in the paper, so the harness is validated end-to-end
before real logs arrive (verified: Ours > B1 > B0 on accel/drift synthetic log).
