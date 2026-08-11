# Overleaf 编译指南（submission-ready）

本目录 `paper/tex/` 是自包含的 IEEEtran 投稿包（不含 PDF，CI 自动编译验证）。

## 上传（推荐：zip 整个 `paper/tex/`）

1. `paper/tex/manuscript.tex`（完整版，JINT/CEP 用）或 `paper/tex/manuscript_ral.tex`（**RA-L 6 页压缩版**，Related Work/Discussion/Section V 已压缩、补充表 S1–S6 移补充材料）
2. `paper/tex/refs.bib`（**19 条参考文献，全部含作者/DOI/卷期页**）
3. `paper/tex/figures/` 不存在 —— 图片在 `paper/figures/` 与 `sim/`：
   - `paper/figures/fig1_architecture.png`
   - `paper/figures/fig2_latency_chain.png`
   - `sim/results_hitrate.png`
   - `sim/results_ablations.png`

   **上传后请保持目录结构**：`\graphicspath{{../../sim/}{../figures/}}` 依赖相对路径。
   更稳妥：把两张 sim 图复制到 `paper/tex/` 下并改 `\graphicspath{{./}}`（见下）。

## 编译前必须替换的占位符（TODO）

| 占位符 | 位置 | 替换为 |
|---|---|---|
| ~~`Team Authors`~~ | manuscript.tex `\author` | **已填：Prep Geng**（如需多作者，按 `AUTHORS_TEMPLATE.tex` 扩展） |
| ~~`<email>`~~ | `\thanks` | **已填：qinghefoever@outlook.com** |
| ~~`<repo-url>`~~ | Data Availability | **已填：https://github.com/prep0227/research** |

## 编译

- Overleaf：新建项目 → 上传 zip → 编译器选 **pdfLaTeX 或 XeLaTeX** → 编译。
- **为什么需要 bibtex**：IEEEtran 参考文献由 BibTeX 管理（`.bib` + `\bibliography`），与引擎无关；pdfLaTeX 与 XeLaTeX 都要跑一遍 bibtex（顺序见下）。
- 本地 **xelatex**（你机器已有 xelatex）：
  ```bash
  cd paper/tex
  xelatex -interaction=nonstopmode manuscript.tex     # 第 1 遍
  bibtex manuscript                                    # 生成参考文献
  xelatex -interaction=nonstopmode manuscript.tex      # 第 2 遍
  xelatex -interaction=nonstopmode manuscript.tex      # 第 3 遍（解析交叉引用）
  ```
- 本地 pdfLaTeX（CI/本仓库）：同上把 `xelatex` 换成 `pdflatex`、`bibtex` 换成 `bibtex.original`（若与系统 bibtex 冲突）。
- 若 `graphicspath` 报找不到图：把 `sim/results_hitrate.png`、`sim/results_ablations.png` 复制进 `paper/tex/`，
  并修改 `\graphicspath{{../../sim/}{../figures/}}` 为 `\graphicspath{{./}}`。
- 本地/CI：见 `.github/workflows/ci.yml`（`xu-cheng/latex-action`，push 自动编译）。

## 页数（已本地编译确认，2026-08-11）

- `manuscript.tex`（完整版）：**9 页**，0 错误，0 Overfull，0 未定义引用（本地 pdflatex + bibtex 验证；xelatex 同理）。
- `manuscript_ral.tex`（RA-L 压缩版）：**6 页**，0 错误，0 Overfull，0 未定义引用 —— **满足 RA-L 6 页限制**，可直接按此版投稿。
- 补充材料（速度/丢帧/延迟估计/RMSE）已并入完整版文末；RA-L 版在压缩 Section V 的同时以单行指引指向补充材料。
