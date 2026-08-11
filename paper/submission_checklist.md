# 投稿前检查清单（Submission Checklist）

## 内容完整性
- [ ] 手稿 manuscript.tex 编译通过（Overleaf/本地 TeX）
- [ ] 摘要 ≤ 250 词，关键词 4–6 个
- [ ] 图表齐全：Fig.1 架构 / Fig.2 延迟链 / Fig.3 主结果 / Fig.4 消融；Table I–IV + Table S1（速度敏感性）+ Table S2（丢帧鲁棒性）
- [ ] Section V 真机数据已填充（非占位）
- [ ] 预注册声明（指标、样本量、失败条件）在 Method 或附录
- [ ] 消融 A1–A6 全部报告，含"不显著"结果（S 形 vs B1）

## 科学诚信
- [x] 引用元数据二次核验（DOI/年份/作者；[R7] 37.6%/66.7%/41.6%、[R8] 42.9%/58.3%/72%、Axioms 2024 36.8%、R13 全文均已核验，2026-08-11；TJURM 机械段量级保留单来源标注）
- [ ] 未验证数字已标注或删除
- [ ] 新颖性声明限定检索范围（"within the searched sources"）
- [ ] 利益冲突/伦理声明（竞赛数据、裁判系统使用）
- [ ] 作者贡献与致谢（含队伍成员、指导老师）

## 数据/代码
- [ ] GitHub 仓库公开：sim/（MIT）、tools/delay_profiler/、tools/replay/、deploy/cpp/、latency_profile.yaml；CI 全绿（assemble/build_tex/C++/LaTeX/sim smoke）
- [ ] results_raw.jsonl（520 组）+ 复现脚本 + README
- [ ] 真机数据（命中事件、时间戳日志）匿名化后公开或数据可用性声明

## 期刊要求（RA-L 默认；其他按目标期刊调整）
- [ ] 视频（≥2 分钟：真机对局 + 仿真对比）— RA-L 必须（分镜见 video_storyboard.md）
- [ ] 6 页正文 + 参考文献（RA-L）或期刊模板
- [ ] Cover letter（见 cover_letter.md）
- [ ] 推荐审稿人 3–5 名（可选）
- [ ] 伦理/版权表格

## 时间线对齐（W17 投稿目标）
- [ ] W15 前：真机数据清洗+统计完成
- [ ] W16：手稿冻结 + 内部评审
- [ ] W17：提交 RA-L

## 投稿占位符（必须替换）
- [ ] `uthor{Team Authors}` → 真实作者；`<email>` → 通信邮箱；`<repo-url>` → GitHub 链接（见 OVERLEAF.md）
- [x] RA-L 页数：`manuscript_ral.tex` **本地编译确认 6 页**（0 错误），`manuscript.tex` 完整版 7 页；均满足/接近 RA-L；超限则转 JINT/CEP
- [ ] CI 首次 push 后确认 latex-build job 产出 manuscript.pdf 且无 warning
