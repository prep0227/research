"""Metrics: angular tracking error RMSE and hit-rate simulation."""
import numpy as np
from trajectories import az_el

def angular_error(gun_dir, target_azel):
    d = gun_dir - target_azel
    return np.linalg.norm(np.arctan2(np.sin(d), np.cos(d)))

def simulate_hits_detailed(shots, targets, gimbal_pos, tau_fire, tau_flight_fn,
                             rng=None, v_bullet=15.0, armor_half=0.08, dispersion=0.008):
    """Per-shot hit outcomes. shots: list of (t_fire, gun_dir[2]); targets: position(t) ground truth.
    rng: optional numpy Generator for reproducible dispersion noise (paired evaluation uses the
    SAME noise draws across controllers). Returns (outcomes, n_hits)."""
    outcomes = []
    n_hits = 0
    for t_f, gun in shots:
        t_impact = t_f + tau_fire + tau_flight_fn(t_f)
        true_pos = targets.position(t_impact)
        true_azel = az_el(true_pos, gimbal_pos)
        tol = np.arctan(armor_half / np.linalg.norm(true_pos - np.asarray(gimbal_pos)))
        noise = (rng.normal(0.0, dispersion, 2) if rng is not None
                 else np.random.normal(0.0, dispersion, 2))
        miss = angular_error(gun + noise, true_azel)
        hit = 1 if miss < tol else 0
        outcomes.append(hit)
        n_hits += hit
    return outcomes, n_hits

def simulate_hits(shots, targets, gimbal_pos, tau_fire, tau_flight_fn,
                  v_bullet=15.0, armor_half=0.08, dispersion=0.008):
    """shots: list of (t_fire, gun_dir[2]); targets: position(t) ground truth.
    Returns number of hits (global RNG dispersion)."""
    outcomes, n_hits = simulate_hits_detailed(shots, targets, gimbal_pos, tau_fire,
                                              tau_flight_fn, rng=None,
                                              v_bullet=v_bullet, armor_half=armor_half,
                                              dispersion=dispersion)
    return n_hits

def run_metrics(log, targets, gimbal_pos, tau_fire, tau_flight_fn):
    """log: list of dicts with t, gun_dir, target_azel_true; shots: list (t, gun_dir)."""
    errs = [angular_error(d["gun_dir"], d["target_azel_true"]) for d in log]
    shots = [d["shot"] for d in log if d["shot"] is not None]
    hits = simulate_hits(shots, targets, gimbal_pos, tau_fire, tau_flight_fn)
    n_shots = len(shots)
    return {
        "err_rmse": float(np.sqrt(np.mean(np.square(errs)))),
        "err_mean": float(np.mean(errs)),
        "err_p95": float(np.quantile(errs, 0.95)),
        "shots": n_shots,
        "hits": hits,
        "hit_rate": hits / n_shots if n_shots > 0 else 0.0,
    }
