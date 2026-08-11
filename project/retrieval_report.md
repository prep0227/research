# Retrieval Report

## RetrievalPolicy
- domain: robotics/control (RoboMaster 自瞄 + 视觉时延补偿 + 预测控制)
- required_source_types: [survey, representative_methods, recent_works, community_practice, benchmark]
- coverage_threshold: 0.7 | saturation_threshold: 0.7 | min_source_diversity: 5 | max_iterations: 3

## Query Expansions (3 轮)
- R1: RoboMaster gimbal auto-aim target tracking control paper
- R2: visual latency delay compensation target tracking predictive control
- R3: model predictive control moving target tracking gimbal camera
- R4: RoboMaster AI Challenge auto-aim paper 2023 2024
- R5: image processing delay compensation gimbal control system
- R6: Kalman filter target prediction lead compensation firing delay
- R7: vision-based target tracking with time delay MPC control
- R8: time-delay compensation visual servo control robot
- R9: RoboMaster 云台 自瞄 视觉 延迟 预测 控制
- R10: 视觉延迟补偿 移动目标跟踪 预测控制 论文
- R11: RMUA RoboMaster AI Challenge champion technical report gimbal prediction
- R12: RoboMaster 步兵机器人 自瞄 运动预测 云台控制 硕士论文
- R13: 云台 目标跟踪 图像延迟 补偿 预测控制 论文
- R14: time delay compensation MPC target tracking moving target 2023 2024
- R15: RoboMaster 自瞄 技术报告 云台 预测 2023 2024 国赛
- R16: RoboMaster gimbal model predictive control auto-aim
- R17: RoboMaster 云台 模型预测控制 MPC 自瞄

## Sources Queried
- web_search(多查询)
- arxiv
- mdpi
- ieee(索引页)
- wanfang
- cnki(wap)
- kci
- pmc
- nature
- github/api
- 专利库

## Selected Count: 17

## CoverageAssessment
- domain_clusters_covered: ['robomaster_community_practice', 'robomaster_academic', 'delay_comp_visual_tracking', 'mpc_target_tracking_gimbal', 'fire_control_lead_prediction']
- source_diversity: 15 | saturation: 0.75 | met: True
- 说明: 覆盖 5 个领域簇、15+ 独立来源；第 2-3 轮新增结果多为重复/已知，判定饱和。未接入 IEEE/Web of Science 全文库，摘要级证据标注 ACCESS_RESTRICTED。