# Delay-Aware Predictive Control for Moving-Target Tracking with Explicit Vision-Latency Compensation (RoboMaster Gimbal Case Study)

Research repository for the project *视觉延迟补偿的移动目标跟踪预测控制（RoboMaster 云台自瞄为载体）*.

**Core idea**: RoboMaster gimbal auto-aim is systematically wrong because it aims at the *current* target position while a
multi-segment latency chain (camera exposure → detection → PnP → serial → gimbal rotation → firing → flight) delays every
measurement. This project models that latency chain as **time-varying and uncertain** ($\tau_i(t)=\bar\tau_i+\delta_i(t)$,
$|\delta_i|\le\Delta_i$), estimates it **online**, and embeds it in a **delay-aware MPC** with an IMM target estimator and an
ADMM box-constrained QP solver. Firing decisions are tightened by the estimated delay uncertainty.

## Repository layout

| Path | Contents |
|---|---|
| `sim/` | Reproducible simulation (canonical v0.3): IMM{CV,CT} + online delay estimator + ADMM QP; 520 runs × 10 seeds; A1–A6 ablations; B2 no-delay upper bound |
| `paper/` | Manuscript (English, v0.5) + IEEEtran LaTeX package (`tex/`), cover letter, journal selection, submission checklist |
| `project/` | Research-agent artifacts: research brief, evidence report (17 records), gap/novelty analysis, technical route, experiment protocol (real-robot v1.1), audit trail (34 events), state machine |
| `tools/delay_profiler/` | Real-robot latency profiling: timestamp instrumentation templates, `compute_latency_profile.py`, `latency_profile.yaml` |
| `deploy/cpp/` | Header-only C++17 ADMM MPC solver (`mpc_solver.hpp`) + unit test, for embedded/real-robot porting |

## Reproduce the simulation

```bash
pip install -r requirements.txt
cd sim
python3 run_experiments.py        # ~8 min, 520 runs, resumes from results_raw.jsonl
python3 plot_results.py           # regenerate figures
```

Key outputs: `sim/results.json` (all numbers used in the paper), `sim/results_summary.md`,
`sim/results_hitrate.png`, `sim/results_ablations.png`, `sim/rt_benchmark.json` (ADMM P99 ≈ 4.9 ms < 20 ms control period).

## Reproduce the manuscript

```bash
python3 paper/assemble_manuscript.py   # paper/manuscript.md (citation-consistency asserted)
python3 paper/tex/build_tex.py         # paper/tex/manuscript.tex + refs.bib (tables from results.json)
```

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs both checks plus a LaTeX compile
(`xu-cheng/latex-action`) so the paper is verifiably buildable without a local TeX installation.

## Real-robot protocol (next phase)

`project/experiment_protocol.md` (v1.1) preregisters: calibration → latency profiling (≥200 samples/segment) →
software delay-injection (fixed/gamma/drift, matching the simulator) → 3 controllers × 4 trajectory classes ×
N=300 shots × 3 rounds; primary test = paired one-sided McNemar; success = observed improvement ≥5 pp and p<0.05
(power analysis in `project/real_power_analysis.json`). `tools/delay_profiler/` is ready for hardware use.

## Publication plan

English journal (RA-L → JINT/CEP → Chinese core fallback), submission window 2026-09 to 2027-01
(see `paper/journal_selection.md` and `project/timeline_publication.md`).

## Status

Simulation, manuscript draft, submission package, and deployment tooling are complete. Real-robot validation is the
remaining phase (blocked on hardware + team availability).
