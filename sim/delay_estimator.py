"""Online delay estimator: sliding-window mean / percentile."""
import numpy as np

class DelayEstimator:
    def __init__(self, window=50):
        self.window = window
        self.samples = []

    def add(self, value):
        self.samples.append(float(value))
        if len(self.samples) > self.window:
            self.samples.pop(0)

    def mean(self):
        return float(np.mean(self.samples)) if self.samples else 0.0

    def p95(self):
        return float(np.quantile(self.samples, 0.95)) if self.samples else 0.0

    def reset(self):
        self.samples = []
