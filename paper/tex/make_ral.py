#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate manuscript_ral.tex (RA-L 6-page edition) from manuscript.tex:
- Related Work  -> compressed (paper/ral_related_work.md)
- Discussion    -> compressed (paper/ral_discussion.md); Conclusion unchanged
- Fig.2 (latency chain) moved out of the main text
- Supplementary Tables S1-S3 removed (kept as placeholder pointer)

Run from paper/tex:  python3 make_ral.py   (reads manuscript.tex, writes manuscript_ral.tex)
"""
import pathlib, re, sys

TEX = pathlib.Path(__file__).resolve().parent
PAPER = TEX.parent

def md2tex(md):
    out = []
    in_list = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            if in_list: out.append(r"\end{itemize}"); in_list = False
            continue  # drop md headers (section header already in tex)
        elif line.startswith("## "):
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append(r"\subsection*{" + line[3:].strip().replace("&", r"\&") + "}")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list: out.append(r"\begin{itemize}"); in_list = True
            item = line[2:].strip()
            item = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", item)
            item = re.sub(r"\[R(\d+)\]", r"\\cite{ref\1}", item)
            out.append(r"\item " + item)
        elif line.strip() == "":
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append("")
        else:
            if in_list: out.append(r"\end{itemize}"); in_list = False
            line = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", line)
            line = re.sub(r"\[R(\d+)\]", r"\\cite{ref\1}", line)
            out.append(line)
    if in_list: out.append(r"\end{itemize}")
    return "\n".join(out)

def main():
    tex = (TEX / "manuscript.tex").read_text(encoding="utf-8")

    # 1) Related Work content replacement
    rel_old = re.search(r"(\\section\*\{II\. Related Work\})(.*?)(\\section\*\{III\. Method\})", tex, re.S)
    assert rel_old, "Related Work span not found"
    rel_new = md2tex((PAPER / "ral_related_work.md").read_text(encoding="utf-8")).strip()
    tex = tex[:rel_old.start(2)] + "\n" + rel_new + "\n" + tex[rel_old.end(2):]

    # 2) Discussion content replacement (keep Conclusion)
    disc_old = re.search(r"(\\section\*\{VI\. Discussion and Limitations\})(.*?)(\\section\*\{VII\. Conclusion\})", tex, re.S)
    assert disc_old, "Discussion span not found"
    disc_new = md2tex((PAPER / "ral_discussion.md").read_text(encoding="utf-8")).strip()
    tex = tex[:disc_old.start(2)] + "\n" + disc_new + "\n" + tex[disc_old.end(2):]

    # 3) remove Fig.2 (latency chain) environment
    fig2 = re.search(r"\\begin\{figure\}\[t\]\\centering\n\\includegraphics\[width=0\.92\\columnwidth\]{fig2_latency_chain.pdf}.*?\\end\{figure\}", tex, re.S)
    assert fig2, "Fig.2 env not found"
    tex = tex[:fig2.start()] + tex[fig2.end():]

    # 4) remove supplementary tables S1-S6, keep section header + pointer
    for label in ["tab:speed_a", "tab:speed_b", "tab:drop", "tab:de_a", "tab:de_b", "tab:rmse"]:
        pat = re.compile(r"\\begin\{table\}\[t\]\\centering\\small\n\\caption\{.*?\\label\{" + label + r"\}.*?\\end\{table\}", re.S)
        tex, n = pat.subn("", tex, count=1)
        assert n == 1, f"table {label} not removed"
    tex = tex.replace("\\section*{Supplementary Material}\n",
                      "\\section*{Supplementary Material}\nSee the supplementary document for the speed-gear sensitivity (hit rates and paired gains), detection-dropout robustness, delay-estimator accuracy/settling, and pointing-error RMSE tables.\n")

    (TEX / "manuscript_ral.tex").write_text(tex, encoding="utf-8")
    print(f"manuscript_ral.tex written: {len(tex)} chars")

if __name__ == "__main__":
    main()
