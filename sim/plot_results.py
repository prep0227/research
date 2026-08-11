"""Generate paper figures from results.json (v0.3)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    r = json.load(open("results.json"))
    rows = r["rows"]
    scenarios = ["line", "circle", "s", "accel"]
    delays = ["fixed", "gamma", "drift"]
    controllers = ["B0", "B1", "Ours"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
    colors = {"B0": "#bbbbbb", "B1": "#88bbee", "Ours": "#cc3333"}
    for ax, sc in zip(axes.ravel(), scenarios):
        x = np.arange(len(delays)); w = 0.26
        for i, c in enumerate(controllers):
            vals = [next(row["hit_rate"] for row in rows if row["scenario"]==sc and row["delay_mode"]==d and row["controller"]==c) for d in delays]
            ax.bar(x + (i-1)*w, vals, w, label=c, color=colors[c])
        ax.set_title(sc)
        ax.set_xticks(x); ax.set_xticklabels(delays)
        ax.set_ylim(0, 0.9)
    axes.ravel()[0].legend()
    fig.suptitle("Hit rate by scenario / delay mode / controller (10 seeds)")
    fig.tight_layout()
    fig.savefig("results_hitrate.png", dpi=150)
    # ablation figure
    ab = r["ablations_drift"]
    fig2, ax2 = plt.subplots(figsize=(9, 5))
    keys = ["Ours_IMM", "A1_no_delay_model", "A2_no_lead", "A4_CV_est", "A6_no_tighten"]
    x = np.arange(len(scenarios)); w = 0.15
    for i, k in enumerate(keys):
        vals = [ab[sc][k] for sc in scenarios]
        ax2.bar(x + (i-2.5)*w, vals, w, label=k)
    ax2.set_xticks(x); ax2.set_xticklabels(scenarios)
    ax2.set_ylabel("hit rate (drift mode)"); ax2.legend(fontsize=8)
    fig2.tight_layout(); fig2.savefig("results_ablations.png", dpi=150)
    print("figures written: results_hitrate.png, results_ablations.png")

if __name__ == "__main__":
    main()
