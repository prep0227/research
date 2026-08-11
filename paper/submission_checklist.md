# 投稿前检查清单（Submission Checklist）

> 更新：2026-08-11（仿真版收尾阶段；真机数据到位前按此核对）

## 内容完整性
- [x] 手稿编译通过：`manuscript.pdf`（JINT 全稿 **9 页**）与 `manuscript_ral.pdf`（RA-L **6 页**），本地与 CI 均 0 错误、0 Overfull、无越界、引用 19/19
- [x] 摘要正文 **244 词**（≤250），关键词 5 个
- [x] 图表齐全：Fig.1 架构 / Fig.2 延迟链 / Fig.3 主结果 / Fig.4 消融；Table I–IV + 补充 S1–S6（速度命中率/速度增益、丢帧、延迟估计精度/收敛、指向 RMSE）；所有图在正文有引用（Fig.1→Method、Fig.2→Intro、Fig.3/4→Simulation）
- [ ] Section V 真机数据待填充（协议 v1.1 已定，等硬件 W10+）
- [x] 预注册载体：`project/experiment_plan.md`（时间戳 2026-08-11T12:41，早于结果）+ SHA-256 已写入 Section V 与 Data Availability
- [x] 消融 A1–A6 全部报告（A1 无时延模型 / A2 无前馈 / **A3 常数时延 MPC** / A4 CV 估计器 / A6 无收紧 / A5 变异系数），含"不显著"结果（S 形 vs B1、accel 20% 丢帧）

## 科学诚信
- [x] 引用元数据二次核验（DOI/年份/作者；R6–R12/R14/R15 作者经 CrossRef/arXiv 核验，R1–R4 机构作者，R7/R8 DOI 补齐；R19 Smith 原典）
- [x] 所有数字来自 `sim/results*.json` 生成器；全局审计无残留旧值（12–42pp、+34pp、accel 0.214 等已同步全文）
- [x] 统计严谨：两尾 paired t-test + Cohen's d + **BH-FDR**（vs B0 12/12 q<0.05，vs B1 9/9）+ p<0.001 格式
- [x] 诚实表述：估计器为 multi-model（MMAE 风格，无 mixing）；B0 为 oracle 整定（B=0.06s、精确弹道前馈）；发弹门限为固定保守 0.05 rad + 时延不确定度余量，命中用距离自适应容差；A3 常数时延仅差 1–3pp、在线估计贡献如实报告；accel RMSE vs B1 略差如实报告
- [x] 新颖性声明限定检索范围（"within the searched scope, August 2026"）
- [ ] 利益冲突/伦理声明（竞赛数据、裁判系统使用）
- [ ] 作者贡献与致谢（含队伍成员、指导老师）

## 数据/代码
- [x] GitHub 仓库公开（`https://github.com/prep0227/research`）：sim/（MIT）、tools/delay_profiler/、tools/replay/、deploy/cpp/；CI 全绿（assemble/build_tex/citation/C++/sim/双版 LaTeX）
- [x] `sim/results_raw.jsonl`（**560 组**：12 主条件×10 seeds + B2 + A2/A4/A6/A3 消融）+ 复现脚本 + README；canonical 备份 `results_raw_v05_2model_imm.jsonl`（v0.5 修复前存档见 git 历史）
- [ ] 真机数据（命中事件、时间戳日志）匿名化后公开或数据可用性声明

## 期刊要求（RA-L 默认；其他按目标期刊调整）
- [ ] 视频（≥2 分钟：真机对局 + 仿真对比）— RA-L 必须（分镜见 video_storyboard.md）
- [x] 6 页正文（RA-L `manuscript_ral.pdf`）+ 完整版 9 页（JINT/arXiv）
- [x] Cover letter（见 cover_letter.md，数字已同步新结果）
- [ ] 推荐审稿人 3–5 名（可选）
- [ ] 伦理/版权表格

## 时间线对齐（9 月–次年 1 月）
- [ ] W10 起：真机数据采集（预注册协议 300 发×3 轮/场景）
- [ ] 真机数据后：统计 + Section V 填充 + 视频制作
- [ ] 数据达标（≥5pp 且 p<0.05）→ RA-L 6 页版；不达标或时间不足 → JINT/中文核心兜底

## 投稿占位符
- [x] `\author` → **Prep Geng**；`<email>` → **qinghefoever@outlook.com**
- [x] `<repo-url>` → **https://github.com/prep0227/research**
- [x] arXiv 提交包：`paper/arxiv_submission.zip`（独立编译 0 错误 9 页）
- [ ] arXiv 上传动作（需作者账号/授权）
