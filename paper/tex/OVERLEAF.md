# Overleaf 编译指南（submission-ready）

本目录 `paper/tex/` 是自包含的 IEEEtran 投稿包（不含 PDF，CI 自动编译验证）。

## 上传（推荐：zip 整个 `paper/tex/`）

1. `paper/tex/manuscript.tex`（完整版，JINT/CEP 用）或 `paper/tex/manuscript_ral.tex`（**RA-L 6 页压缩版**，Related Work/Discussion 已压缩、Fig.2 与 Table S1–S3 移补充材料）
2. `paper/tex/refs.bib`（15 条参考文献，全部含 DOI/卷期页）
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
| `Team Authors` | manuscript.tex `\author` | 真实作者（IEEE 格式：名 姓；模板见 `AUTHORS_TEMPLATE.tex`） |
| `<email>` | `\thanks` | 通信作者邮箱 |
| `<repo-url>` | Data Availability | GitHub 公开仓库 URL |

## 编译

- Overleaf：新建项目 → 上传 zip → 编译器选 **pdfLaTeX** → 编译。
- 若 `graphicspath` 报找不到图：把 `sim/results_hitrate.png`、`sim/results_ablations.png` 复制进 `paper/tex/`，
  并修改 `\graphicspath{{../../sim/}{../figures/}}` 为 `\graphicspath{{./}}`。
- 本地/CI：见 `.github/workflows/ci.yml`（`xu-cheng/latex-action`，push 自动编译）。

## 页数（已本地编译确认，2026-08-11）

- `manuscript.tex`（完整版）：**7 页**，0 错误，0 未定义引用（本地 pdflatex + bibtex 验证）。
- `manuscript_ral.tex`（RA-L 压缩版）：**6 页**，0 错误，0 未定义引用 —— **满足 RA-L 6 页限制**，可直接按此版投稿。
- 若需再压缩：Table S1–S3 移补充材料（arXiv）已做；可进一步压缩 Section II/VI 各 1/3。
