"""Target state estimator: linear KF (CV model) with delayed measurements."""
import numpy as np

class TargetKF:
    """Constant-velocity KF on Cartesian position [x,y,z,vx,vy,vz].
    Handles delayed measurements: update at measurement time, then propagate to now.
    """
    def __init__(self, dt=0.02, q=0.6, r=0.03**2):
        self.dt = dt
        self.x = np.zeros(6)
        self.P = np.eye(6) * 1.0
        self.t = 0.0        # internal filter time
        self.q = q          # process noise accel PSD-ish
        self.r = r          # measurement noise variance (m^2)
        self.H = np.zeros((3, 6)); self.H[:3, :3] = np.eye(3)

    def _F(self, dt):
        F = np.eye(6)
        F[:3, 3:] = np.eye(3) * dt
        return F

    def _Q(self, dt):
        q = self.q
        d3 = dt**3 / 3.0; d2 = dt**2 / 2.0
        Q = np.zeros((6, 6))
        Q[:3, :3] = np.eye(3) * (q * d3)
        Q[:3, 3:] = np.eye(3) * (q * d2)
        Q[3:, :3] = np.eye(3) * (q * d2)
        Q[3:, 3:] = np.eye(3) * (q * dt)
        return Q

    def _propagate(self, dt):
        F = self._F(dt)
        Q = self._Q(dt) if dt >= 0 else np.zeros((6, 6))
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, z, t_now, t_meas):
        """z: noisy position measured at t_meas (<= t_now). OOSM: propagate to
        measurement time, update, then propagate to t_now. Tracks self.t."""
        self._propagate(t_meas - self.t)  # to measurement time (signed)
        self.t = t_meas
        S = self.H @ self.P @ self.H.T + np.eye(3) * self.r
        K = self.P @ self.H.T @ np.linalg.inv(S)
        y = np.asarray(z, float) - self.H @ self.x
        self.x = self.x + K @ y
        self.P = (np.eye(6) - K @ self.H) @ self.P
        self._propagate(t_now - t_meas)   # propagate to now
        self.t = t_now

    def likelihood(self, z):
        S = self.H @ self.P @ self.H.T + np.eye(3) * self.r
        y = np.asarray(z, float) - self.H @ self.x
        return _gauss_loglike(y, S)

    def predict(self, horizon):
        """Predict position at t_now + horizon."""
        F = self._F(horizon)
        return (F @ self.x)[:3]

    def predict_pos_vel(self, horizon):
        F = self._F(horizon)
        x = F @ self.x
        return x[:3], x[3:]


# ---------------------------------------------------------------------------
# v0.2: CT-EKF (constant turn rate, ground-plane 2D) and IMM (CV + CT)
# ---------------------------------------------------------------------------

class CTEKF:
    """Constant-turn-rate EKF on ground plane: state [x, y, vx, vy, w].
    Measurement: [x, y] (z handled separately / assumed known).
    Handles delayed measurements like TargetKF.
    """
    def __init__(self, dt=0.02, q=0.6, qw=0.05, r=0.03**2):
        self.dt = dt
        self.x = np.zeros(5)          # [x, y, vx, vy, w]
        self.x[4] = 0.0
        self.P = np.eye(5) * 1.0
        self.t = 0.0
        self.q = q; self.qw = qw; self.r = r
        self.H = np.zeros((2, 5)); self.H[0, 0] = 1.0; self.H[1, 1] = 1.0

    @staticmethod
    def f(x, dt):
        """Exact CT transition."""
        px, py, vx, vy, w = x
        wdt = w * dt
        if abs(wdt) < 1e-9:
            return np.array([px + vx*dt, py + vy*dt, vx, vy, w])
        s, c = np.sin(wdt), np.cos(wdt)
        px2 = px + (vx*s - vy*(1-c)) / w
        py2 = py + (vy*s + vx*(1-c)) / w
        vx2 = vx*c - vy*s
        vy2 = vx*s + vy*c
        return np.array([px2, py2, vx2, vy2, w])

    def _F(self, dt):
        # numeric Jacobian of f
        x = self.x
        F = np.zeros((5, 5))
        for j in range(5):
            dx = np.zeros(5); dx[j] = 1e-6
            F[:, j] = (self.f(x + dx, dt) - self.f(x - dx, dt)) / 2e-6
        return F

    def _Q(self, dt):
        q, qw = self.q, self.qw
        d3 = dt**3/3.0; d2 = dt**2/2.0
        Q = np.zeros((5, 5))
        Q[0,0] = q*d3; Q[0,2] = q*d2; Q[2,0] = q*d2; Q[2,2] = q*dt
        Q[1,1] = q*d3; Q[1,3] = q*d2; Q[3,1] = q*d2; Q[3,3] = q*dt
        Q[4,4] = qw*dt
        return Q

    def _propagate(self, dt):
        F = self._F(dt)
        Q = self._Q(dt) if dt >= 0 else np.zeros((5, 5))
        self.x = self.f(self.x, dt)
        self.P = F @ self.P @ F.T + Q

    def update(self, z, t_now, t_meas):
        self._propagate(t_meas - self.t)  # to measurement time (signed)
        self.t = t_meas
        S = self.H @ self.P @ self.H.T + np.eye(2) * self.r
        K = self.P @ self.H.T @ np.linalg.inv(S)
        y = np.asarray(z[:2], float) - self.H @ self.x
        self.x = self.x + K @ y
        self.P = (np.eye(5) - K @ self.H) @ self.P
        self._propagate(t_now - t_meas)   # to t_now
        self.t = t_now

    def likelihood(self, z):
        S = self.H @ self.P @ self.H.T + np.eye(2) * self.r
        y = np.asarray(z[:2], float) - self.H @ self.x
        return _gauss_loglike(y, S)

    def predict(self, horizon):
        p = self.f(self.x, horizon)[:2]
        return np.array([p[0], p[1], 0.0])




class CAKF:
    """Constant-acceleration KF on 3D Cartesian state [p, v, a] (9-dim)."""
    def __init__(self, dt=0.02, q=0.6, qj=1.5, r=0.03**2):
        self.dt = dt
        self.x = np.zeros(9)
        self.P = np.eye(9) * 1.0
        self.t = 0.0
        self.q = q; self.qj = qj; self.r = r
        self.H = np.zeros((3, 9)); self.H[:3, :3] = np.eye(3)

    def _F(self, dt):
        F = np.eye(9)
        F[:3, 3:6] = np.eye(3) * dt
        F[:3, 6:9] = np.eye(3) * 0.5 * dt**2
        F[3:6, 6:9] = np.eye(3) * dt
        return F

    def _Q(self, dt):
        q, qj = self.q, self.qj
        d5 = dt**5/20.0; d4 = dt**4/8.0; d3 = dt**3/6.0; d2 = dt**2/2.0
        Q = np.zeros((9, 9))
        Q[:3,:3] = np.eye(3)*qj*d5; Q[:3,3:6] = np.eye(3)*qj*d4; Q[:3,6:9] = np.eye(3)*qj*d3
        Q[3:6,:3] = np.eye(3)*qj*d4; Q[3:6,3:6] = np.eye(3)*qj*d3; Q[3:6,6:9] = np.eye(3)*qj*d2
        Q[6:9,:3] = np.eye(3)*qj*d3; Q[6:9,3:6] = np.eye(3)*qj*d2; Q[6:9,6:9] = np.eye(3)*qj*dt
        return Q

    def _propagate(self, dt):
        F = self._F(dt)
        Q = self._Q(dt) if dt >= 0 else np.zeros((9, 9))
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, z, t_now, t_meas):
        self._propagate(t_meas - self.t)
        self.t = t_meas
        S = self.H @ self.P @ self.H.T + np.eye(3) * self.r
        K = self.P @ self.H.T @ np.linalg.inv(S)
        y = np.asarray(z, float) - self.H @ self.x
        self.x = self.x + K @ y
        self.P = (np.eye(9) - K @ self.H) @ self.P
        self._propagate(t_now - t_meas)
        self.t = t_now

    def likelihood(self, z):
        S = self.H @ self.P @ self.H.T + np.eye(3) * self.r
        y = np.asarray(z, float) - self.H @ self.x
        return _gauss_loglike(y, S)

    def predict(self, horizon):
        return (self._F(horizon) @ self.x)[:3]

    def predict_pos_vel(self, horizon):
        x = self._F(horizon) @ self.x
        return x[:3], x[3:6]

class TargetIMM:
    """Multi-model Bayesian estimator (MMAE-style) with two models: CV-KF (3D)
    and CT-EKF (2D ground plane). Outputs a weighted mixture prediction with
    Markov prior on mode probabilities (no interactive mixing; see text).
    """
    def __init__(self, dt=0.02, q=0.6, qw=0.05, r=0.03**2, p_switch=0.05):
        self.dt = dt
        self.cv = TargetKF(dt=dt, q=q, r=r)
        self.ct = CTEKF(dt=dt, q=q, qw=qw, r=r)
        self.mu = np.array([0.5, 0.5])   # [P(CV), P(CT)]
        self.p_switch = p_switch

    def update(self, z, t_now, t_meas):
        self.cv.update(z, t_now, t_meas)
        self.ct.update(z, t_now, t_meas)
        l = np.array([self.cv.likelihood(z), self.ct.likelihood(z)])
        P = np.array([[1-self.p_switch, self.p_switch],
                      [self.p_switch, 1-self.p_switch]])
        mu_pred = P.T @ self.mu
        w = mu_pred * np.exp(np.clip(l, -50, 50))
        self.mu = w / (w.sum() + 1e-12)

    def predict(self, horizon):
        return (self.mu[0]*self.cv.predict(horizon) +
                self.mu[1]*self.ct.predict(horizon))

    def predict_pos_vel(self, horizon):
        p = self.predict(horizon)
        v = (self.mu[0]*self.cv.predict_pos_vel(horizon)[1] +
             self.mu[1]*np.array([self.ct.f(self.ct.x, horizon)[2], self.ct.f(self.ct.x, horizon)[3], 0.0]))
        return p, v


def _gauss_loglike(y, S):
    import numpy.linalg as la
    sign, logdet = la.slogdet(S)
    return -0.5 * (len(y)*np.log(2*np.pi) + logdet + y @ la.solve(S, y))
