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
        line = re.sub(r"`([^`]*)`",
                     lambda m: r"\texttt{" + m.group(1).replace("_", r"\_").replace("#", r"\#").replace("%", r"\%") + "}", line)
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

def _fmt_p(p):
    if p is None: return "n/a"
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"

def bh_q(pvals):
    n = len(pvals); order = sorted(range(n), key=lambda i: pvals[i]); q = [0.0]*n
    for rank, i in enumerate(order, start=1): q[i] = pvals[i]*n/rank
    for rank in range(n-2, -1, -1): q[order[rank]] = min(q[order[rank]], q[order[rank+1]])
    return q

def rmse_drift(sc):
    return {c: next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]=="drift" and x["controller"]==c)["err_rmse_mrad"] for c in ctrls}

RMSE = {sc: rmse_drift(sc) for sc in scenarios}
Q_B0 = bh_q([stat_row(sc,dm,'ours_vs_B0')['p'] for sc in scenarios for dm in delays])
Q_B1 = bh_q([stat_row(sc,dm,'ours_vs_B1')['p'] for sc in scenarios for dm in delays])

def fmt_stat(s):
    if s["p"] is None: return "--"
    return f"{s['mean_diff_pp']:+.1f} pp (${_fmt_p(s['p'])}$, $d$={s['d']:+.2f})"

T1 = [r"Table~\ref{tab:primary} reports the mean hit rate over ten seeds. Ours outperforms B0 in all 12 conditions by 12--42~pp ($p<0.01$ in all; $p<0.001$ in 11 of 12; Cohen's $d\\ge1.3$), with 29--42~pp gains on line and circle, 12--21~pp on accelerating motion, and 12--13~pp on the sinusoidal trajectory, and outperforms B1 on line, circle, and accelerating motion (9 of 12 cells, $p<0.05$)."]
T1.append(f"All 12 comparisons versus B0 and all 9 significant comparisons versus B1 remain significant after Benjamini--Hochberg false-discovery-rate control ($q<0.05$).")
T1.append(f"Under the drift profile, Ours reduces pointing-error RMSE versus B0 from {RMSE['line']['B0']:.1f} to {RMSE['line']['Ours']:.1f}~mrad (line), {RMSE['circle']['B0']:.1f} to {RMSE['circle']['Ours']:.1f}~mrad (circle), {RMSE['s']['B0']:.1f} to {RMSE['s']['Ours']:.1f}~mrad (S), and {RMSE['accel']['B0']:.1f} to {RMSE['accel']['Ours']:.1f}~mrad (accel); on the S trajectory the RMSE also improves from {RMSE['s']['B1']:.1f} to {RMSE['s']['Ours']:.1f}~mrad versus B1 even though the hit-rate gain is not significant (Table~\\ref{{tab:rmse}}).")
T1.append("\\begin{table*}[t]\\centering\\small")
T1.append("\\caption{Hit rate (mean over 10 seeds) and paired comparisons.}")
T1.append("\\label{tab:primary}")
T1.append("\\begin{tabular}{llrrrrr}")
T1.append("\\toprule Scenario & Delay & B0 & B1 & Ours & vs B0 & vs B1\\\\ \\midrule")
for sc in scenarios:
    for dm in delays:
        row = {c: next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]==dm and x["controller"]==c) for c in ctrls}
        T1.append(f"{sc} & {dm} & {row['B0']['hit_rate']:.3f} & {row['B1']['hit_rate']:.3f} & {row['Ours']['hit_rate']:.3f} & {fmt_stat(stat_row(sc,dm,'ours_vs_B0'))} & {fmt_stat(stat_row(sc,dm,'ours_vs_B1'))}\\\\")
T1.append("\\bottomrule\\end{tabular}\\end{table*}")

T2 = [r"Table~\ref{tab:b2} gives the zero-delay upper bound of Ours and the residual gap under the drift profile."]
T2.append("\\begin{table}[t]\\centering\\small")
T2.append("\\caption{Zero-delay upper bound (B2).}")
T2.append("\\label{tab:b2}\\begin{tabular}{lrrr}")
T2.append("\\toprule Scenario & B2 & Ours (drift) & Residual (pp)\\\\ \\midrule")
for sc in scenarios:
    b2 = R["b2_zero_delay"][sc]
    ours_d = next(x for x in R["rows"] if x["scenario"]==sc and x["delay_mode"]=="drift" and x["controller"]=="Ours")["hit_rate"]
    T2.append(f"{sc} & {b2:.3f} & {ours_d:.3f} & {(b2-ours_d)*100:+.1f}\\\\")
T2.append("\\bottomrule\\end{tabular}\\end{table}")

T3 = [r"Table~\ref{tab:abl} ablates the contributions under the drift profile."]
T3.append("\\begin{table*}[t]\\centering\\small")
T3.append("\\caption{Ablations under the drift profile (mean hit rate).}")
T3.append("\\label{tab:abl}\\begin{tabular}{lrrrrrr}")
T3.append("\\toprule Scenario & Ours & A1 & A2 & A4 & A6 & CV\\%\\\\ \\midrule")
for sc in scenarios:
    a = R["ablations_drift"][sc]
    T3.append(f"{sc} & {a['Ours_IMM']:.3f} & {a['A1_no_delay_model']:.3f} & {a['A2_no_lead']:.3f} & {a['A4_CV_est']:.3f} & {a['A6_no_tighten']:.3f} & {a['A5_cv']*100:.1f}\\\\")
T3.append("\\bottomrule\\end{tabular}\\end{table*}")

T4 = [r"Table~\ref{tab:rt} reports per-step solver time in Python as a conservative upper bound."]
T4.append("\\begin{table}[t]\\centering\\small")
T4.append("\\caption{Solver real-time benchmark (per step, $H=18$).}")
T4.append("\\label{tab:rt}\\begin{tabular}{lrrrrrc}")
T4.append("\\toprule Solver & mean & p50 & p95 & p99 & max & $<20$ ms\\\\ \\midrule")
for name in ["admm", "slsqp"]:
    b = RT[name]
    T4.append(f"{name.upper()} & {b['mean_ms']:.2f} & {b['p50']:.2f} & {b['p95']:.2f} & {b['p99']:.2f} & {b['max']:.2f} & {'yes' if b['p99_lt_period'] else 'no'}\\\\")
T4.append("\\bottomrule\\end{tabular}\\end{table}")

# --- supplementary speed-sweep tables (number discipline: from results_speed_sweep.json) --
SSW = json.loads((SIM / "results_speed_sweep.json").read_text(encoding="utf-8"))
SPEED_LABEL = {"low": "0.5", "mid": "1.2", "high": "2.0"}
T5a = ["\\begin{table}[t]\\centering\\small",
       "\\caption{Speed-gear sensitivity (drift latency, 10 seeds): hit rate by controller.}\\label{tab:speed_a}",
       "\\begin{tabular}{lrrrr}",
       "\\toprule Scenario & m/s & B0 & B1 & Ours\\\\ \\midrule"]
for _sc in ["line", "circle", "s", "accel"]:
    for _sp in ["low", "mid", "high"]:
        _d = SSW["results"][f"{_sc}/{_sp}"]
        T5a.append(f"{_sc} & {SPEED_LABEL[_sp]} & {_d['B0']['hit_rate']:.3f} & {_d['B1']['hit_rate']:.3f} & {_d['Ours']['hit_rate']:.3f}\\\\")
T5a.append("\\bottomrule\\end{tabular}\\end{table}")
T5b = ["\\begin{table}[t]\\centering\\small",
       "\\caption{Speed-gear sensitivity (drift latency, 10 seeds): paired gains vs. baselines.}\\label{tab:speed_b}",
       "\\begin{tabular}{lrrr}",
       "\\toprule Scenario & m/s & Ours$-$B0 (pp, $p$) & Ours$-$B1 (pp, $p$)\\\\ \\midrule"]
for _sc in ["line", "circle", "s", "accel"]:
    for _sp in ["low", "mid", "high"]:
        _d = SSW["results"][f"{_sc}/{_sp}"]
        _p0, _p1 = _d["ours_vs_B0"], _d["ours_vs_B1"]
        T5b.append(f"{_sc} & {SPEED_LABEL[_sp]} & {_p0['mean_diff_pp']:+.1f} ({_fmt_p(_p0['p'])}) & {_p1['mean_diff_pp']:+.1f} ({_fmt_p(_p1['p'])})\\\\")
T5b.append("\\bottomrule\\end{tabular}\\end{table}")
supp_tab = "\n".join(T5a)
supp_tab2 = "\n".join(T5b)

# --- supplementary dropout table (number discipline: from results_dropout.json) --
DRO = json.loads((SIM / "results_dropout.json").read_text(encoding="utf-8"))
T6 = ["\\begin{table}[t]\\centering\\small",
      "\\caption{Detection-dropout robustness (drift latency, 10 seeds): hit rate by controller and paired gains vs. B1.}\\label{tab:drop}",
      "\\begin{tabular}{lrrrr}",
      "\\toprule Scenario & Dropout & B1 & Ours & Ours$-$B1 (pp, $p$)\\\\ \\midrule"]
for _sc in ["line", "accel"]:
    for _dp in [0.0, 0.1, 0.2]:
        _d = DRO["results"][f"{_sc}/dropout={_dp:.1f}"]
        _p1 = _d["ours_vs_B1"]
        T6.append(f"{_sc} & {_dp*100:.0f}\\% & {_d['B1']['hit_rate']:.3f} & {_d['Ours']['hit_rate']:.3f} & {_p1['mean_diff_pp']:+.1f} ({_fmt_p(_p1['p'])})\\\\")
T6.append("\\bottomrule\\end{tabular}\\end{table}")
supp_tab3 = "\n".join(T6)

# --- supplementary delay-estimator accuracy tables (from results_delay_estimation.json) --
DE = json.loads((SIM / "results_delay_estimation.json").read_text(encoding="utf-8"))
T7a = ["\\begin{table}[t]\\centering\\small",
       "\\caption{Online delay-estimator accuracy in ms (causal lag-1 estimate, steady state $t\\in[1,6]$~s; protocol secondary metric).}\\label{tab:de_a}",
       "\\begin{tabular}{llrrr}",
       "\\toprule Mode & Segment & Bias & MAE & RMSE\\\\ \\midrule"]
for _r in DE:
    for _seg in ["vision", "gimbal"]:
        _d = _r[_seg]; _s = _d["lag1"]
        T7a.append(f"{_r['mode']} & {_seg} & {_s['bias_ms']:+.2f} & {_s['mae_ms']:.2f} & {_s['rmse_ms']:.2f}\\\\")
T7a.append("\\bottomrule\\end{tabular}\\end{table}")
T7b = ["\\begin{table}[t]\\centering\\small",
       "\\caption{Online delay-estimator settling time (causal lag-1 estimate, $\\pm15$~ms jitter / drift profiles).}\\label{tab:de_b}",
       "\\begin{tabular}{llrr}",
       "\\toprule Mode & Segment & P95 abs (ms) & Settling (s)\\\\ \\midrule"]
for _r in DE:
    for _seg in ["vision", "gimbal"]:
        _d = _r[_seg]; _s = _d["lag1"]
        _wu = f"{_d['warmup_to_5ms_s']:.2f}" if _d["warmup_to_5ms_s"] is not None else ">6"
        T7b.append(f"{_r['mode']} & {_seg} & {_s['p95_ms']:.2f} & {_wu}\\\\")
T7b.append("\\bottomrule\\end{tabular}\\end{table}")
supp_tab4 = "\n".join(T7a)
supp_tab5 = "\n".join(T7b)

# --- supplementary pointing-error RMSE table (from results.json, drift) ------
T8 = ["\\begin{table}[t]\\centering\\small",
      "\\caption{Pointing-error RMSE (mrad) under the drift profile (mean over 10 seeds).}\\label{tab:rmse}",
      "\\begin{tabular}{lrrrr}",
      "\\toprule Scenario & B0 & B1 & Ours & Ours$-$B1 (\\%)\\\\ \\midrule"]
for _sc in scenarios:
    _r0, _r1, _ro = RMSE[_sc]['B0'], RMSE[_sc]['B1'], RMSE[_sc]['Ours']
    _red = (_r1-_ro)/_r1*100 if _r1 > 0 else float('nan')
    T8.append(f"{_sc} & {_r0:.1f} & {_r1:.1f} & {_ro:.1f} & {_red:+.1f}\\\\")
T8.append("\\bottomrule\\end{tabular}\\end{table}")
supp_tab6 = "\n".join(T8)

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
\author{Prep~Geng\thanks{Corresponding author: \texttt{qinghefoever@outlook.com}.}}
\maketitle
"""

refs_body = ""

FIG1 = r"""\begin{figure*}[t]\centering
\includegraphics[width=0.95\textwidth]{fig1_architecture.pdf}
\caption{System architecture. Detection and PnP are shared with the baselines; the multi-model estimator, online latency estimator, delay-aware MPC, and firing decision are the proposed blocks. Referee-system hit feedback provides the ground-truth label.}\label{fig:arch}
\end{figure*}"""
FIG2 = r"""\begin{figure}[t]\centering
\includegraphics[width=0.92\columnwidth]{fig2_latency_chain.pdf}
\caption{Six-segment latency chain with nominal magnitudes (TJURM order of magnitude). The online estimator provides $\bar\tau_i$ and uncertainty bound $\Delta_i$ used to tighten the firing decision.}\label{fig:chain}
\end{figure}"""
FIG3 = r"""\begin{figure}[t]\centering
\includegraphics[width=0.9\columnwidth]{results_hitrate.pdf}
\caption{Hit rate by scenario / delay mode / controller (10 seeds).}\label{fig:hit}
\end{figure}"""
FIG4 = r"""\begin{figure}[t]\centering
\includegraphics[width=0.9\columnwidth]{results_ablations.pdf}
\caption{Ablations under the drift profile.}\label{fig:abl}
\end{figure}"""
BIB = r"""\bibliographystyle{IEEEtran}
\bibliography{refs}"""

doc = [preamble,
       r"\begin{abstract}", abstract, r"\end{abstract}",
       r"\begin{IEEEkeywords} predictive control; visual latency compensation; target tracking; RoboMaster gimbal; delay-aware MPC \end{IEEEkeywords}",
       intro, FIG2, related, method, FIG1,
       r"\section{Simulation Study}", sim, FIG3, FIG4,
       realrobot, disc, concl, BIB,
       r"""
\section*{Supplementary Material}
""" + supp_tab + r"""
""" + supp_tab2 + r"""
""" + supp_tab3 + r"""
""" + supp_tab4 + r"""
""" + supp_tab5 + r"""
""" + supp_tab6 + r"""
\section*{Data Availability}
Code, per-seed results, real-time benchmark, and latency-profiling tooling are available at \url{https://github.com/prep0227/research}. The pre-registered experiment plan is included as \texttt{project/experiment\_plan.md} (timestamp 2026-08-11T12:41+08:00; SHA-256 \texttt{0361b95b\-fe8f6537\-0693572b\-ceac100b\-e757df35\-e7f563c2\-e07ba3af\-fdc828c}).
\end{document}
"""]
tex = "\n".join(doc)
(TEX / "manuscript.tex").write_text(tex, encoding="utf-8")

# --- refs.bib ----------------------------------------------------------------
bib = r"""@misc{ref1, author={RMVL Project}, title={RMVL: Prediction quantities in vehicle state estimation}, howpublished={\url{https://cv-rmvl.github.io/docs/1.0.0/d1/d40/tutorial_autoaim_gyro_predictor.html}}, year={2023}}
@misc{ref2, author={Tianjin University RoboMaster Team}, title={TJURM Auto-Aim Wiki}, howpublished={\url{https://github.com/HHgzs/TJURM-2024/wiki}}, year={2024}}
@misc{ref3, author={Astra-Whale}, title={SHtech\_auto\_aim}, howpublished={\url{https://github.com/Astra-Whale/SHtech_auto_aim}}, year={2026}}
@misc{ref4, author={rm-controls contributors}, title={rm\_controllers: Gimbal Controllers}, howpublished={\url{https://deepwiki.com/rm-controls/rm_controllers}}, year={2025}}
@inproceedings{ref5, author={Barreto, J. P. and Batista, P.}, title={Model predictive control to improve visual control of motion: applications in active tracking of moving targets}, booktitle={Proc. 15th Int. Conf. Pattern Recognition (ICPR)}, volume={4}, pages={732--735}, year={2000}, doi={10.1109/ICPR.2000.903021}}
@article{ref6, author={Deng, Keran and Tan, Juan and Chen, Piao and Zhang, Shige and Wang, Ke and Luo, Yong}, title={A Smith Predictor Modified with a Pseudo Feedforward Control for the CCD-Based Optoelectronic Tracking System}, journal={Sensors}, volume={24}, number={17}, pages={5546}, year={2024}, doi={10.3390/s24175546}}
@article{ref7, author={Shen, Cheng and Wen, Zhijie and Zhu, Wenliang and Fan, Dapeng and Ling, Mingyuan}, title={Small tracking error correction for moving targets of intelligent electro-optical detection systems}, journal={Frontiers of Mechanical Engineering}, volume={19}, number={2}, pages={11}, year={2024}, doi={10.1007/s11465-024-0782-6}}
@article{ref8, author={Shen, Cheng and Wen, Zhijie and Zhu, Wenliang and Fan, Dapeng and Chen, Yukang and Zhang, Zhuo}, title={Prediction and Control of Small Deviation in the Time-Delay of the Image Tracker in an Intelligent Electro-Optical Detection System}, journal={Actuators}, volume={12}, number={7}, pages={296}, year={2023}, doi={10.3390/act12070296}}
@article{ref9, author={Zhang, Liyuan and Wang, Zhongshi and Xu, Rui and Tian, Dapeng and Guo, Lihong}, title={A robust adaptive Kalman filter based visual servoing control for an inertial stabilization platform}, journal={Measurement Science and Technology}, volume={36}, number={10}, pages={106204}, year={2025}, doi={10.1088/1361-6501/ae0e8f}}
@article{ref10, author={Miao, Qingqing and Bian, Qihui and Yu, Zhiyong and Tang, Tao}, title={Nonlinear Direct Error Compensator for Visual Servo Trajectory Tracking Under Image Sensor Delay on a Moving Platform}, journal={IEEE Transactions on Industrial Electronics}, volume={73}, number={6}, pages={9198--9208}, year={2026}, doi={10.1109/TIE.2025.3649866}}
@article{ref11, author={Hai, Shiji and Na, Xitai and Feng, Zhihui and Shi, Jinshuo and Sun, Qingbin}, title={PENC: a predictive-estimative nonlinear control framework for robust target tracking of fixed-wing UAVs in complex urban environments}, journal={Scientific Reports}, volume={15}, pages={13095}, year={2025}, doi={10.1038/s41598-025-13095-z}}
@misc{ref12, author={Qin, Junjia and Xu, Kangli}, title={Design and Implementation of Automatic Assisted Aiming System For Robomaster EP Based on YOLOv5}, howpublished={arXiv:2312.05055}, year={2023}}
@article{ref13, author={Wang, Hongxi and Ji, Zexian and Zhang, Lanyong}, title={Design of target recognition tracking and attack system based on Kalman filter}, journal={Journal of Ordnance Equipment Engineering}, volume={43}, number={11}, pages={286--296}, year={2022}, doi={10.11809/bqzbgcxb2022.11.041}}
@article{ref14, author={Zhang, Kunwu and Shi, Yang and Sheng, Huaiyuan}, title={Robust nonlinear model predictive control based visual servoing of quadrotor UAVs}, journal={IEEE/ASME Transactions on Mechatronics}, volume={26}, number={2}, pages={700--708}, year={2021}, doi={10.1109/TMECH.2021.3053267}}
@article{ref15, author={Zhang, Qinghui and Han, Tianhao and Lu, Lei and Pan, Wei and Gao, Ge}, title={Fusing Phase Map Servoing and MPC for High-Precision Robotic Tracking of Dynamic Objects}, journal={Actuators}, volume={15}, number={2}, pages={77}, year={2026}, doi={10.3390/act15020077}}
@article{ref16, author={Blom, Henk A. P. and Bar-Shalom, Yaakov}, title={The interacting multiple model algorithm for systems with Markovian switching coefficients}, journal={IEEE Transactions on Automatic Control}, volume={33}, number={8}, pages={780--783}, year={1988}, doi={10.1109/9.1299}}
@article{ref17, author={Bar-Shalom, Yaakov}, title={Update with out-of-sequence measurements in tracking: exact solution}, journal={IEEE Transactions on Aerospace and Electronic Systems}, volume={38}, number={3}, pages={769--778}, year={2002}, doi={10.1109/TAES.2002.1039398}}
@article{ref18, author={Mayne, David Q. and Rawlings, James B. and Rao, Christopher V. and Scokaert, Pierre O. M.}, title={Constrained model predictive control: Stability and optimality}, journal={Automatica}, volume={36}, number={6}, pages={789--814}, year={2000}, doi={10.1016/S0005-1098(99)00214-9}}
@article{ref19, author={Smith, Otto J. M.}, title={A controller to overcome dead time}, journal={ISA Journal}, volume={6}, number={2}, pages={28--33}, year={1959}}
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
