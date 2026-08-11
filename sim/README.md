# sim/ — 可复现仿真环境（canonical v0.3）

RoboMaster 自瞄"延迟感知 MPC"研究的可复现仿真环境（Python + numpy/scipy）。

> **canonical = v0.3**（二模型 IMM{CV,CT} + ADMM 盒约束 QP + 在线时延估计）。
> 补充对照：`results_raw_v03_2model_imm.jsonl`、`results_raw_v04_3model_imm.jsonl`（三模型 IMM 鲁棒性检查，非主配置）。

## 模块

| 文件 | 职责 |
|---|---|
| `trajectories.py` | 目标轨迹生成：直线 / 圆周 / S 形 / 变速（`make_trajectory(name)`），方位/俯仰解算 `az_el` |
| `delay.py` | 延迟链模型：`fixed` / `uniform` / `gamma`（时变 jitter） |
| `gimbal.py` | 两轴云台：二阶模型 + 输入延迟缓冲 + 加速度/角速度限幅 |
| `estimator.py` | 目标估计：CV-KF，支持延迟测量（先回退到测量时刻更新，再传播到当前） |
| `controllers.py` | 控制器：`LeadCompPID`（B0 社区基线 Kt+B 风格）、`PlainMPC`（B1 无时延建模）、`DelayAwareMPC`（Ours 时延感知，状态含角速度 + 输入延迟增广，闭式最小二乘求解） |
| `metrics.py` | 角误差 RMSE / 命中率（弹丸飞行时间 + 装甲板角容差 + 散布噪声） |
| `run_experiments.py` | 预注册实验：4 场景 × 3 延迟模式 × 3 方案 × 10 种子 + B2/A1-A6 消融 → `results.json` + `results_summary.md`（520 runs） |
| `delay_estimator.py` | 滑动窗在线时延估计（均值/P95 → 不确定性界 Δ_i） |
| `plot_results.py` | 出图：`results_hitrate.png` / `results_ablations.png` |
| `rt_benchmark.json` | ADMM 求解耗时基准（P99=4.9ms<20ms） |

## 运行

```bash
cd sim
python3 run_experiments.py        # 520 组，约 8 分钟（支持断点续跑：results_raw.jsonl 按行去重）
python3 plot_results.py            # 重新生成结果图
```

## 当前配置（预注册值，v0.1）

- `dt=0.02s`，`T=6s`，MPC `H=30`（0.6s 时域），`Q=diag(200,200)`，`R=diag(0.1,0.1)`，终端权重 ×5
- `tau_fire=0.08s`，`tau_gimbal=0.06s`（输入延迟 3 步），`tau_vision=0.03s`（fixed / gamma jitter 0.015）
- `v_bullet=15 m/s`，装甲板半宽 `0.08m`，散布 `0.008 rad`
- 云台：`acc_max=10 rad/s²`，`rate_max=6 rad/s`

## v0.1 结果要点（`results_summary.md`，非论文结论）

- **S 形**：Ours 命中率 +6.3~6.4pp vs B0（gamma 下 p=0.005）；**变速**：Ours +35.6~43.3pp vs B0（p<0.05），且 RMSE 明显更低（~105 vs ~180 mrad）。
- **直线**：Ours 落后 B0（−4.7~12.8pp）；**圆周**：三方案命中率都低，Ours 0。
- 已知局限：CV-KF 对圆周/S 形预测有系统性滞后；MPC 未含速率约束与鲁棒时延处理；时延未在线估计。

## v0.2 升级路线（Phase 2）

1. 估计器升级为 IESEKF / CT（恒转率）与车辆旋转平移模型（TJURM 模型二）。
2. MPC 升级为带约束求解（ADMM/OSQP，参考 tinympc），加入速率约束与终端/输入约束。
3. 在线延迟估计（滑动窗均值/分位数 + 不确定性界 → 约束收紧）。
4. 延迟模式扩展：按真机"延迟画像"注入；A3 消融（固定 vs 时变）。
5. 统计升级：更多种子（≥10）、预注册显著性（配对 t / Wilcoxon + 效应量）、B2 零延迟上界。

## v0.2 结果（`results_summary.md`，10 seeds × 480 runs，~7min）

- **Ours 在 ≥3 类轨迹显著优于 B0**（直线 +34~39pp、圆周 +28~30pp、变速 +61~65pp，均 p<0.001, d>2）。
- **Ours 在直线/变速（及圆周-drift）显著优于 B1**（+13~59pp，p<0.01~0.001）；S 形 vs B1 无显著差异（诚实报告）。
- **B2 零延迟上界**：line 0.545 / circle 0.589 / accel 0.815 —— 表明延迟仍造成可观损失，时延补偿有进一步空间。
- **消融（drift）**：A2 去掉预测（lead）命中率大幅下降（如 accel 0.735→0.398，line 0.399→0.070）→ 预测贡献关键；A4 CV vs IMM 估计器差异小 → 本场景主要贡献来自时延感知 MPC + 在线时延估计。
- **实时性**：MPC 求解 P99=5.7ms < 控制周期 20ms（Python/SLSQP 保守上界）。

## v0.2 模块变更

- `estimator.py`：新增 CT-EKF 与 IMM（CV+CT）；修正 OOSM（内部时间跟踪，`t_meas - self.t` 回退）。
- `gimbal.py`：输入延迟改为**时变**（历史命令查找 `u(t-τ(t))`）。
- `controllers.py`：MPC 改 SLSQP（解析梯度）+ 加速度盒约束 + 加速度变化率约束 + 热启动；新增 `lead`（A2）与 `delay_est`（在线时延估计）接口。
- `delay_estimator.py`：滑动窗在线时延估计（均值/P95）。
- `run_experiments.py`：主矩阵 + B2 + A2/A4 消融 + 配对检验/效应量 + `results_raw.jsonl` 断点续跑。

## v0.3 结果（ADMM 求解器，`results_summary.md`，520 runs，~7min）

- **Ours 在直线/圆周/变速 3 类轨迹同时显著优于 B0 与 B1**（vs B0: +28~67pp p<0.001；vs B1: line +27~34pp、circle +6~19pp、accel +35~57pp，除 S 形外全部 p<0.05）。
- **ADMM（盒约束 QP）**：P99 求解 4.8ms < 20ms 控制周期；与 SLSQP 结果一致（0.500 vs 0.469 line-fixed 等），作为论文级实时求解器（对标 SHtech tinympc）。
- **消融（drift）**：A1 无时延建模（=B1）远差（line 0.450 vs 0.106）；A2 无预测 line 0.450→0.064；A6 关闭时延不确定性收紧 0.450→0.408（小幅一致增益）；A4 IMM vs CV 差异小（诚实报告）；A5 跨种子 CV 15–47%。
- 求解器实现：`controllers.py` 中 `ADMMSolver`（warm-start，60 iter），SLSQP 保留为兜底。

## 补充实验：三模型 IMM（CV+CT+CA）鲁棒性检查（非主配置）

实现于 `estimator.py`（`CAKF` + 三模型 `TargetIMM`），作为主配置的鲁棒性对照：
- **改善**：S 形 drift 命中率 0.111→0.146（vs B1 +5.4pp，p=0.114，仍不显著）。
- **回退**：变速 drift 0.713→0.513（−20pp）；CA 模型在减速段持续外推加速度导致过冲。
- **结论**：模型集合选择依赖场景；主配置采用二模型 IMM（CV+CT，整体最优），三模型结果作为补充/未来工作（自适应模型集切换）。
- 数据备份：`results_raw_v04_3model_imm.jsonl`（520 组）。
