"""Target trajectory generators (ground truth) for RoboMaster auto-aim simulation."""
import numpy as np

class Trajectory:
    """Base: position(t) and velocity(t) in world frame (x forward, y left, z up)."""
    def position(self, t): raise NotImplementedError
    def velocity(self, t): raise NotImplementedError

class LineTraj(Trajectory):
    def __init__(self, p0, v, scale=1.0):
        self.p0 = np.asarray(p0, float); self.v = np.asarray(v, float) * scale
    def position(self, t): return self.p0 + self.v * t
    def velocity(self, t): return self.v

class CircleTraj(Trajectory):
    """Circle on the ground plane (x-y, z=0) around center -- target driving in a loop."""
    def __init__(self, center, radius, omega, phase=0.0, scale=1.0):
        self.c = np.asarray(center, float)
        self.r = radius; self.w = omega * scale; self.phi = phase
    def position(self, t):
        a = self.w * t + self.phi
        return self.c + np.array([self.r*np.cos(a), self.r*np.sin(a), 0.0])
    def velocity(self, t):
        a = self.w * t + self.phi
        return np.array([-self.r*self.w*np.sin(a), self.r*self.w*np.cos(a), 0.0])

class STraj(Trajectory):
    """Lateral S (sinusoidal) maneuver while advancing along x."""
    def __init__(self, p0, vx, amp, freq, scale=1.0):
        self.p0 = np.asarray(p0, float); self.vx = vx * scale
        self.amp = amp; self.freq = freq * scale
    def position(self, t):
        return self.p0 + np.array([self.vx*t, self.amp*np.sin(self.freq*t), 0.0])
    def velocity(self, t):
        return np.array([self.vx, self.amp*self.freq*np.cos(self.freq*t), 0.0])

class AccelTraj(Trajectory):
    """Piecewise acceleration: accel -> cruise (at v_cruise) -> decel -> rest.
    Reaches v_cruise at t=t_accel, cruises until t=2*t_accel, decelerates back
    to v0 by t=3*t_accel, then rests at v0."""
    def __init__(self, p0, v0, v_cruise, t_accel, scale=1.0):
        self.p0 = np.asarray(p0, float); self.v0 = np.asarray(v0, float) * scale
        self.vc = v_cruise * scale; self.ta = t_accel
        self.a = (self.vc - self.v0) / t_accel
    def _phase(self, t):
        if t <= self.ta: return "accel"
        if t <= 2*self.ta: return "cruise"
        if t <= 3*self.ta: return "decel"
        return "rest"
    def position(self, t):
        if t <= self.ta:
            return self.p0 + self.v0*t + 0.5*self.a*t*t
        p = self.p0 + self.v0*self.ta + 0.5*self.a*self.ta**2   # end of accel
        tt = t - self.ta
        if tt <= self.ta:                                        # cruise
            return p + self.vc*tt
        p = p + self.vc*self.ta                                  # end of cruise
        tt -= self.ta
        if tt <= self.ta:                                        # decel
            return p + self.vc*tt - 0.5*self.a*tt*tt
        p = p + self.vc*self.ta - 0.5*self.a*self.ta**2          # end of decel
        tt -= self.ta
        return p + self.v0*tt                                    # rest
    def velocity(self, t):
        ph = self._phase(t)
        if ph == "accel": return self.v0 + self.a*t
        if ph == "cruise": return self.vc
        if ph == "decel":
            tt = t - 2*self.ta
            return self.vc - self.a*tt
        return self.v0

def make_trajectory(name, scale=1.0):
    """Pre-registered scenario set (world frame)."""
    name = name.lower()
    if name == "line":
        return LineTraj(p0=[1.0, -0.6, 0.0], v=[1.2, 0.5, 0.0], scale=scale)
    if name == "circle":
        return CircleTraj(center=[3.0, 0.0, 0.0], radius=0.8, omega=0.8, phase=0.0, scale=scale)
    if name == "s":
        return STraj(p0=[1.0, 0.0, 0.0], vx=1.0, amp=0.9, freq=0.9, scale=scale)
    if name == "accel":
        return AccelTraj(p0=[1.0, -0.4, 0.0], v0=0.2, v_cruise=2.0, t_accel=1.0, scale=scale)
    raise ValueError(f"unknown trajectory: {name}")

def az_el(pos, gimbal_pos):
    """Azimuth (yaw) and elevation (pitch) of a point seen from gimbal position."""
    d = np.asarray(pos, float) - np.asarray(gimbal_pos, float)
    az = np.arctan2(d[1], d[0])
    r = np.linalg.norm(d[:2])
    el = np.arctan2(d[2], r)
    return np.array([az, el])

def ang_diff(a, b):
    d = a - b
    return np.arctan2(np.sin(d), np.cos(d))
