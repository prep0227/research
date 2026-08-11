"""Controllers: LeadCompPID (community baseline), PlainMPC, DelayAwareMPC.

All controllers share the same interface:
    reset()
    step(t, gimbal, estimator, fire_state) -> (u, fire_flag)
where fire_state carries shared fire bookkeeping (cooldown, shots left).
"""
import numpy as np
from scipy.optimize import minimize
from trajectories import az_el

# --- shared fire bookkeeping -------------------------------------------------
class FireState:
    def __init__(self, tau_fire=0.08, cooldown=0.2, ammo=100):
        self.tau_fire = tau_fire
        self.cooldown = cooldown
        self.ammo = ammo
        self.last_fire = -1e9
    def can_fire(self, t):
        return (t - self.last_fire >= self.cooldown) and (self.ammo > 0)
    def fire(self, t):
        self.last_fire = t; self.ammo -= 1

def desired_aim(t, estimator, tau_fire, tau_flight_fn, dt=0.02, gimbal_pos=(0,0,0.3)):
    """Aim point = az/el of predicted target at t + tau_fire + tau_flight(t)."""
    horizon = tau_fire + tau_flight_fn(t)
    pos = estimator.predict(horizon)
    return az_el(pos, gimbal_pos)

# --- baseline: lead-compensated PID ------------------------------------------
class LeadCompPID:
    name = "B0_LeadCompPID"
    def __init__(self, dt=0.02, kp=8.0, kd=1.5, kff=0.6, tau_fire=0.08, tau_flight_fn=None,
                 B=0.06, gimbal_pos=(0,0,0.3)):
        self.dt = dt; self.kp = kp; self.kd = kd; self.kff = kff
        self.tau_fire = tau_fire; self.tau_flight_fn = tau_flight_fn
        self.B = B; self.gimbal_pos = gimbal_pos
        self.e_prev = np.zeros(2)
    def reset(self): self.e_prev = np.zeros(2)
    def step(self, t, gimbal, estimator, fs):
        horizon = self.tau_fire + self.tau_flight_fn(t) + self.B
        pos = estimator.predict(horizon)
        aim = az_el(pos, self.gimbal_pos)
        cur = gimbal.pointing()
        e = aim - cur
        de = (e - self.e_prev) / self.dt
        u = self.kp * e + self.kd * de
        # feedforward: approximate desired angular velocity from predicted aim sequence
        pos2 = estimator.predict(horizon + self.dt)
        aim2 = az_el(pos2, self.gimbal_pos)
        ff = (aim2 - aim) / self.dt
        u = u + self.kff * ff
        self.e_prev = e
        fire = False
        if fs.can_fire(t) and np.linalg.norm(e) < hit_tolerance(t, self.tau_flight_fn):
            fire = True; fs.fire(t)
        return u, fire

# --- MPC (plain / delay-aware) ------------------------------------------------
class MPC:
    """v0.2 MPC: quadratic cost with analytic gradient, solved by SLSQP under
    accel (box) and accel-rate (slope) constraints. Supports time-varying input
    delay (d estimated online via DelayEstimator) and a no-lead ablation flag.
    """
    name = "MPC"
    def __init__(self, dt=0.02, H=30, d_steps=3, Q=None, R=None,
                 acc_max=10.0, rate_max=6.0, du_max=8.0,
                 tau_fire=0.08, tau_flight_fn=None, gimbal_pos=(0,0,0.3),
                 use_input_delay=True, delay_est=None, lead=True, max_d=10,
                 solver="admm", tighten=True):
        self.dt = dt; self.H = H; self.d_steps = int(d_steps)
        self.solver = solver
        self.tighten = tighten
        self._admm = ADMMSolver(rho=2.0, iters=60)
        self.Q = np.diag([200.0, 200.0]) if Q is None else np.asarray(Q, float)
        self.R = np.diag([0.1, 0.1]) if R is None else np.asarray(R, float)
        self.acc_max = acc_max; self.rate_max = rate_max; self.du_max = du_max
        self.tau_fire = tau_fire; self.tau_flight_fn = tau_flight_fn
        self.gimbal_pos = gimbal_pos
        self.use_input_delay = use_input_delay
        self.delay_est = delay_est
        self.lead = lead
        self.max_d = max_d
        self.u_prev = np.zeros(2)
        self.buf = []   # past controls actually sent
        self.u_last = None  # warm-start solution from previous step

    def reset(self):
        self.u_prev = np.zeros(2); self.buf = []; self.u_last = None

    def _current_d(self):
        if not self.use_input_delay:
            return 0
        if self.delay_est is not None:
            return int(round(self.delay_est.gimbal_mean() / self.dt))
        return self.d_steps

    def _build_prediction(self, g0):
        """Linear map: traj_flat = T @ u_flat + b; g0 = [yaw, yaw_rate, pitch, pitch_rate]."""
        dt = self.dt; H = self.H; d = self._current_d()
        T = np.zeros((2*H, 2*H))
        b = np.zeros(2*H)
        yaw0, yr0, pitch0, pr0 = g0
        hist = list(self.buf[-d:]) if d > 0 else []
        if len(hist) < d:
            hist = [np.zeros(2)] * (d - len(hist)) + hist
        for k in range(H):
            b[2*k]   += yaw0 + yr0 * dt * (k+1)
            b[2*k+1] += pitch0 + pr0 * dt * (k+1)
            for m in range(k+1):
                j = m - d
                if j < 0:
                    u_past = hist[j + d] if (0 <= j + d < len(hist)) else np.zeros(2)
                    b[2*k]   += u_past[0] * dt * dt * (k - m + 1)
                    b[2*k+1] += u_past[1] * dt * dt * (k - m + 1)
                else:
                    T[2*k,   2*j]   += dt * dt * (k - m + 1)
                    T[2*k+1, 2*j+1] += dt * dt * (k - m + 1)
        return T, b

    def _ref_seq(self, t, estimator):
        ref = np.zeros((self.H, 2))
        for j in range(self.H):
            tt = t + (j+1)*self.dt
            horizon = (self.tau_fire + self.tau_flight_fn(tt)) if self.lead else 0.0
            pos = estimator.predict(horizon)
            ref[j] = az_el(pos, self.gimbal_pos)
        return ref

    def _solve(self, ref, g0):
        H = self.H
        T, b = self._build_prediction(g0)
        ref_flat = ref.reshape(-1)
        D = D_mat(H)
        Qs = np.kron(np.eye(H), np.sqrt(self.Q))
        Qs[2*(H-1):, :] *= np.sqrt(5.0)                 # terminal weight
        A = np.vstack([Qs @ T,
                       np.kron(np.eye(H), np.sqrt(self.R)) @ np.kron(D, np.eye(2))])
        c = np.concatenate([Qs @ (ref_flat - b),
                            np.kron(np.eye(H), np.sqrt(self.R)) @ np.tile(self.u_prev, H)])
        AtA = A.T @ A
        Atc = A.T @ c
        def fun(u):
            return float(u @ (AtA @ u) - 2.0 * u @ Atc)
        def grad(u):
            return 2.0 * (AtA @ u - Atc)
        if self.solver == "slsqp":
            C = np.kron(D_mat(H), np.eye(2))
            cons = [
                {"type": "ineq", "fun": lambda u: self.du_max - C @ u, "jac": lambda u: -C},
                {"type": "ineq", "fun": lambda u: self.du_max + C @ u, "jac": lambda u: C},
            ]
            u0 = np.tile(self.u_prev, H)
            res = minimize(fun, u0, jac=grad, method="SLSQP",
                           bounds=[(-self.acc_max, self.acc_max)] * (2*H),
                           constraints=cons, options={"maxiter": 15, "ftol": 1e-7})
            if not res.success:
                u, *_ = np.linalg.lstsq(A, c, rcond=None)
                return np.clip(u, -self.acc_max, self.acc_max).reshape(H, 2)
            return res.x.reshape(H, 2)
        # ADMM (box constraints; slope smoothness via R(du) cost)
        u0 = self.u_last.reshape(-1) if self.u_last is not None else np.tile(self.u_prev, H)
        lb = np.full(2*H, -self.acc_max); ub = np.full(2*H, self.acc_max)
        u = self._admm.solve(A, c, lb, ub, u0=u0)
        return u.reshape(H, 2)

    def step(self, t, gimbal, estimator, fs):
        ref = self._ref_seq(t, estimator)
        u_seq = self._solve(ref, gimbal.state())
        self.u_last = u_seq.copy()
        u = u_seq[0]
        self.u_prev = u.copy()
        if self.use_input_delay:
            self.buf.append(u.copy())
            if len(self.buf) > self.max_d:
                self.buf.pop(0)
        aim = ref[0]
        cur = gimbal.pointing()
        e = aim - cur
        margin = self._delay_margin(estimator) if self.tighten else 0.0
        fire = False
        if fs.can_fire(t) and (np.linalg.norm(e) + margin) < hit_tolerance(t, self.tau_flight_fn):
            fire = True; fs.fire(t)
        return u, fire

    def _delay_margin(self, estimator):
        """Angular margin from delay uncertainty: speed * (d_vision + d_gimbal) / dist."""
        if self.delay_est is None:
            return 0.0
        d_v = max(0.0, self.delay_est.vision.p95() - self.delay_est.vision.mean())
        d_g = max(0.0, self.delay_est.gimbal.p95() - self.delay_est.gimbal.mean())
        pos, vel = estimator.predict_pos_vel(0.0)
        speed = float(np.linalg.norm(vel))
        dist = float(np.linalg.norm(pos - np.asarray(self.gimbal_pos)))
        if dist < 1e-6:
            return 0.0
        return speed * (d_v + d_g) / dist


# ---------------------------------------------------------------------------
# v0.3: ADMM QP solver (box constraints; warm-started), tinympc-style.
# Solves  min_u  (Au-c)^T(Au-c)   s.t. lb <= u <= ub
# ---------------------------------------------------------------------------

class ADMMSolver:
    def __init__(self, rho=1.0, iters=80):
        self.rho = rho
        self.iters = iters
        self._L = None

    def _factor(self, A):
        n = A.shape[1]
        H = A.T @ A
        self._L = np.linalg.cholesky(H + self.rho * np.eye(n))
        self._At = A.T
        self._c = None

    def solve(self, A, c, lb, ub, u0=None):
        n = A.shape[1]
        if self._L is None or self._L.shape[0] != n:
            self._factor(A)
        rho = self.rho
        g = -(self._At @ c)
        z = u0.copy() if u0 is not None else np.zeros(n)
        w = np.zeros(n)
        L = self._L
        for _ in range(self.iters):
            b = rho * (z - w) - g
            u = np.linalg.solve(L.T, np.linalg.solve(L, b))
            z = np.clip(u + w, lb, ub)
            w = w + u - z
        return z


def D_mat(H):
    """Difference matrix mapping u_seq -> du (with u_prev as reference)."""
    D = np.zeros((H, H))
    for k in range(H):
        D[k, k] = 1.0
        if k > 0:
            D[k, k-1] = -1.0
    return D

class PlainMPC(MPC):
    name = "B1_PlainMPC"
    def __init__(self, **kw):
        kw["use_input_delay"] = False
        super().__init__(**kw)

class DelayAwareMPC(MPC):
    name = "Ours_DelayAwareMPC"
    def __init__(self, **kw):
        kw["use_input_delay"] = True
        super().__init__(**kw)

def hit_tolerance(t, tau_flight_fn):
    """Angular hit radius from armor half-width / distance (pre-registered)."""
    # distance unknown here; use fixed conservative tolerance for fire window.
    # Real hit check in metrics.py computes per-distance tolerance.
    return 0.05  # rad, fire-window threshold (conservative)
