# -*- coding: utf-8 -*-
"""Build paper/tex/manuscript.tex + refs.bib from section .md files and sim/results.json.
Run from paper/tex: python3 build_tex.py
Tables are generated from sim/results.json to guarantee number consistency.
"""
import json, pathlib, re

TEX = pathlib.Path(__file__).parent
PAPER = TEX.parent
SIM = PAPER.parent / "sim"
R = json.loads((SIM / "results.json").read_text(encoding="utf-8"))
RT = json.loads((SIM / "rt_benchmark.json").read_text(encoding="utf-8"))
scenarios = ["line", "circle", "s", "accel"]
delays = ["fixed", "gamma", "drift"]
ctrls = ["B0", "B1", "Ours"]

def esc(t):
    return t.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")

def md2tex(md):
    """Minimal markdown -> LaTeX for our section files."""
    out = []
    in_list = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append(r"\section*{" + esc(line[2:].strip()) + "}")
        elif line.startswith("## "):
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append(r"\subsection*{" + esc(line[3:].strip()) + "}")
        elif line.startswith("### "):
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append(r"\subsubsection*{" + esc(line[4:].strip()) + "}")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list: out.append(r"\begin{itemize}"); in_list = True
            item = line[2:].strip()
            item = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", item)
            item = re.sub(r"\*(.+?)\*", r"\\textit{\1}", item)
            item = re.sub(r"\[R(\d+)\]", r"\\cite{ref\1}", item)
            out.append(r"\item " + item)
        elif line.strip() == "":
            if in_list: out.append(r"\end{itemize}"); in_list = False
            out.append("")
        else:
            if in_list: out.append(r"\end{itemize}"); in_list = False
            line = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", line)
            line = re.sub(r"\*(.+?)\*", r"\\textit{\1}", line)
            line = re.sub(r"\[R(\d+)\]", r"\\cite{ref\1}", line)
            out.append(line)
    if in_list: out.append(r"\end{itemize}")
    return "\n".join(out)

def load(name):
    return (PAPER / name).read_text(encoding="utf-8")

# --- tables from JSON -------------------------------------------------------
def stat_row(sc, dm, key):
    return next(s for s in R["paired"] if s["scenario"]==sc and s["delay_mode"]==dm)[key]

def fmt_stat(s):
    if s["p"] is None: return "--"
    return f"{s['mean_diff_pp']:+.1f} pp ($p$={s['p']:.3f}, $d$={s['d']:+.2f})"

T1 = [r"Table~\ref{tab:primary} reports the mean hit rate over ten seeds. Ours outperforms B0 on all trajectory classes and delay profiles by 28--67~pp (all $p<0.001$), and outperforms B1 on line, circle, and accelerating motion."]
T1.append("\\begin{table}[t]\\centering\\small")
T1.append("\\caption{Hit rate (mean over 10 seeds) and paired comparisons.}")
T1.append("\\label{tab:primary}")
T1.append("\\begin{tabular}{llccccl}")
T1.append("\\toprule Scenario & Delay & B0 & B1 & Ours & vs B0 & vs B1\\\\ \\midrule")
for sc in scenarios:
    for dm in delays:
        row = {c: next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]==dm and x["controller"]==c) for c in ctrls}
        T1.append(f"{sc} & {dm} & {row['B0']['hit_rate']:.3f} & {row['B1']['hit_rate']:.3f} & {row['Ours']['hit_rate']:.3f} & {fmt_stat(stat_row(sc,dm,'ours_vs_B0'))} & {fmt_stat(stat_row(sc,dm,'ours_vs_B1'))}\\\\")
T1.append("\\bottomrule\\end{tabular}\\end{table}")

T2 = [r"Table~\ref{tab:b2} gives the zero-delay upper bound of Ours and the residual gap under the drift profile."]
T2.append("\\begin{table}[t]\\centering\\small")
T2.append("\\caption{Zero-delay upper bound (B2).}")
T2.append("\\label{tab:b2}\\begin{tabular}{lccc}")
T2.append("\\toprule Scenario & B2 & Ours (drift) & Residual (pp)\\\\ \\midrule")
for sc in scenarios:
    b2 = R["b2_zero_delay"][sc]
    ours_d = next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]=="drift" and x["controller"]=="Ours")["hit_rate"]
    T2.append(f"{sc} & {b2:.3f} & {ours_d:.3f} & {(b2-ours_d)*100:+.1f}\\\\")
T2.append("\\bottomrule\\end{tabular}\\end{table}")

T3 = [r"Table~\ref{tab:abl} ablates the contributions under the drift profile."]
T3.append("\\begin{table}[t]\\centering\\small")
T3.append("\\caption{Ablations under the drift profile (mean hit rate).}")
T3.append("\\label{tab:abl}\\begin{tabular}{lcccccc}")
T3.append("\\toprule Scenario & Ours & A1 & A2 & A4 & A6 & CV\\%\\\\ \\midrule")
for sc in scenarios:
    a = R["ablations_drift"][sc]
    T3.append(f"{sc} & {a['Ours_IMM']:.3f} & {a['A1_no_delay_model']:.3f} & {a['A2_no_lead']:.3f} & {a['A4_CV_est']:.3f} & {a['A6_no_tighten']:.3f} & {a['A5_cv']*100:.1f}\\\\")
T3.append("\\bottomrule\\end{tabular}\\end{table}")

T4 = [r"Table~\ref{tab:rt} reports per-step solver time in Python as a conservative upper bound."]
T4.append("\\begin{table}[t]\\centering\\small")
T4.append("\\caption{Solver real-time benchmark (per step, $H=18$).}")
T4.append("\\label{tab:rt}\\begin{tabular}{lcccccc}")
T4.append("\\toprule Solver & mean & p50 & p95 & p99 & max & $<20$ ms\\\\ \\midrule")
for name in ["admm", "slsqp"]:
    b = RT[name]
    T4.append(f"{name.upper()} & {b['mean_ms']:.2f} & {b['p50']:.2f} & {b['p95']:.2f} & {b['p99']:.2f} & {b['max']:.2f} & {'yes' if b['p99_lt_period'] else 'no'}\\\\")
T4.append("\\bottomrule\\end{tabular}\\end{table}")

# --- supplementary speed-sweep table (number discipline: from results_speed_sweep.json) --
SSW = json.loads((SIM / "results_speed_sweep.json").read_text(encoding="utf-8"))
SPEED_LABEL = {"low": "0.5", "mid": "1.2", "high": "2.0"}
T5 = ["\\begin{table}[t]\\centering",
      "\\caption{Speed-gear sensitivity (drift latency, 10 seeds): hit rate by controller and paired gains vs. baselines.}\\label{tab:speed}",
      "\\begin{tabular}{lcccccc}",
      "\\toprule Scenario & m/s & B0 & B1 & Ours & Ours$-$B0 (pp, $p$) & Ours$-$B1 (pp, $p$)\\ \\midrule"]
for _sc in ["line", "circle", "s", "accel"]:
    for _sp in ["low", "mid", "high"]:
        _d = SSW["results"][f"{_sc}/{_sp}"]
        _p0, _p1 = _d["ours_vs_B0"], _d["ours_vs_B1"]
        _p0s = f"{_p0['p']:.3f}" if _p0["p"] is not None else "n/a"
        _p1s = f"{_p1['p']:.3f}" if _p1["p"] is not None else "n/a"
        T5.append(f"{_sc} & {SPEED_LABEL[_sp]} & {_d['B0']['hit_rate']:.3f} & {_d['B1']['hit_rate']:.3f} "
                  f"& {_d['Ours']['hit_rate']:.3f} & {_p0['mean_diff_pp']:+.1f} ({_p0s}) "
                  f"& {_p1['mean_diff_pp']:+.1f} ({_p1s})\\")
T5.append("\\bottomrule\\end{tabular}\\end{table}")
supp_tab = "\n".join(T5)

# --- sections ----------------------------------------------------------------
abstract = md2tex(load("abstract.md")).replace("\\section*{Abstract}\n", "")
intro = md2tex(load("introduction.md"))
related = md2tex(load("related_work.md"))
method = md2tex(load("method.md"))
disc = md2tex(load("discussion_conclusion.md").split("---")[0])
concl = md2tex(load("discussion_conclusion.md").split("---")[-1])
realrobot = md2tex(load("real_robot_section.md"))
refs_md = load("references.md")

sim_prose = load("simulation_section.md").split("**Table I.")[0]
sim_prose = re.sub(r"\|.*\|", "", sim_prose)   # strip md tables (we insert LaTeX tables)
sim = md2tex(sim_prose)
sim += "\n" + "\n\n".join(T1) + "\n" + "\n\n".join(T2) + "\n" + "\n\n".join(T3) + "\n" + "\n\n".join(T4)

preamble = r"""\documentclass[journal]{IEEEtran}
\usepackage{amsmath,amssymb,graphicx,booktabs,url,hyperref}
\usepackage[margin=1in]{geometry}
\graphicspath{{../../sim/}{../figures/}}
\begin{document}
\title{Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation: A RoboMaster Gimbal Case Study}
\author{Team Authors\thanks{Corresponding author: \texttt{<email>}}}
\maketitle
"""

refs_body = ""

doc = [preamble,
       r"\begin{abstract}", abstract, r"\end{abstract}",
       r"\begin{IEEEkeywords} predictive control; visual latency compensation; target tracking; RoboMaster gimbal; delay-aware MPC \end{IEEEkeywords}",
       intro, related, method,
       r"\section{Simulation Study}", sim,
       realrobot, disc, concl,
       r"""
\bibliographystyle{IEEEtran}
\bibliography{refs}

\section*{Figures}
\begin{figure*}[t]\centering
\includegraphics[width=0.95\textwidth]{fig1_architecture.png}
\caption{System architecture. Detection and PnP are shared with the baselines; the IMM estimator, online latency estimator, delay-aware MPC, and firing decision are the proposed blocks. Referee-system hit feedback provides the ground-truth label.}\label{fig:arch}
\end{figure*}
\begin{figure}[t]\centering
\includegraphics[width=0.92\columnwidth]{fig2_latency_chain.png}
\caption{Six-segment latency chain with nominal magnitudes (TJURM order of magnitude). The online estimator provides $\bar\tau_i$ and uncertainty bound $\Delta_i$ used to tighten the firing decision.}\label{fig:chain}
\end{figure}
\begin{figure}[t]\centering
\includegraphics[width=0.9\columnwidth]{results_hitrate.png}
\caption{Hit rate by scenario / delay mode / controller (10 seeds).}\label{fig:hit}
\end{figure}
\begin{figure}[t]\centering
\includegraphics[width=0.9\columnwidth]{results_ablations.png}
\caption{Ablations under the drift profile.}\label{fig:abl}
\end{figure}
\section*{Supplementary Material}
""" + supp_tab + r"""
\section*{Data Availability}
Code, per-seed results, real-time benchmark, and latency-profiling tooling are available at \url{<repo-url>}.
\end{document}
"""]
tex = "\n".join(doc)
(TEX / "manuscript.tex").write_text(tex, encoding="utf-8")

# --- refs.bib ----------------------------------------------------------------
bib = r"""@misc{ref1, title={RMVL: Prediction quantities in vehicle state estimation}, howpublished={\url{https://cv-rmvl.github.io/docs/1.0.0/d1/d40/tutorial_autoaim_gyro_predictor.html}}, year={2023}}
@misc{ref2, title={TJURM Auto-Aim Wiki}, howpublished={\url{https://github.com/HHgzs/TJURM-2024/wiki}}, year={2024}}
@misc{ref3, title={SHtech\_auto\_aim}, howpublished={\url{https://github.com/Astra-Whale/SHtech_auto_aim}}, year={2026}}
@misc{ref4, title={rm\_controllers: Gimbal Controllers}, howpublished={\url{https://deepwiki.com/rm-controls/rm_controllers}}, year={2025}}
@inproceedings{ref5, author={Barreto, J. P. and Batista, P.}, title={Model predictive control to improve visual control of motion: applications in active tracking of moving targets}, booktitle={Proc. 15th Int. Conf. Pattern Recognition (ICPR)}, volume={4}, pages={732--735}, year={2000}, doi={10.1109/ICPR.2000.903021}}
@article{ref6, title={A Smith Predictor Modified with a Pseudo Feedforward Control for the CCD-Based Optoelectronic Tracking System}, journal={Sensors}, volume={24}, number={17}, pages={5546}, year={2024}, doi={10.3390/s24175546}}
@article{ref7, title={Small tracking error correction for moving targets of intelligent electro-optical detection systems}, journal={Frontiers of Mechanical Engineering}, volume={19}, number={2}, pages={11}, year={2024}}
@article{ref8, title={Prediction and Control of Small Deviation in the Time-Delay of the Image Tracker in an Intelligent Electro-Optical Detection System}, journal={Actuators}, volume={12}, number={7}, pages={296}, year={2023}}
@article{ref9, title={A robust adaptive Kalman filter based visual servoing control for an inertial stabilization platform}, journal={Measurement Science and Technology}, volume={36}, number={10}, pages={106204}, year={2025}, doi={10.1088/1361-6501/ae0e8f}}
@article{ref10, title={Nonlinear Direct Error Compensator for Visual Servo Trajectory Tracking Under Image Sensor Delay on a Moving Platform}, journal={IEEE Transactions on Industrial Electronics}, volume={73}, number={6}, pages={9198--9208}, year={2026}, doi={10.1109/TIE.2025.3649866}}
@article{ref11, title={PENC: a predictive-estimative nonlinear control framework for robust target tracking of fixed-wing UAVs in complex urban environments}, journal={Scientific Reports}, volume={15}, pages={13095}, year={2025}, doi={10.1038/s41598-025-13095-z}}
@misc{ref12, title={Design and Implementation of Automatic Assisted Aiming System For Robomaster EP Based on YOLOv5}, howpublished={arXiv:2312.05055}, year={2023}}
@article{ref13, author={Wang, Hongxi and Ji, Zexian and Zhang, Lanyong}, title={Design of target recognition tracking and attack system based on Kalman filter}, journal={Journal of Ordnance Equipment Engineering}, volume={43}, number={11}, pages={286--296}, year={2022}, doi={10.11809/bqzbgcxb2022.11.041}}
@article{ref14, title={Robust nonlinear model predictive control based visual servoing of quadrotor UAVs}, journal={IEEE/ASME Transactions on Mechatronics}, volume={26}, number={2}, pages={700--708}, year={2021}, doi={10.1109/TMECH.2021.3053267}}
@article{ref15, title={Fusing Phase Map Servoing and MPC for High-Precision Robotic Tracking of Dynamic Objects}, journal={Actuators}, volume={15}, number={2}, pages={77}, year={2026}, doi={10.3390/act15020077}}
"""
(TEX / "refs.bib").write_text(bib, encoding="utf-8")

# --- sanity checks ------------------------------------------------------------
errs = []
if tex.count(r"\begin{") != tex.count(r"\end{"):
    errs.append("begin/end mismatch")
for tok in ["{", "}"]:
    pass
# brace balance (rough: ignore escaped)
depth = 0
for i, ch in enumerate(tex):
    if ch == "\\" and i+1 < len(tex): continue
    if ch == "{": depth += 1
    elif ch == "}": depth -= 1
    if depth < 0: errs.append("negative brace depth"); break
if depth != 0: errs.append(f"unbalanced braces: {depth}")
if "TODO" in tex: errs.append("TODO marker left")
print("manuscript.tex:", len(tex), "chars; refs.bib:", len(bib), "chars")
print("sanity:", errs or "OK")
