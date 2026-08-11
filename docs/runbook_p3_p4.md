# P3/P4 真机执行 Runbook（硬件到位后按此执行）

> 对应协议：`project/experiment_protocol.md` v1.1；统计功效：`project/real_power_analysis.json`。
> 前置：队伍可安排 1 名电控 + 1 名视觉 + 场地（≥6m×6m）+ 裁判系统。

## 阶段 P3：延迟画像（2 周）

### 第 1 周：标定
| 项 | 方法 | 验收 |
|---|---|---|
| 相机内参/外参 | 棋盘格 + 手眼 | 重投影 <0.3px |
| PnP | 装甲板四点 | 3m 位置误差 <3cm |
| 弹道 | 不同距离实弹 | 飞行时间误差 <10ms |
| 云台带宽 | 阶跃响应 | 一/二阶模型 + 延迟分布 |

### 第 2 周：画像（每段 ≥200 样本）
```bash
# 1) 在流水线插桩（模板在 tools/delay_profiler/record_timestamps.py）
#    记录：曝光中点/取图/检测/PNP/指令发送/回执/云台到位/发弹/命中
# 2) 计算画像
python3 tools/delay_profiler/compute_latency_profile.py --events events.jsonl \
    --out latency_profile.yaml
# 3) 验收：各段 P99-mean 与仿真三模式对齐（fixed≈常数；gamma≈±20% 抖动；drift≈±30% 漂移）
#    不对齐 → 调整仿真参数并重跑补充仿真（sim/run_*.py）
```

## 阶段 P4：受控对照（3 周）

### 第 1 周：注入与采集
- 按协议 §2.1 实现软件延迟注入（固定/gamma/drift 三种画像，时间戳搬移）。
- 靶标装置：旋转臂（圆周）、循迹小车（直线/变速）、摆动机构（S 形）；速度档 0.5/1.2/2.0 m/s。
- 每方案每场景 **300 发 × 3 轮**（轮次随机交叉）；保存全链路事件日志（schema: `tools/replay/EVENT_LOG_SCHEMA.md`）。

### 第 2 周：离线重放 + 在线统计
```bash
# 离线重放（同一日志 → B0/B1/Ours 对比，隔离控制贡献）
python3 tools/replay/replay.py --log round1.jsonl --all

# 主统计（配对单侧 McNemar + 单侧 95% CI 下界）
python3 tools/power_analysis.py            # 功效参考（N=900/方法：显著功效≈0.85@5pp）
python3 tools/replay/stats_report.py       # （P4 时补充：输出每场景配对 p 与 CI）
```

### 第 3 周：判定与收尾
| 结果 | 行动 |
|---|---|
| ≥2 场景 `p<0.05 且观测≥5pp（或 CI 下界≥3pp）` | 支持假设 → 填 Section V，投 RA-L |
| 仅 1 场景达标 | 追加 1 轮（N=300）收窄 CI；仍不达标 → 改"跟踪误差"定位 |
| 0 场景达标 | 假设不成立 → 按失败条件改写论文定位或转中文核心 |

## 关键风险与对策
- **时延测量 <1ms 精度**：用光电/声学出膛触发 + 裁判系统时间戳；达不到 → 回退仿真+半实物（论文如实说明）。
- **云台 P99 超 20ms**：降 H（18→12）或换 `deploy/cpp/mpc_solver.hpp`（C++17 ADMM，测试通过）。
- **靶标丢失/丢帧**：仿真已验证 0–20% 丢帧下 Ours 稳健（Table S2），无需加实验。
- **裁判系统命中判定**：命中事件需与 `fire` 事件按发弹序号配对（schema 中 `hit.fire_t_ms`）。
