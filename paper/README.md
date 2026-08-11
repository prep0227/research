# Paper workspace

| 文件 | 内容 | 再生方式 |
|---|---|---|
| `manuscript.md` | 完整英文手稿草稿 v0.5.2（Abstract + I–VII + References + Data Availability + Supplementary S1–S3） | 由各 section 文件组装；`simulation_section.md` 由 `generate_sim_section.py` 生成；S1/S2/S3 由对应 generate_*_section.py 从 sim JSON 生成 |
| `abstract.md` / `introduction.md` / `related_work.md` / `method.md` / `discussion_conclusion.md` / `references.md` / `real_robot_section.md` | 分章节草稿 | 手工维护 |
| `simulation_section.md` | Simulation Study（数字与 sim/results.json 强一致） | `python3 generate_sim_section.py` |
| `methods_math.md` | 方法数学稿（IMM/延迟链/MPC/ADMM/收紧） | 与 sim 实现同步维护 |
| `outline.md` | 论文结构与图表映射 | 手工维护 |

## 数字纪律

- Simulation 章节数字**只准**从 `sim/results.json` / `sim/rt_benchmark.json` 生成，禁止手改。
- 参考文献 [R1]–[R15] 与 `project/evidence_report.md` 的 EvidenceRecord 对应；[R7] 37.6%/66.7%/41.6%、[R8] 42.9%/58.3%/72%、Axioms 2024 36.8%、[R13] 全文命中率均已核验（2026-08-11）；TJURM 机械段量级保留单来源标注。

## 下一步（论文侧）

- [ ] Introduction/Related Work 校对（补充最新文献，投稿前）
- [ ] 真机章节数据填充（P4 后）
- [ ] 期刊模板化（RA-L / JINT / CEP 二选一）与 LaTeX 转换

## 投稿包（本轮新增）

| 文件 | 内容 |
|---|---|
| `journal_selection.md` | 期刊对比与推荐路线（首选 RA-L，次选 JINT/CEP，兜底 MDPI/IEEE Access/中文核心） |
| `tex/manuscript.tex` + `tex/refs.bib` | IEEEtran 手稿（4 图 + Table I–IV/S1/S2/S3，cite 15 条；**无本机 LaTeX，Overleaf 编译，CI latex-action 验证**，见 `tex/OVERLEAF.md`） |
| `tex/build_tex.py` | 从 section md + results.json 重建 tex（数字强一致） |
| `cover_letter.md` | RA-L 投稿信初稿 |
| `submission_checklist.md` | 投稿前检查清单（内容/诚信/数据/期刊要求/时间线） |

## 补充材料（自动生成，数字纪律）

| 文件 | 内容 | 生成器 |
|---|---|---|
| `speed_sweep_section.md` | Table S1 速度敏感性（360 runs） | `generate_speed_sweep_section.py` |
| `dropout_section.md` | Table S2 检测丢帧鲁棒性（120 runs） | `generate_dropout_section.py` |
| `delay_est_section.md` | Table S3 延迟估计器精度 | `generate_delay_est_section.py` |
| `video_storyboard.md` | RA-L 视频分镜（真机段待 P4） | 手工 |
