# 仿真阶段发布审计（v0.6-simulation）

> 生成：2026-08-11 ｜ 基线：git tag `v0.6-simulation`（HEAD `0a2df64` 附近） ｜ 后续真机阶段从该基线继续。

## 对照目标逐项审计

| 目标要求 | 状态 | 证据 |
|---|---|---|
| RQ：视觉延迟补偿的移动目标跟踪预测控制（RoboMaster 云台自瞄为载体） | ✅ | `project/research_brief.md`、论文 Title/Abstract |
| 技术路线细化 | ✅ | `project/technical_route*.md`、`project/experiment_protocol.md` v1.1 |
| 平台：自研步兵（全向轮底盘+两轴云台+工业相机） | ✅（协议就绪，硬件待 W10+） | `project/experiment_protocol.md` §1/§7、论文 §V |
| 真值：裁判系统命中判定 | ✅（协议） | 协议 §4；`tools/replay` 事件日志 schema |
| 目标谱：直线/圆周/S 形/变速 | ✅ | `sim/trajectories.py`（含 accel 轨迹修正后巡航 2.0 m/s）、论文 §IV.A |
| 产出：英文期刊（兜底中文核心） | ✅（仿真版可投稿） | `manuscript.pdf` 9 页 / `manuscript_ral.pdf` 6 页、`arxiv_submission.zip`、`fallback_zh/` |
| 时间：9 月–次年 1 月 | ✅（计划） | `project/timeline_publication.md`、协议 §7 |
| 失败阈值：命中率提升 ≥5pp | ✅（仿真远超阈值；真机门限已工具化） | 仿真 vs B0 12.1–42.4pp 全显著；`tools/real_robot_stats.py` 实现 ≥5pp 且 p<0.05 判定 |
| 仿真版与最终真机版分开推进 | ✅ | 仿真版已发布（本标签）；真机版协议预注册、工具就绪 |

## 仿真版交付物清单（均已验证）

- 论文：`paper/tex/manuscript.pdf`（9 页）与 `manuscript_ral.pdf`（6 页），0 错误、0 Overfull、无越界、引用 19/19；arXiv 包独立编译通过。
- 数据/代码：`sim/results*.json`（canonical 560 runs + 速度/丢帧/延迟估计/实时基准）、生成器、`deploy/cpp` C++ 求解器；CI（`verify`）每次 push 全绿。
- 统计严谨性：两尾 paired t-test + Cohen's d + BH-FDR（vs B0 12/12 q<0.05）；p<0.001 格式；诚实报告（S 形 vs B1 不显著、accel 20% 丢帧不显著、accel RMSE vs B1 略差、A3 常数时延仅差 1–3pp）。
- 可复现：README 全流程 runbook、Overleaf 指南（含 xelatex+bibtex）、示例统计输入。
- 审计：`project/audit/events.jsonl`（80+ 条）、`project/state.json`。

## 关键数字（canonical，修复后）

- vs B0：**12.1–42.4 pp**，12/12 p<0.01、11/12 p<0.001、FDR q<0.05 全部。
- vs B1：9/12 显著；drift 下 line +33.7 / circle +15.1 / accel +18.2 pp；S 形不显著（诚实）。
- 消融：A1（时延模型）与 A2（前馈）主导；A3（常数时延）差 1–3pp；A6 收紧小幅；A4 CV 相当。
- 实时性：ADMM P99 ≈ 5.0 ms < 20 ms。

## 剩余待办（外部依赖）

| 待办 | 依赖 | 触发 |
|---|---|---|
| 逐页视觉排版审查（mimo 辅助） | mimo-v2.5 服务恢复 | 恢复后自动执行 |
| arXiv 上传 | 作者账号/授权 | 用户确认 |
| 真机实验（标定→延迟画像→注入→数据→统计） | 硬件到位（开学后 W10+） | 按协议执行 |
| 真机数据后：Section V 填充、视频、最终投稿（RA-L/JINT，兜底中文核心） | 真机数据 | 数据达标（≥5pp 且 p<0.05） |
