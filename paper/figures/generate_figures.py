#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Fig.1 (system architecture) and Fig.2 (latency chain) for the manuscript.

Includes a deterministic geometry self-check (text/patch bounding-box overlaps)
so layout issues are caught without visual inspection.
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

OUT = pathlib.Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.linewidth": 0.8})

def check_overlaps(fig, ax, label):
    """Geometric QA: report any text-text / text-patch overlaps (excluding a text
    whose center lies inside its own parent block)."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(renderer)) for t in ax.texts]
    patches = [(p, p.get_window_extent(renderer)) for p in ax.patches
               if isinstance(p, FancyBboxPatch)]
    problems = []
    for i, (t1, e1) in enumerate(texts):
        c1 = np.array([e1.x0 + e1.width / 2, e1.y0 + e1.height / 2])
        # parent patch = patch containing text center
        parent = None
        for p, e in patches:
            if e.contains(e1.x0 + e1.width/2, e1.y0 + e1.height/2):
                parent = e; break
        for j, (t2, e2) in enumerate(texts):
            if j <= i: continue
            if e1.overlaps(e2):
                problems.append(f"text-text overlap: '{t1.get_text()[:24]}' vs '{t2.get_text()[:24]}'")
        for p, e in patches:
            if parent is not None and e == parent: continue
            if e1.overlaps(e):
                problems.append(f"text-patch overlap: '{t1.get_text()[:24]}' with patch at ({p.get_x():.0f},{p.get_y():.0f})")
    if problems:
        print(f"[{label}] {len(problems)} potential layout issues:")
        for p in problems[:12]: print("   -", p)
    else:
        print(f"[{label}] geometry check OK")

# ---------------------------------------------------------------- Fig.1
def fig1():
    fig, ax = plt.subplots(figsize=(10.0, 3.6), dpi=300)
    ax.set_xlim(-9, 102); ax.set_ylim(-3.2, 34); ax.axis("off")

    shared = dict(boxstyle="round,pad=0.28", fc="#e8e8e8", ec="#555555", lw=0.9)
    ours   = dict(boxstyle="round,pad=0.28", fc="#cfe3f7", ec="#1f5fa8", lw=1.4)
    W, H = 13.0, 10.0
    top_y, bot_y = 21.0, 5.0
    # top row x: camera, detect, IMM, latency, MPC, firing
    top = [
        ("Industrial\ncamera", 1.0, shared),
        ("Detection\n+ PnP pose", 16.0, shared),
        ("IMM estimator\n(CV/CT, OOSM)", 31.0, ours),
        ("Online latency\nestimator", 46.0, ours),
        ("Delay-aware MPC\n(ADMM QP)", 61.0, ours),
        ("Firing\ndecision", 76.0, ours),
    ]
    # bottom row (snake: firing -> serial -> gimbal -> flight -> target)
    bot = [
        ("Target / referee\nhit detection", 31.0, shared),
        ("Projectile\nflight", 46.0, shared),
        ("Gimbal +\nlauncher", 61.0, shared),
        ("Serial\n+ MCU", 76.0, shared),
    ]
    blocks = []
    for name, x, sty in top:
        blocks.append((name, x, top_y, W, H, sty))
    for name, x, sty in bot:
        blocks.append((name, x, bot_y, W, H, sty))
    for name, x, y, w, h, sty in blocks:
        ax.add_patch(FancyBboxPatch((x, y), w, h, **sty))
        ax.text(x + w/2, y + h/2, name, ha="center", va="center", fontsize=8.4)

    def top_center(i):
        return top[i][1] + W/2, top_y + H
    def bot_center(i):
        return bot[i][1] + W/2, bot_y + H

    def arrow(p1, p2, color="black", lw=1.3, ls="-", style="-|>"):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13,
                                     color=color, lw=lw, linestyle=ls,
                                     shrinkA=0, shrinkB=0))
    # top row arrows (across the 2-unit gaps)
    for i in range(5):
        arrow((top[i][1] + W, top_y + H/2), (top[i+1][1], top_y + H/2))
    # firing -> serial (vertical drop, same x)
    fx = top[5][1] + W/2
    arrow((fx, top_y), (fx, bot_y + H))
    # serial -> gimbal -> flight -> target (right-to-left)
    for i in range(3, 0, -1):
        arrow((bot[i][1], bot_y + H/2), (bot[i-1][1] + W, bot_y + H/2))
    # measurement-timestamp feedback: detection bottom -> latency estimator bottom
    dtx = top[1][1] + W/2
    ltx = top[3][1] + W/2
    mid_y = (bot_y + H + top_y) / 2
    arrow((dtx, top_y), (dtx, mid_y), color="#b06500", lw=1.1, ls=(0, (4, 3)))
    arrow((dtx, mid_y), (ltx, mid_y), color="#b06500", lw=1.1, ls=(0, (4, 3)))
    arrow((ltx, mid_y), (ltx, top_y), color="#b06500", lw=1.1, ls=(0, (4, 3)))
    ax.text((dtx + ltx)/2, mid_y, "image timestamps (τ_meas)",
            ha="center", va="center", fontsize=7.4, color="#b06500")
    # legend (kept outside the block area, bottom-right corner)
    ax.add_patch(FancyBboxPatch((78, -3.0), 13, 5.5, boxstyle="round,pad=0.25", fc="#cfe3f7", ec="#1f5fa8", lw=1.0))
    ax.text(84.5, -0.25, "proposed", fontsize=7.6, ha="center", va="center")
    ax.add_patch(FancyBboxPatch((92, -3.0), 13, 5.5, boxstyle="round,pad=0.25", fc="#e8e8e8", ec="#555555", lw=0.9))
    ax.text(98.5, -0.25, "shared", fontsize=7.6, ha="center", va="center")

    check_overlaps(fig, ax, "fig1")
    fig.savefig(OUT / "fig1_architecture.png", dpi=600, bbox_inches="tight")
    fig.savefig(OUT / "fig1_architecture.pdf", bbox_inches="tight")
    plt.close(fig)
    print("fig1_architecture.png written")

# ---------------------------------------------------------------- Fig.2
def fig2():
    segs = [("τ_cam", "exposure/readout", 10, 5, 15, "#9ecae1"),
            ("τ_proc", "detection/PnP", 10, 5, 15, "#9ecae1"),
            ("τ_serial", "communication", 1, 0.5, 3, "#c6dbef"),
            ("τ_gimbal", "actuation", 110, 20, 200, "#fdae6b"),
            ("τ_fire", "firing", 75, 50, 100, "#fdae6b"),
            ("τ_flight", "projectile flight", 150, 50, 250, "#fc9272")]
    total = sum(s[2] for s in segs)  # 356 ms nominal
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.0, 4.6), dpi=300,
                                   gridspec_kw={"height_ratios": [1.1, 1.0], "hspace": 0.55})

    # Panel A: stacked proportional latency chain
    x0 = 0.0
    y0, h = 0.0, 0.9
    for name, desc, mean, lo, hi, c in segs:
        ax1.add_patch(Rectangle((x0, y0), mean, h, fc=c, ec="#333333", lw=0.7))
        ax1.plot([x0 + hi, x0 + hi], [y0 - 0.18, y0 + h + 0.18], color="#333333", lw=0.8)
        ax1.plot([x0 + hi - 1.8, x0 + hi + 1.8], [y0 + h + 0.18]*2, color="#333333", lw=0.8)
        x0 += mean
    ax1.plot([0, x0], [y0 - 0.18]*2, color="#333333", lw=0.8)
    ax1.text(x0, y0 + h + 0.5, f"nominal total ≈ {total} ms", ha="right", va="bottom", fontsize=8.2)
    ax1.text(2, y0 + h + 0.5, "six-segment latency chain (TJURM order of magnitude)",
             ha="left", va="bottom", fontsize=8.2)
    ax1.set_xlim(-6, 400); ax1.set_ylim(-0.7, 2.2)
    ax1.set_yticks([]); ax1.set_xticks([0, 100, 200, 300, 356, 400])
    ax1.set_xlabel("accumulated latency (ms)", fontsize=8.5)
    ax1.spines[["left", "top", "right"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, fc=c, ec="#333333") for _, _, _, _, _, c in segs]
    labels = [f"{n} ({d})" for n, d, *_ in segs]
    ax1.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 1.02), ncol=3,
               fontsize=7.4, frameon=False, handlelength=1.2, columnspacing=1.2)

    # Panel B: online estimate mean ± Δ (bar chart, evenly spaced categories)
    names = [s[0] for s in segs]
    means = [s[2] for s in segs]
    los, his = [s[3] for s in segs], [s[4] for s in segs]
    Delta = [max(m - lo, hi - m) for m, lo, hi in zip(means, los, his)]
    xs = np.arange(len(segs))
    ax2.bar(xs, means, 0.55, color=["#9ecae1", "#9ecae1", "#c6dbef", "#fdae6b", "#fdae6b", "#fc9272"],
            edgecolor="#333333", linewidth=0.7)
    ax2.errorbar(xs, means, yerr=Delta, fmt="none", ecolor="#333333", elinewidth=0.9, capsize=3)
    for xi, m in zip(xs, means):
        ax2.text(xi, m + 8, f"{m}", ha="center", va="bottom", fontsize=7.6)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([f"{n}\n±{int(round(d))}" for n, d in zip(names, Delta)], fontsize=7.4)
    ax2.set_ylabel("estimated delay (ms)", fontsize=8.5)
    ax2.set_ylim(0, 330)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", ls=":", lw=0.5, alpha=0.6)
    ax2.text(2.0, 315, "online estimator output:  $\\bar\\tau_i \\pm \\Delta_i$  → firing tightening",
             ha="center", va="top", fontsize=8.4, color="#1f5fa8")

    check_overlaps(fig, ax1, "fig2-panelA")
    check_overlaps(fig, ax2, "fig2-panelB")
    fig.savefig(OUT / "fig2_latency_chain.png", dpi=600, bbox_inches="tight")
    fig.savefig(OUT / "fig2_latency_chain.pdf", bbox_inches="tight")
    plt.close(fig)
    print("fig2_latency_chain.png written")

if __name__ == "__main__":
    fig1()
    fig2()
    print("PDF copies written to paper/figures/")
