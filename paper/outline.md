# 论文大纲（英文期刊，目标 RA-L / JINT / CEP）

- **工作标题（暂定）**: Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation: A RoboMaster Gimbal Case Study

## 结构

1. **Introduction**
   - RoboMaster 自瞄问题：多段延迟链（视觉/通信/机构/发弹/飞行）是命中瓶颈（证据：TJURM 延迟表、RMVL 经验前瞻）。
   - 现有实践：EKF 预测 + Kt+B 经验前瞻 + PID（分离式）；近期开源 MPC 方案（SHtech）把延迟当常量参数。
   - 学术先例：MPC 补偿视觉运动控制延迟（Barreto 2002）、Smith 预测器（Sensors 2024）等，但均不以 RM 平台为对象、无受控消融归因。
   - 贡献（三点）：① 时变延迟链显式建模 + 在线延迟估计；② 延迟感知 MPC（输入延迟状态增广 + 约束优化 + 提前瞄准参考）；③ 可复现仿真/真机基准与消融归因（延迟建模 vs 目标模型 vs 弹道）。

2. **Problem Formulation**
   - 坐标系与目标运动模型（CV/CT/IMM）。
   - 延迟链定义与不确定性界（τ = τ̄ + δ, |δ| ≤ Δ）。
   - 云台模型（两轴二阶 + 输入延迟）与瞄准/命中几何（含弹道飞行时间）。

3. **Method**
   - 3.1 IMM 目标状态估计（CV+CT，OOSM 延迟测量处理）。
   - 3.2 在线延迟估计（滑动窗均值/P95 → Δ）。
   - 3.3 延迟感知 MPC：预测参考（提前 τ_fire+τ_flight）、输入延迟增广、QP 约束（加速度/加速度变化率）、终端权重。
   - 3.4 发弹决策（fire window：预测命中角误差 + 时延不确定性收紧 `κ·v̂·Δ/dist`）。
   - 3.5 求解器：ADMM 盒约束 QP（热启动；SLSQP 兜底）。
   - 3.6 与基线的差异（B0 Kt+B+PID；B1 无时延建模 MPC）。

4. **Simulation Study**
   - 设置（预注册）：4 轨迹 × 3 延迟模式 × 3 方案 × 10 seeds；指标与统计（配对 t + Cohen's d）。
   - 结果：主表（对应 sim/results_summary.md §1）；B2 上界（§2）；消融 A1–A6（§3）。
   - 实时性：P99 求解耗时 < 控制周期。

5. **Real-Robot Experiments**（P3–P4 后填写）
   - 平台/标定/延迟画像；对照流程；命中率结果。

6. **Discussion & Limitations**
   - S 形 vs B1 无显著差异的诚实讨论；IMM vs CV 的边际收益；真机随机性。
   - 可扩展性（空中机器人、哨兵、能量机关）。

7. **Conclusion**

## 图表映射
- Fig 1 系统架构；Fig 2 延迟链画像；Fig 3 方法框图（IMM→延迟估计→MPC→fire）；Fig 4 仿真主结果条形图；Fig 5 消融；Tab 1 参数；Tab 2 主表；Tab 3 实时性。

## 数据/代码
- 仿真代码：`sim/`（MIT）；结果：`results_raw.jsonl`、`results_summary.md`。
