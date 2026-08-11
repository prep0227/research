# 真机延迟画像测量（P3 第一优先级）

目的：按 `project/experiment_protocol.md` §2 实测自研步兵自瞄的六段延迟，
产出 `latency_profile.yaml`（各段均值/std/P50/P95/P99），直接喂给仿真 `delay_fns` 与论文表。

## 六段延迟与测量方法

| 段 | 时间戳定义 | 测量点 |
|---|---|---|
| τ_cam | 曝光中点 → 图像到达主机 Buffer | 工业相机 SDK 时间戳（曝光开始/结束）+ 回调到达时间 |
| τ_proc | 取图 → 检测 → 角点 → PNP 解算完成 | 流水线各子模块进出时间戳（ns 级插桩） |
| τ_serial | 指令主机发出 → 电控接收 | 主机发送时间戳 + 电控回执时间戳（回包带回） |
| τ_gimbal | 电控收到 → 云台到位 | 电控记录指令时间 + 编码器/IMU 到位判据时间（随状态包回传） |
| τ_fire | 发弹信号 → 弹丸出膛 | 光电/声学触发传感器，或裁判系统发弹事件 |
| τ_flight | 出膛 → 命中 | 弹道模型解算 + 实测标定（不在线测量） |

## 使用

```bash
# 1) 在自瞄代码中插入 record_timestamps.py 提供的时间戳记录（模板，按你们框架改）
# 2) 跑一次/多次对局，输出 events.jsonl（每行一个事件 {ts_ns, name, info}）
# 3) 离线计算画像
python3 compute_latency_profile.py events.jsonl latency_profile.yaml
```

## 时间基准（重要）

- 统一使用单调时钟（`time.monotonic_ns()`）；跨设备（主机/电控/裁判系统）需标定时钟偏移：
  电控回包中携带其本地单调时间，主机用往返测量估计偏移（同步误差 <1ms 即满足协议要求）。
- 曝光时间戳取**曝光中点**（= 曝光开始 + 曝光时长/2），避免曝光区间偏差。
- 每段至少 200 样本；输出分布而非单一均值（时变/抖动建模需要）。

## 输出格式

`latency_profile.yaml` 的 `vision`/`gimbal` 字段可直接对应仿真 `DelayPair` 的 `vision`/`gimbal` 估计器输入：
- `mean` → 名义延迟；`p95 - mean` → 不确定性界 Δ（用于 MPC 约束收紧）。
