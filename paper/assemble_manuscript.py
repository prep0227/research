# -*- coding: utf-8 -*-
"""Assemble paper/manuscript.md from section files (run: python3 assemble_manuscript.py)."""
import pathlib, re
P = pathlib.Path(__file__).parent

def read(name):
    return (P / name).read_text(encoding="utf-8").strip()

title = """# Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation: A RoboMaster Gimbal Case Study

**Draft v0.5.4** -- generated from verified simulation artifacts (2026-08-11). Real-robot section pending hardware (Section V).
"""

def _supplementary():
    """Figures + auto-generated speed-sweep table (if present)."""
    txt = """## Figures

- **Fig. 1**: `paper/figures/fig1_architecture.png` -- system architecture (shared detection/PnP -> proposed IMM estimator, online latency estimator, delay-aware MPC, firing decision; referee hit feedback).
- **Fig. 2**: `paper/figures/fig2_latency_chain.png` -- six-segment latency chain with per-segment magnitudes and online uncertainty estimate (mean +/- Delta_i) for firing tightening.
- **Fig. 3**: `sim/results_hitrate.png` -- hit rate by scenario / delay mode / controller (10 seeds).
- **Fig. 4**: `sim/results_ablations.png` -- ablation hit rates under the drift profile.
"""
    try:
        txt += "\n\n" + read("speed_sweep_section.md")
    except FileNotFoundError:
        pass
    try:
        txt += "\n\n" + read("dropout_section.md")
    except FileNotFoundError:
        pass
    try:
        txt += "\n\n" + read("delay_est_section.md")
    except FileNotFoundError:
        pass
    txt += """
## Data Availability

- Simulation code: `sim/` (Python, MIT-style).
- Per-seed raw results: `sim/results_raw.jsonl` (canonical, 2-model IMM); `sim/results_raw_v03_2model_imm.jsonl`, `sim/results_raw_v04_3model_imm.jsonl` (backups).
- Summary tables: `sim/results_summary.md`; real-time benchmark: `sim/rt_benchmark.json`.
- Real-robot latency tooling: `tools/delay_profiler/`.
- All research-plan artifacts and audit trail: `project/` (research-agent state machine).

## Acknowledged limits of this draft

- Literature citations are abstract/metadata-level except [R5][R6][R12] (full text); quantitative claims cited from [R7][R8] were re-verified against publisher metadata/abstracts on 2026-08-11 (full experimental protocols remain inaccessible).
- Simulation-only conclusions; real-robot validation is the planned next stage.
"""
    return txt

sections = [
    ("# Abstract", read("abstract.md")),
    ("# I. Introduction", read("introduction.md")),
    ("# II. Related Work", read("related_work.md")),
    ("# III. Method", read("method.md")),
    ("# IV. Simulation Study", read("simulation_section.md")),
    ("# V. Real-Robot Experiments", read("real_robot_section.md")),
    ("# VI. Discussion and Limitations", read("discussion_conclusion.md")),
    ("# References", read("references.md")),
    ("# Supplementary Material", _supplementary()),
]
parts = [title, "# Abstract\n\n" + read("abstract.md")]
for h, c in sections:
    if h == "# Abstract":
        continue
    parts.append(h + "\n\n" + c)
manuscript = "\n\n---\n\n".join(parts) + "\n"
(P / "manuscript.md").write_text(manuscript, encoding="utf-8")

# verify citation consistency
text = manuscript
refs = read("references.md")
used = set(re.findall(r"\[R(\d+)\]", text))
defined = set(re.findall(r"^\-\s*\*\*\[R(\d+)\]\*\*", refs, re.M))
assert used == defined, (used - defined, defined - used)
print(f"manuscript.md assembled: {len(manuscript)} chars; citations {len(used)} consistent")
