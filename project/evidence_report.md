# Evidence Report

- **assessment_date**: 2026-08-11
- **检索方式**: 本次会话真实网络检索（web search + 来源页读取 + GitHub API 核验）

## Claims

### clm_rm_practice — Confidence: HIGH
- **Claim**: RoboMaster 自瞄的主流公开实践是‘检测 + EKF/KF 目标预测 + 弹道补偿 + PID（串级/前馈）控制’，预测与控制分离，延迟主要靠经验参数（Kt+B、SHOOT_B）处理。
- **Allowed Expression**: Evidence supports：多个相互独立的公开来源（RMVL 官方文档、TJURM-2024 wiki、rm-controls、arXiv 论文、核心期刊摘要）一致表明该实践模式。
- **Evidence**: ev_rmvl_predictor, ev_tjurm_delay, ev_rm_controls, ev_arxiv_2312_05055, ev_harbe_kalman_2022

### clm_delay_chain — Confidence: MEDIUM
- **Claim**: RM 自瞄总延迟由多段组成：视觉采集/计算约 10ms 量级，信号/通信 1ms 量级，机械旋转 20–200ms，发弹 50–100ms，弹丸飞行 50–250ms；后三段远大于视觉计算段。
- **Allowed Expression**: Current evidence suggests：具体数值主要来自 TJURM 单战队 wiki（未经第二来源核验），但延迟分段结构被 RMVL 与社区教程定性支持。
- **Evidence**: ev_tjurm_delay, ev_rmvl_predictor, ev_guyue_2021

### clm_delay_hurts — Confidence: HIGH
- **Claim**: 视觉/图像处理延迟会显著限制跟踪闭环带宽并降低跟踪精度；插值、Kalman/EKF 预测、Smith 预测器、MPC 等已被用于补偿该延迟。
- **Allowed Expression**: Evidence supports / Studies consistently indicate：跨多个独立来源（IEEE、Sensors、FME、MST）一致。
- **Evidence**: ev_barreto_mpc, ev_smith_ots_2024, ev_fme_2024, ev_mdpi_act2023, ev_nudt_mst2025, ev_ndec_2026

### clm_mpc_prior — Confidence: MEDIUM
- **Claim**: MPC 已用于视觉运动控制的延迟补偿（Barreto 2000）及 UAV/云台目标跟踪（PENC 2025 等）；RoboMaster 开源社区 2026 年出现基于 MPC 的云台规划实现（SHtech），但未以视觉时延显式/鲁棒补偿为核心贡献，且未见受控定量评估。
- **Allowed Expression**: Current evidence suggests：学术先例存在（MEDIUM）；SHtech 仅部分核验（MEDIUM）。
- **Evidence**: ev_barreto_mpc, ev_penc_2025, ev_shtech_mpc

### clm_no_peer_rq — Confidence: MEDIUM
- **Claim**: 在本次检索范围内，未发现‘以 RoboMaster 云台为载体、显式建模时变视觉延迟并嵌入预测控制、附受控定量评估’的同行评审工作。
- **Allowed Expression**: 允许表述：Initial search did not identify highly similar peer-reviewed work within the searched sources；开源社区实现（SHtech 2026）存在，需视为直接先例。
- **Evidence**: ev_shtech_mpc, ev_harbe_kalman_2022, ev_arxiv_2312_05055, ev_tjurm_delay

## Evidence Records

### ev_rmvl_predictor — RMVL: 在整车状态估计中涉及到的预测量 (2023)
- 来源: RoboMaster Vision Community 官方文档 | 标识: https://cv-rmvl.github.io/docs/1.0.0/d1/d40/tutorial_autoaim_gyro_predictor.html | 访问: fulltext
- 质量: R=3 D=2 X=3 P=3 A=3 | bias: KNOWN/LOW
- 摘录: 静态响应预测量…由于通信延迟的存在需要提前瞄准的预测量，调节参数为B（秒）；动态响应预测量…与子弹飞行时间呈正相关，调节参数为K；射击延迟预测量…抵消射击延迟带来的发射滞后，调节参数为SHOOT_B。调参策略：先设K=0调B直至目标不再滞后，再调K。
- 摘要: RMVL 官方文档将 RoboMaster 自瞄预测量分为静态响应（B）、动态响应（Kt）与射击延迟（SHOOT_B）三类，均为经验参数、人工调参；预测与控制（发弹决策）分离。
- content_hash: sha256:bfda88b886b509c5b303e0ea3d6e8514b31548c15b23d00d34f3a0a43d74dfa8
- 局限: 工程文档，非同行评审；参数为经验值。

### ev_tjurm_delay — TJURM 自瞄算法 Wiki（北洋机甲2024） (2024)
- 来源: GitHub wiki（天津大学 2024 自瞄框架） | 标识: https://github.com/HHgzs/TJURM-2024/wiki/TJURM%E8%87%AA%E7%9E%84%E7%AE%97%E6%B3%95Wiki | 访问: fulltext
- 质量: R=2 D=2 X=3 P=2 A=3 | bias: UNKNOWN/None
- 摘录: 延迟类型/延迟时长/是否忽略：采图1ms忽略、取图1ms忽略、计算10ms忽略、信号1ms忽略、旋转20-200ms不可忽略、发弹50-100ms不可忽略、飞行50-250ms不可忽略。目标追踪采用扩展卡尔曼滤波（EKF），两种运动模型：单板变速运动模型、车辆中心匀速旋转平移模型。
- 摘要: 天津大学 2024 战队自瞄 wiki 显式列出七段延迟及其量级，并说明旋转/发弹/飞行延迟不可忽略；其预测采用 EKF 双运动模型，属社区主流做法（经验延迟参数 + 滤波预测）。
- content_hash: sha256:109ab6360b5cbfd28d70c0746e8772da7e3298473540ef88c4eec3c42b72e1e1
- 局限: 单战队经验数据，延迟数值未与第二来源交叉核验。

### ev_shtech_mpc — SHtech_auto_aim（上海科技大学开源自瞄仓库） (2026)
- 来源: GitHub 开源仓库 | 标识: https://github.com/Astra-Whale/SHtech_auto_aim | 访问: fulltext
- 质量: R=2 D=2 X=3 P=2 A=3 | bias: KNOWN/MEDIUM
- 摘录: Planner.hpp: MPC时间步长DT=0.01s，HORIZON=100；planner_param_infantry4.yml: latency=2（PC到yaw动作完成的平均总延迟ms）、single_shoot_latency=115ms；predict/ 含 IESEKF、ExtendedKalman、Kalman；planner/tinympc 为 ADMM 求解器。
- 摘要: 2026-04 创建的 RoboMaster 自瞄开源实现：IESEKF 目标状态估计 + 基于 tinympc(ADMM) 的 MPC 云台轨迹规划 + 弹道补偿与射击决策；将通信/发射延迟作为常量参数，未发现对视觉时延链（曝光/检测/解算）的显式时变建模或受控实验评估（仅核验部分源码）。
- content_hash: sha256:655b74aa9083879f52f464355cb38876faa437df101c3968a50b0ebb0046b04c
- 局限: 仅核验 README/Planner.hpp/Planner.cpp/plannerParam 与目录结构，未逐行确认内部时延处理；无论文、无公开评测数据。

### ev_rm_controls — rm-controls/rm_controllers Gimbal Controllers (2025)
- 来源: RoboMaster 开源 ROS 控制器 | 标识: https://deepwiki.com/rm-controls/rm_controllers/2-gimbal-controllers | 访问: fulltext
- 质量: R=2 D=2 X=3 P=2 A=2 | bias: UNKNOWN/None
- 摘录: RATE/TRACK/DIRECT 三状态；yaw/pitch 采用 PID 控制；TRACK 状态基于弹道模型（BulletSolver）计算瞄准点与目标预测。
- 摘要: RoboMaster 标准开源电控控制器：云台控制为 PID，预测依赖弹道求解器，未使用 MPC 或显式时延建模。
- content_hash: sha256:4f4bcc87fc3d042712f9495c60357d38165fc9fd37d89dd24de8299f43caef4d
- 局限: 社区文档/代码库，非评审文献。

### ev_arxiv_2312_05055 — Design and Implementation of Automatic Assisted Aiming System For Robomaster EP Based on YOLOv5 (2023)
- 来源: arXiv:2312.05055 | 标识: https://arxiv.org/abs/2312.05055 | 访问: fulltext
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: KNOWN/MEDIUM
- 摘录: 集成 YOLOv5 + DeepSORT + 卡尔曼滤波预测 + PID with Feedforward Enhancement + FIR 控制器实现云台快速瞄准与位置预测；自建 AAAS-2021 数据集 2.8 万张图像。
- 摘要: RoboMaster EP 自瞄系统论文：检测+跟踪+KF 预测+PID 前馈+FID；未对视觉延迟显式建模，控制为 PID 而非预测控制。
- content_hash: sha256:0cd53affd75a8356a86b3b1220b445c9ba58218dd994506235ec109d2e3cf671
- 局限: 预印本，系统设计类，定量评估有限（主要报告 mAP 与结构）。

### ev_harbe_kalman_2022 — 基于卡尔曼滤波的目标识别跟踪与射击系统设计 (2022)
- 来源: 兵器装备工程学报（北大核心） | 标识: https://d.wanfangdata.com.cn/periodical/scbgxb202211041 | 访问: abstract
- 质量: R=3 D=2 X=3 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 以 RoboMaster 哈工程自瞄系统为例：目标识别与位置解算、云台姿态估计、目标运动预测与弹道补偿、云台运动控制四部分；KF 估计目标运动与云台姿态，弹道模型预测，串级反馈云台控制，弹丸初速 15 m/s。
- 摘要: 国内核心期刊：RM 自瞄的 KF+弹道+串级控制完整链路（摘要级）。
- content_hash: sha256:7b12ba1d1e029a727a81a31a468161aa24d9258197327d7cc8c61c576123bc90
- 局限: 仅摘要，实验细节/命中率数据不可访问。

### ev_barreto_mpc — Model predictive control to improve visual control of motion: applications in active tracking of moving targets (2000)
- 来源: IEEE ICPR 2000（15th Int. Conf. on Pattern Recognition），vol.4 pp.732-735，DOI 10.1109/icpr.2000.903021 | 标识: https://ieeexplore.ieee.org/document/903021 | 访问: abstract
- 质量: R=3 D=3 X=2 P=2 A=3 | bias: KNOWN/LOW
- 摘录: 视觉跟踪作为调节控制问题；延迟与系统时延显著影响视觉引导系统性能；用插值处理视觉处理延迟，用 MPC 补偿视觉运动控制中的机械延迟。
- 摘要: 经典工作：已明确将 MPC 用于视觉运动控制的延迟补偿（机械延迟），插值处理视觉延迟；是'MPC+视觉时延'最直接的学术先例。
- content_hash: sha256:2690f2a902f01bc985e567209e8eb2793042f482ec1ee7f9d3dd210484a6fe59
- 局限: 2000 年 ICPR 会议工作，未覆盖现代深度学习检测与 RM 场景；元数据经 Crossref 核验（2026-08-11）。

### ev_smith_ots_2024 — A Smith Predictor Modified with a Pseudo Feedforward Control for the CCD-Based Optoelectronic Tracking System (2024)
- 来源: Sensors, 24(17):5546 | 标识: https://pmc.ncbi.nlm.nih.gov/articles/PMC11398195/ | 访问: fulltext
- 质量: R=3 D=3 X=2 P=2 A=3 | bias: KNOWN/LOW
- 摘录: CCD 光电跟踪系统中，脱靶量提取含不可忽略延迟，直接限制视觉跟踪控制带宽；Smith 预测器将时延移出闭环提升带宽；改进方法在 1Hz 最大残余误差由经典 Smith 365 arcsec 降至 283 arcsec（22.5% 提升），0.2-2Hz 主频带一致更低。
- 摘要: 光电跟踪中延迟-带宽-精度关系与 Smith 预测器补偿的最新实证；含稳定性条件（模型失配约束控制器增益）。
- content_hash: sha256:d63c9f8d7e740c06971f9af0d8dda7be1fb34999f52a3178ded8f4502a6b7e23
- 局限: 快反镜平台，非 RoboMaster 云台；数值来自该文实验（已核验全文摘要）。

### ev_fme_2024 — Small tracking error correction for moving targets of intelligent electro-optical detection systems (2024)
- 来源: Frontiers of Mechanical Engineering, 19(2):11 | 标识: https://academic.hep.com.cn/fme/CN/10.1007/s11465-024-0782-6 | 访问: abstract
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: KNOWN/MEDIUM
- 摘录: 提出跟踪控制器时延预测方法（基于两轴两云台悬臂梁共轴构型的 Euler 变换模型）+ 改进分段插值滤波；仿真（S=100m, A=1m^2, v=5m/s）：优化方法 1mrad 圆内跟踪误差分布概率 66.7% vs 传统 41.6%，LOS 射击精度提升 37.6%。
- 摘要: 国防科大团队：光电探测系统小跟踪误差校正，含跟踪控制器延迟预测与插值滤波；结果基于仿真。
- content_hash: sha256:7c8d6c1bee5c9828468cc77da75640e35e78021c16f6e1bd8e7dd2338e2b5a54
- 局限: 仅摘要；37.6%/66.7%/41.6% 数值已于 2026-08-11 经官方摘要页(academic.hep.com.cn) + 万方/Springer 检索佐证二次核验，全文实验协议细节仍不可访问。

### ev_mdpi_act2023 — Prediction and Control of Small Deviation in the Time-Delay of the Image Tracker in an Intelligent Electro-Optical Detection System (2023)
- 来源: Actuators, 12(7):296 | 标识: https://www.mdpi.com/2076-0825/12/7/296 | 访问: abstract
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 针对图像跟踪器时延提出预测与控制方法（N 步 Kalman 滤波控制器 + 火控判断 + 抗遮挡 DSST 跟踪）；官方摘要报 0.15 mrad 圆内视轴测量误差分布概率 72%、跟踪精度较传统方法提升 58.3%；正文结论报响应比提升 42.9%，目标跟踪稳定性显著改善，可避免目标检测失效。
- 摘要: 图像跟踪器时延预测与控制；58.3%/72%（官方摘要，Semantic Scholar DOI 元数据 2026-08-11 核验）+ 42.9% 响应比（MDPI XML 官方内容索引核验）。
- content_hash: sha256:3ce5e44bb421870dde4af066b9a929e5e7d1fb7f3dd0f8baebf1e61090f251d8
- 局限: 仅摘要级访问；42.9%/58.3%/72% 已二次核验（2026-08-11），方法细节与平台构型不可访问。

### ev_mdpi_axioms2024 — Optimizing Controls to Track Moving Targets in an Intelligent Electro-Optical Detection System (2024)（曾用标识 ev_mdpi_mach2024）
- 来源: Axioms, 13(2):113（原记录误标 Machines；URL 的 ISSN 2075-1680 即 Axioms），DOI 10.3390/axioms13020113 | 标识: https://www.mdpi.com/2075-1680/13/2/113 | 访问: abstract
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 优化 nKF-Gyro + 瞄准控制模型；误差抑制最高提升 36.8%；自适应视线滤波与瞄准控制模型可校正瞄准误差并提升光电探测系统射击精度。
- 摘要: EODS 瞄准控制优化（nKF-Gyro+瞄准控制）；36.8% 误差抑制提升经 Semantic Scholar 官方摘要核验（2026-08-11）。
- content_hash: sha256:c55a60bc55d0cdcf112b50482f135d860048acd66acdde41e6f0888a2c99673b
- 局限: 仅摘要级访问；36.8% 已核验（2026-08-11），方法细节不可访问。

### ev_kci_gimbal_delay — Gimbal Tracking Control with Delayed Feedback of Target Information (2021)
- 来源: KCI 期刊 | 标识: https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002480617 | 访问: abstract
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 提出利用两个图像跟踪任务与相机内置图像缓冲消除延迟；并根据延迟调整云台速度以降低因相机运动丢失目标的风险。
- 摘要: 云台延迟反馈跟踪控制：图像缓冲 + 双跟踪任务消除延迟（摘要级）。
- content_hash: sha256:c69a31a5ad81e1ebfb6c6ed26519ff3910e18b66637c1d24f5c9d6b765554cc9
- 局限: 仅摘要。

### ev_penc_2025 — PENC: a predictive-estimative nonlinear control framework for robust target tracking of fixed-wing UAVs in complex urban environments (2025)
- 来源: Scientific Reports, 15:13095 | 标识: https://www.nature.com/articles/s41598-025-13095-z | 访问: abstract
- 质量: R=3 D=3 X=2 P=2 A=2 | bias: KNOWN/LOW
- 摘录: 预测-估计非线性控制框架：MPC（滚动时域）在预测时域内优化 UAV-云台系统控制序列以满足可见性与障碍约束；NMHE 提供目标状态估计；每步仅执行首个控制量并重复优化。
- 摘要: UAV-云台目标跟踪的 MPC+NMHE 框架（摘要级），证明 MPC 在云台目标跟踪的实时可行性，但非 RM 自瞄、不聚焦视觉时延补偿。
- content_hash: sha256:6d08307695d7cfd14c06afabcfc0664f0d18a91490fe0725fca3c09ddca8feba
- 局限: 仅摘要；场景为固定翼 UAV，与 RM 弹道/射击不同。

### ev_nudt_mst2025 — A robust adaptive Kalman filter based visual servoing control for an inertial stabilization platform (2025)
- 来源: Measurement Science and Technology | 标识: https://sciprofiles.com/publication/view/7d27cd8cf1f736aa701be4520fda9e34 | 访问: abstract
- 质量: R=3 D=3 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 提出面向惯性稳定平台的视觉伺服方案，处理视觉测量延迟、传感器噪声与模型不确定对高精度跟踪的影响。
- 摘要: 自适应鲁棒 KF 处理视觉测量延迟（摘要级）。
- content_hash: sha256:c732d14d954342d54ee7ac56b5cd4b436dbb1e682ce043432d63d002563fa920
- 局限: 仅摘要。

### ev_ndec_2026 — Nonlinear Direct Error Compensator for Visual Servo Trajectory Tracking Under Image Sensor Delay on a Moving Platform (2026)
- 来源: IEEE 期刊 | 标识: https://ieeexplore.ieee.org/document/11355653 | 访问: abstract
- 质量: R=3 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 提出非线性直接误差补偿器（NDEC）抑制移动平台上视觉伺服轨迹跟踪系统中图像传感器时延引起的高频非线性扰动。
- 摘要: 图像传感器时延下视觉伺服的直接误差补偿（摘要级），属最新（2026）相关工作。
- content_hash: sha256:c08d94e65db8cefff418613f43e68f9607d3cb032631fc2e6b1c6e4ba2c57e4b
- 局限: 仅摘要。

### ev_patent_cn_strike — 基于视觉的小型无人机目标跟踪与打击的云台控制方法（CN117826873A） (2024)
- 来源: 中国发明专利 | 标识: https://patentimages.storage.googleapis.com/8a/a1/1c/db93b49d336186/CN117826873A.pdf | 访问: abstract
- 质量: R=2 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 关键点检测网络 + 匹配跟踪 + 扩展卡尔曼滤波建立目标运动模型；根据弹速计算打击延时，结合打击延时与通信延时预测打击点坐标。
- 摘要: 专利：视觉目标跟踪云台打击中，EKF 预测 + 弹速/通信延时预测打击点；表明'预测+延时'思路在工程领域常见。
- content_hash: sha256:59c46c458c699cf3076813f1d5252ba8645870688c9115804aeb412d6e485049
- 局限: 专利文献，仅摘要级浏览。

### ev_guyue_2021 — RoboMaster视觉教程（10）目标预测 (2021)
- 来源: 古月居社区教程 | 标识: http://dev.guyuehome.com/detail?id=1825476120040796162 | 访问: metadata
- 质量: R=2 D=2 X=2 P=2 A=2 | bias: UNKNOWN/None
- 摘录: 120fps 下摄像头约 8ms 延迟，加上处理与串口传输共十几毫秒；上位机发送频率低于下位机控制频率时，下位机每周期对装甲板位置预测后再控制云台旋转。
- 摘要: 社区教程证实 RM 自瞄存在约 8ms 相机延迟 + 处理/通信延迟，社区做法为下位机预测（摘要/片段级）。
- content_hash: sha256:335ad935aa219f81a5ec05f8179a1010ce04d43def8bc07cba3b8a607b6dc110
- 局限: 仅检索片段；页面正文未能抓取，访问受限。