# Gap Report

## 判定规则：Limitation + Importance + Feasibility + Evidence


### gap_delayaware_mpc — PLAUSIBLE_GAP (Risk: MEDIUM)
- **Problem**: RoboMaster 自瞄缺少把‘多段时变/不确定视觉-机构-弹道延迟链’显式建模进预测控制的统一方案，且缺乏受控、可复现的延迟补偿对比实验。
- **Existing Solution**: 社区主流：EKF/KF 预测 + 经验 Kt+B + PID（RMVL/TJURM/rm-controls）；新近开源：MPC 云台规划但延迟以常量参数近似（SHtech）；学术：MPC 视觉延迟补偿（Barreto 2002）、Smith/插值/自适应 KF（Sensors 2024、FME 2024、MST 2025）。
- **Limitation**: 社区实践的延迟处理依赖人工调参、无时变/不确定性建模、无公开对照评测；学术先例不针对 RM 平台与弹道射击场景；SHtech 无受控实验。
- **Evidence Refs**: ev_tjurm_delay, ev_rmvl_predictor, ev_shtech_mpc, ev_barreto_mpc, ev_smith_ots_2024
- **Potential Value**: 若成立，可给出 RM 自瞄可复现的延迟感知预测控制方案与定量基准，服务竞赛与低成本打击平台。
- **判定检查**: Limitation 有证据（TJURM/SHtech/RMVL）；Importance 明确（延迟被公认为性能瓶颈）；Feasibility 可评估（仿真+真实平台可控）；Evidence 已绑定。

### gap_benchmark — SUPPORTED_GAP (Risk: LOW)
- **Problem**: 缺少公开的 RoboMaster 自瞄延迟测量协议与延迟补偿基准（含地面真值、轨迹集、指标）。
- **Existing Solution**: 各战队私有自测；TJURM wiki 给出延迟分段但无标准协议；学术基准面向光电跟踪而非 RM。
- **Limitation**: 无可复用评测，导致不同方案无法横向比较。
- **Evidence Refs**: ev_tjurm_delay, ev_shtech_mpc, ev_arxiv_2312_05055
- **Potential Value**: 工程/基准贡献，可独立发表或作为方法论文附属。
- **判定检查**: Limitation 有证据；Importance 中等；Feasibility 高；Evidence 已绑定。

### gap_delay_robust_mpc — PLAUSIBLE_GAP (Risk: HIGH)
- **Problem**: 时变/不确定视觉延迟下 MPC 的鲁棒稳定性条件与实时求解在 RM 场景未验证。
- **Existing Solution**: Smith 预测器给出模型失配下稳定性条件（Sensors 2024）；时变时延 MPC 远程控制（IEEJ 2024）；RM 场景无验证。
- **Limitation**: 理论门槛高、验证周期长，且可能被现有鲁棒控制/扰动观测方法覆盖。
- **Evidence Refs**: ev_smith_ots_2024, ev_shtech_mpc
- **Potential Value**: 理论贡献强，但风险高。
- **判定检查**: Limitation 有证据；Importance 中等偏上；Feasibility 中等；Evidence 偏弱。

## Selected Gap
- **selected_gap_id**: gap_delayaware_mpc（与 gap_benchmark 联合推进：方法 + 基准）