"""Delay-chain models: fixed and time-varying (jitter) vision/actuation delays."""
import numpy as np

class FixedDelay:
    def __init__(self, seconds): self.s = seconds
    def sample(self, t): return self.s

class UniformJitterDelay:
    """Uniform jitter around a nominal delay: U(lo, hi)."""
    def __init__(self, nominal, jitter):
        self.lo = nominal - jitter; self.hi = nominal + jitter
    def sample(self, t):
        return np.random.uniform(self.lo, self.hi)

class GammaJitterDelay:
    """Gamma-distributed delay with given mean and std (positive, skewed)."""
    def __init__(self, mean, std, seed=None):
        rng = np.random.default_rng(seed)
        k = (mean / std) ** 2
        theta = (std ** 2) / mean
        self.k = k; self.theta = theta; self.rng = rng
    def sample(self, t):
        return float(self.rng.gamma(self.k, self.theta))

def make_delay(mode, nominal, jitter=0.0, seed=None):
    mode = mode.lower()
    if mode == "fixed":
        return FixedDelay(nominal)
    if mode == "uniform":
        return UniformJitterDelay(nominal, jitter)
    if mode == "gamma":
        return GammaJitterDelay(nominal, jitter, seed=seed)
    raise ValueError(f"unknown delay mode: {mode}")
