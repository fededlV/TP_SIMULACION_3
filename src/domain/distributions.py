# Discretas/alias, sampleo, RNG}
from __future__ import annotations
import numpy as np
from typing import Sequence


class DiscreteSampler:
    def __init__(self, values: Sequence[int], probs: Sequence[float], rng: np.random.Generator):
        self.values = np.asarray(values)
        self.cum = np.cumsum(probs)
        self.rng = rng


    def sample(self) -> tuple[float, int]:
        u = self.rng.random()
        idx = np.searchsorted(self.cum, u, side='right')
        return float(u), int(self.values[idx])