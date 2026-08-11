"""Generate IEEE-style paper figures from results.json (v0.3).

Follows IEEE figure guidelines: >=300 dpi (we use 600), 8-10 pt fonts,
column-width sizing (3.5in single / 7.16in double), ~0.8 pt line width.
Also writes vector PDF copies to ../paper/figures/ for submission.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "lines.linewidth": 0.9,
})

COLORS = {"B0": "#8c8c8c", "B1": "#4C72B0", "Ours": "#C44E52"}
SCENARIOS = ["line", "circle", "s", "accel"]
DELAYS = ["fixed", "gamma", "drift"]
CONTROLLERS = ["B0", "B1", "Ours"]

def save(fig, name, outdir="."):
    fig.savefig(f"{outdir}/{name}.png", dpi=600, bbox_inches="tight")
    fig.savefig(f"{outdir}/{name}.pdf", bbox_inches="tight")
    print("wrote", name, "(png@600 + pdf)")

def main():
    r = json.load(open("results.json"))
    rows = r["rows"]

    # ---- Fig.3: hit rate by scenario / delay mode / controller (2x2, double-column) ----
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 5.0), sharey=True)
    for ax, sc in zip(axes.ravel(), SCENARIOS):
        x = np.arange(len(DELAYS)); w = 0.26
        for i, c in enumerate(CONTROLLERS):
            vals = [next(row["hit_rate"] for row in rows
                         if row["scenario"] == sc and row["delay_mode"] == d and row["controller"] == c)
                    for d in DELAYS]
            ax.bar(x + (i - 1) * w, vals, w, label=c, color=COLORS[c], edgecolor="black", linewidth=0.4)
        ax.set_title(sc)
        ax.set_xticks(x); ax.set_xticklabels(DELAYS)
        ax.set_ylim(0, 0.9)
        ax.grid(axis="y", ls=":", lw=0.4, alpha=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for ax in axes[:, 1]:
        ax.set_yticklabels([])
    axes[0, 0].set_ylabel("hit rate"); axes[1, 0].set_ylabel("hit rate")
    fig.legend(labels=CONTROLLERS, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "results_hitrate", outdir=".")

    # ---- Fig.4: ablations under drift (single-column) ----
    ab = r["ablations_drift"]
    keys = ["Ours_IMM", "A1_no_delay_model", "A2_no_lead", "A4_CV_est", "A6_no_tighten"]
    labels = ["Ours", "A1: no delay model", "A2: no lead", "A4: CV est.", "A6: no tighten"]
    colors = ["#C44E52", "#8c8c8c", "#8c8c8c", "#4C72B0", "#dd8452"]
    fig2, ax2 = plt.subplots(figsize=(3.5, 2.6))
    x = np.arange(len(SCENARIOS)); w = 0.15
    for i, (k, lab) in enumerate(zip(keys, labels)):
        vals = [ab[sc][k] for sc in SCENARIOS]
        ax2.bar(x + (i - 2) * w, vals, w, label=lab, color=colors[i], edgecolor="black", linewidth=0.4)
    ax2.set_xticks(x); ax2.set_xticklabels(SCENARIOS)
    ax2.set_ylabel("hit rate (drift)")
    ax2.set_ylim(0, 0.9)
    ax2.grid(axis="y", ls=":", lw=0.4, alpha=0.5)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.legend(frameon=False, fontsize=6.5, loc="upper right")
    fig2.tight_layout()
    save(fig2, "results_ablations", outdir=".")

if __name__ == "__main__":
    main()
