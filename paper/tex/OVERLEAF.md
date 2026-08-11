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

## 页数（RA-L 6 页约束）

- 当前 tex 约 28.6k 字符 + 4 图 + 5 表（I–IV + S1），预计 **7–9 页**（两栏 IEEEtran）。
- RA-L 需压缩到 6 页正文：优先移动 Table S1/S2 到补充材料（arXiv），压缩 Section II（Related Work）与
  Section VI（Discussion）各 1/3，图 2 可合并进图 1。若压缩后仍 >6 页 → 转投 JINT/CEP（无页数压力）。
