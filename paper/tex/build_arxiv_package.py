#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an arXiv-ready submission package (full manuscript + vector figures).

Usage (from paper/tex): python3 build_arxiv_package.py
Output: paper/arxiv/ (flat) + paper/arxiv_submission.zip
"""
import pathlib, shutil, zipfile

TEX = pathlib.Path(__file__).resolve().parent
PAPER = TEX.parent
ROOT = PAPER.parent
OUT = PAPER / "arxiv"

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    files = [
        (TEX / "manuscript.tex", "manuscript.tex"),
        (TEX / "refs.bib", "refs.bib"),
        (PAPER / "figures" / "fig1_architecture.pdf", "fig1_architecture.pdf"),
        (PAPER / "figures" / "fig2_latency_chain.pdf", "fig2_latency_chain.pdf"),
        (ROOT / "sim" / "results_hitrate.pdf", "results_hitrate.pdf"),
        (ROOT / "sim" / "results_ablations.pdf", "results_ablations.pdf"),
    ]
    for src, dst in files:
        assert src.exists(), src
        shutil.copy2(src, OUT / dst)
    p = OUT / "manuscript.tex"
    t = p.read_text(encoding="utf-8")
    t = t.replace(r"\graphicspath{{../../sim/}{../figures/}}", r"\graphicspath{{./}}")
    p.write_text(t, encoding="utf-8")
    (OUT / "README.md").write_text(
        "# arXiv submission notes\n\n"
        "**Title**: Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency "
        "Compensation: A RoboMaster Gimbal Case Study\n\n"
        "**Authors**: Prep Geng (corresponding: qinghefoever@outlook.com)\n\n"
        "**Categories**: cs.RO (Robotics) ; eess.SY (Systems and Control)\n\n"
        "**Comments**: Simulation study with a pre-registered real-robot protocol (Section V); code, per-seed data, "
        "and CI at https://github.com/prep0227/research . This is the arXiv version; a version with real-robot data "
        "is planned after hardware bring-up.\n\n"
        "**License**: CC BY 4.0 (recommended for arXiv)\n\n"
        "**Files**: manuscript.tex (pdfLaTeX), refs.bib, fig1_architecture.pdf, fig2_latency_chain.pdf, "
        "results_hitrate.pdf, results_ablations.pdf. Compile with pdfLaTeX + BibTeX (2 passes).\n",
        encoding="utf-8")
    zpath = PAPER / "arxiv_submission.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT))
    print(f"arXiv package ready: {OUT} ({sum(1 for _ in OUT.rglob('*') if _.is_file())} files); zip={zpath}")

if __name__ == "__main__":
    main()
