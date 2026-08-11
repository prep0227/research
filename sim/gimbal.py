"""Two-axis gimbal model: double integrator per axis + input delay + rate/accel limits.
Supports time-varying input delay via command history lookup: u_eff(t) = u(t - tau(t))."""
import numpy as np

class Gimbal:
    def __init__(self, dt=0.02, delay=0.06, acc_max=10.0, rate_max=6.0, init=(0.0, 0.0)):
        self.dt = dt
        self.delay = delay if callable(delay) else (lambda t: delay)
        self.acc_max = acc_max
        self.rate_max = rate_max
        self.yaw, self.pitch = init
        self.yaw_rate, self.pitch_rate = 0.0, 0.0
        self.history = []          # (t, u) applied commands

    def _effective(self, t):
        tau = max(0.0, float(self.delay(t)))
        t_apply = t - tau
        if not self.history:
            return np.zeros(2)
        ts = [h[0] for h in self.history]
        us = np.array([h[1] for h in self.history])
        if t_apply <= ts[0]:
            return us[0]
        idx = np.searchsorted(ts, t_apply) - 1
        idx = min(max(idx, 0), len(us)-1)
        return us[idx]

    def step(self, t, u):
        u = np.clip(np.asarray(u, float), -self.acc_max, self.acc_max)
        self.history.append((t, u))
        if len(self.history) > 2000:
            self.history.pop(0)
        u_eff = self._effective(t)
        self.yaw_rate = np.clip(self.yaw_rate + u_eff[0] * self.dt, -self.rate_max, self.rate_max)
        self.pitch_rate = np.clip(self.pitch_rate + u_eff[1] * self.dt, -self.rate_max, self.rate_max)
        self.yaw += self.yaw_rate * self.dt
        self.pitch += self.pitch_rate * self.dt
        return self.pointing()

    def pointing(self):
        return np.array([self.yaw, self.pitch])

    def state(self):
        return np.array([self.yaw, self.yaw_rate, self.pitch, self.pitch_rate])
