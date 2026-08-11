# Research Brief
- **id**: brief_rm_vision_delay_mpc
- **version**: v1.0.0
- **status**: draft（待 Gate 1 用户确认）

## Topic
视觉延迟补偿的移动目标跟踪预测控制——以 RoboMaster 云台自瞄为实验载体

## Domain
robotics / control / computer-vision（预测控制、视觉伺服、时延系统）

## Motivation
RoboMaster 自瞄的目标跟踪-射击闭环中存在多段延迟（视觉采集/计算、通信、云台机构、发弹、弹丸飞行），社区普遍以 EKF/KF 预测 + 经验前瞻（Kt+B）处理，缺乏统一的延迟感知预测控制框架与受控定量评估；而学术界的 MPC/时延补偿研究未以 RM 平台为载体。若能给出可复现的延迟感知预测控制方案与基准，兼具工程价值与学术意义。

## Research Question（Gate 1 审批对象，可修改）
在 RoboMaster 云台自瞄场景中，将多段时变/不确定延迟链显式建模并嵌入预测控制（延迟感知 MPC），相比当前 EKF 预测+经验前瞻+PID 以及未显式建模时延的 MPC，能否在快速机动目标跟踪中显著提升命中率并降低云台指向角误差？其提升来源（延迟建模 vs 目标模型 vs 弹道模型）是什么？

## Background
- 社区实践：RMVL（Kt+B/SHOOT_B 经验预测）、TJURM-2024（七段延迟、EKF 双模型）、rm-controls（PID+弹道解算）、SHtech 2026（IESEKF+MPC 云台规划）— ev_rmvl_predictor, ev_tjurm_delay, ev_rm_controls, ev_shtech_mpc
- 学术先例：Barreto & Batista 2000（MPC 补偿视觉运动控制延迟）、Sensors 2024（Smith 预测器）、FME 2024 / Actuators 2023 / Axioms 2024（光电跟踪延迟预测与校正）、PENC 2025（UAV-云台 MPC）、MST 2025 / IEEE 2026（视觉延迟鲁棒伺服）— ev_barreto_mpc, ev_smith_ots_2024, ev_fme_2024, ev_penc_2025, ev_nudt_mst2025, ev_ndec_2026

## Constraints
- 硬件：RoboMaster EP/自研云台 + 工业相机 + Jetson/工控机；需要裁判系统或运动捕捉提供命中/真值
- 时间：竞赛赛季节奏；理论分析（鲁棒稳定性）与工程实现需并行
- 检索范围：本次仅覆盖 web/arXiv/部分期刊索引，未接入 IEEE/Web of Science 全文库

## Unknowns
- SHtech MPC 内部对视觉时延的处理细节（需逐模块核验）
- 用户可用的具体平台（EP？自研步兵？哨兵？）与地面真值设备
- 目标运动谱（对手机动模式、装甲板旋转）与可接受的实验时长
- 预期发表目标（竞赛技术报告/中文核心/英文期刊）决定理论深度
