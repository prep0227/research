# Event Log Schema (offline replay / full-chain timestamp log)

JSONL, one JSON object per line. Timestamps in **monotonic ms**; positions in **meters** (world frame, x forward, y left, z up); angles in **radians**.

## Event types

### `cam_exposure`
Camera exposure/readout ground truth for timestamp calibration.
```json
{"event":"cam_exposure","t_start_ms":0,"t_mid_ms":5,"t_end_ms":10,"frame_id":0}
```

### `detection`
Detection/PnP output (the only input the controllers see in replay).
```json
{"event":"detection","t_meas_ms":15,"frame_id":0,"pos":[1.2,-0.3,0.0],"conf":0.98}
```
- `t_meas_ms` = the **measurement timestamp** (image exposure midpoint + processing latency); controllers must use `t_meas` for out-of-sequence updates.

### `latency_measure`
Per-segment latency samples (from `tools/delay_profiler` or software injection).
```json
{"event":"latency_measure","t_ms":50,"segment":"vision","value_ms":31.2}
```
Segments: `vision`, `gimbal`, `fire`, `flight` (or full taxonomy `cam/proc/serial/gimbal/fire/flight`).

### `cmd_sent` / `gimbal_done`
Actuation timeline (for gimbal-delay estimation and verification).
```json
{"event":"cmd_sent","t_ms":48,"yaw":0.12,"pitch":-0.03,"frame_id":0}
{"event":"gimbal_done","t_ms":118,"yaw":0.1201,"pitch":-0.0298}
```

### `fire`
Shot record with the **pre-fire gun direction** (aim at decision time) and predicted impact.
```json
{"event":"fire","t_ms":152,"gun_yaw":0.13,"gun_pitch":-0.04,"pred_pos":[1.9,-0.5,0.0]}
```

### `target_truth`
Ground-truth target pose (encoder / motion capture / referee-driven known trajectory). **Required for offline hit evaluation.**
```json
{"event":"target_truth","t_ms":160,"pos":[1.93,-0.51,0.0]}
```

### `hit`
Referee verdict per shot (for real-robot primary metric).
```json
{"event":"hit","t_ms":350,"fire_t_ms":152,"hit":true}
```

## Replay semantics (tools/replay/replay.py)

1. Load `detection` events -> measurement stream `(t_meas, pos)`, sorted.
2. Load `target_truth` events -> `position(t)` interpolation for metrics.
3. Load `latency_measure` events -> feed online delay estimator (Ours) or use nominal.
4. Replay `B0` / `B1` / `Ours` control laws at control rate `dt=20ms`, using the **same** measurement stream and latency log.
5. Output per-controller: angular error RMSE, shots, offline hit rate (against `target_truth`), and per-shot aim diff vs recorded `fire` events.

This isolates the control/compensation contribution because detection/PnP front-end outputs are identical across controllers.
