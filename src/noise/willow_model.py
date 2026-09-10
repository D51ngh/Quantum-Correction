"""Reference-backed phenomenological parameters from Google's Willow experiment.

These values are measurements from the Willow surface-code experiment, not
generic defaults for every superconducting device. Component error rates that
the paper does not publish as scalar values are intentionally left to the user.

Source: Google Quantum AI, "Quantum error correction below the surface code
threshold", Nature 638, 920-926 (2025), DOI: 10.1038/s41586-024-08449-y.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class WillowParameters:
    """Measured Willow reference values and their units."""

    t1_us: float = 68.0
    t2_cpmg_us: float = 89.0
    qec_cycle_us: float = 1.1
    leakage_decay_cycles: float = 4.4
    p_det_by_distance: tuple[tuple[int, float], ...] = (
        (3, 0.077),
        (5, 0.085),
        (7, 0.087),
    )
    source: str = (
        "Google Quantum AI, Nature 638, 920-926 (2025), "
        "doi:10.1038/s41586-024-08449-y; Fig. 1 and Extended Data Fig. 1"
    )

    def relaxation_probability_per_cycle(self) -> float:
        """Amplitude-relaxation probability over one QEC cycle."""
        return 1.0 - math.exp(-self.qec_cycle_us / self.t1_us)

    def coherence_survival_per_cycle(self) -> float:
        """CPMG coherence-envelope survival over one QEC cycle."""
        return math.exp(-self.qec_cycle_us / self.t2_cpmg_us)

    def leakage_survival(self, rounds: int | float) -> float:
        """Survival of a leakage episode after ``rounds`` QEC cycles."""
        if rounds < 0:
            raise ValueError("rounds must be non-negative")
        return math.exp(-float(rounds) / self.leakage_decay_cycles)

    def leakage_persistence_stream(
        self, n_rounds: int, injection_probability: float, seed: int | None = None
    ) -> np.ndarray:
        """Sample a persistent leakage-state stream.

        The injection probability is explicit because Willow reports the
        leakage lifetime, but not a universal scalar leakage-injection rate.
        Returned values are leakage states, not detector events.
        """
        if n_rounds < 0:
            raise ValueError("n_rounds must be non-negative")
        if not 0.0 <= injection_probability <= 1.0:
            raise ValueError("injection_probability must be between 0 and 1")
        rng = np.random.default_rng(seed)
        survives = self.leakage_survival(1)
        active = False
        states = np.zeros(n_rounds, dtype=np.int8)
        for i in range(n_rounds):
            if active:
                active = bool(rng.random() < survives)
            elif rng.random() < injection_probability:
                active = True
            states[i] = int(active)
        return states
