#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a self-contained Overleaf upload bundle (flat directory + zip).

Usage (from paper/tex):  python3 build_submission_bundle.py
Output: paper/submission_bundle/ (flat) + paper/submission_bundle.zip
The tex files are patched to \\graphicspath{{./}} so the bundle is directory-independent.
"""
import pathlib, shutil, zipfile

TEX = pathlib.Path(__file__).resolve().parent
PAPER = TEX.parent
ROOT = PAPER.parent
BUNDLE = PAPER / "submission_bundle"

def main():
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)
    # sources: tex, bib, figures
    files = [
        (TEX / "manuscript.tex", "manuscript.tex"),
        (TEX / "manuscript_ral.tex", "manuscript_ral.tex"),
        (TEX / "refs.bib", "refs.bib"),
        (PAPER / "figures" / "fig1_architecture.png", "fig1_architecture.png"),
        (PAPER / "figures" / "fig2_latency_chain.png", "fig2_latency_chain.png"),
        (ROOT / "sim" / "results_hitrate.png", "results_hitrate.png"),
        (ROOT / "sim" / "results_ablations.png", "results_ablations.png"),
    ]
    for src, dst in files:
        assert src.exists(), src
        shutil.copy2(src, BUNDLE / dst)
    # patch graphicspath to flat
    for name in ["manuscript.tex", "manuscript_ral.tex"]:
        p = BUNDLE / name
        t = p.read_text(encoding="utf-8")
        t = t.replace(r"\graphicspath{{../../sim/}{../figures/}}", r"\graphicspath{{./}}")
        p.write_text(t, encoding="utf-8")
    # manifest + readme
    (BUNDLE / "MANIFEST.md").write_text(
        "# Submission bundle manifest\n\n"
        "- `manuscript.tex` — full version (JINT/CEP).\n"
        "- `manuscript_ral.tex` — RA-L 6-page compressed edition.\n"
        "- `refs.bib` — 15 references (all with DOI/volume/pages).\n"
        "- `fig1_architecture.png`, `fig2_latency_chain.png`, `results_hitrate.png`, `results_ablations.png` — all figures.\n\n"
        "## Before upload (Overleaf)\n"
        "1. Replace `Team Authors`, `<email>`, `<repo-url>` (see OVERLEAF.md in paper/tex/).\n"
        "2. Compile with pdfLaTeX (main file: manuscript.tex or manuscript_ral.tex).\n"
        "3. RA-L: confirm body <= 6 pages; otherwise use the full version for JINT/CEP.\n",
        encoding="utf-8")
    (BUNDLE / "README.md").write_text(
        "Upload the whole `paper/submission_bundle/` folder (or submission_bundle.zip) to Overleaf as a new project.\n"
        "Both tex files already point at `./` for graphics, so no directory juggling is needed.\n",
        encoding="utf-8")
    # zip
    zpath = PAPER / "submission_bundle.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(BUNDLE.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(BUNDLE))
    print(f"bundle ready: {BUNDLE} ({sum(1 for _ in BUNDLE.rglob('*') if _.is_file())} files), zip={zpath} ({zpath.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
