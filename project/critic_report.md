# Critic Report

- **id**: critic_delay_mpc_rm
- **decision**: REVISE

## Strengths
- 方向落在真实工程痛点：RM 自瞄延迟链已被社区明确定义且被公认为命中瓶颈（TJURM/RMVL）。
- 有可复现的实验载体（RoboMaster 平台 + 裁判系统命中数据 + 开源代码基座 RMVL/SHtech）。
- 学术侧有扎实先例（MPC 视觉延迟补偿、Smith、自适应 KF），可形成方法论对照。

## Weaknesses
- ‘MPC+视觉延迟补偿’本身不是新组合：Barreto(2002) 已提出 MPC 补偿机械延迟，光电跟踪文献已系统研究延迟补偿。
- 开源社区 2026 年已出现 MPC 云台规划自瞄（SHtech），直接把‘RoboMaster+MPC’当创新会被证伪。
- 延迟数值依赖单战队经验（TJURM），需要自建测量协议，否则证据链脆弱。

## Fatal Risks
- Novelty Risk（N1/N2）：存在高度相似开源实现（SHtech）与学术先例（Barreto 2002），宽泛表述不成立；必须收窄为‘时变视觉延迟显式建模 + 鲁棒性 + 受控对比’。
- Evidence Risk：SHtech 内部时延处理仅部分核验；TJURM 延迟数值与 MDPI 提升百分比（42.9%/36.8%）未二次核验，引用需标注。
- Method Risk：真实平台命中率受弹道、机械、裁判系统随机性影响大；若无地面真值轨迹，无法分离‘延迟补偿’贡献。
- Alternative Explanation：性能提升可能来自目标运动模型（EKF vs IESEKF）、检测精度或弹道模型，而非延迟补偿；需消融隔离。

## Recommended Changes
- 研究问题收窄：以‘时变视觉延迟链的显式建模 + 延迟感知预测控制（含鲁棒性分析）’为核心贡献，RoboMaster 仅作为验证载体。
- 先把 SHtech 仓库逐模块核验（Planner/predict 全部源码 + issue/评测），在论文中明确差异化：本工作补充时延显式建模、鲁棒性与受控实验。
- 预注册实验：仿真（含延迟真值）+ 真实平台（地面真值轨迹/裁判系统命中），主指标命中率与跟踪角误差 RMSE，并预先定义失败条件。
- 在方法中把 SHtech 风格 MPC 作为基线之一，避免‘与空基线对比’。

## 检查清单
- [x] Novelty Risk 已评估（N1/N2：存在 SHtech 与 Barreto 先例）
- [x] Claim 未超过 Evidence（延迟数值/提升百分比标注未核验）
- [x] 实验可证明问题（仿真+真实+消融+失败条件）
- [x] 替代解释已考虑（A1-A4 消融隔离）