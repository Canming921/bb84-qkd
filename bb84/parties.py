"""Protocol roles: Alice (sender), Bob (receiver), Eve (eavesdropper)."""
from __future__ import annotations

import numpy as np

from .qubit import BASES, measure, prepare


class Alice:
    """Sender. Draws a random bit string and a random basis string, then
    prepares one qubit per position encoding ``bit`` in ``basis``."""

    def __init__(self, n_bits: int, rng: np.random.Generator):
        self.rng = rng
        self.bits = rng.integers(0, 2, size=n_bits)
        self.bases = rng.choice(BASES, size=n_bits)

    def transmit(self):
        """Yield the prepared qubit for each position, in order."""
        for bit, basis in zip(self.bits, self.bases):
            yield prepare(int(bit), basis)


class Bob:
    """Receiver. Chooses a random measurement basis per position and records
    the outcome. He does *not* know Alice's bases until the public sift."""

    def __init__(self, n_bits: int, rng: np.random.Generator):
        self.rng = rng
        self.bases = rng.choice(BASES, size=n_bits)
        self.results = np.empty(n_bits, dtype=int)

    def measure(self, index: int, qubit: np.ndarray) -> int:
        outcome, _ = measure(qubit, self.bases[index], self.rng)
        self.results[index] = outcome
        return outcome


class Eve:
    """Eavesdropper running an intercept-resend attack.

    For each intercepted qubit she measures in a *randomly* chosen basis,
    which collapses the state, then forwards the post-measurement state to
    Bob. She has no information about Alice's basis choice, so half the time
    she measures (and resends) in the wrong basis and irreversibly disturbs
    the qubit -- this is what produces the detectable error rate.

    ``p_intercept`` lets her attack only a fraction of the qubits, which makes
    the QBER scale linearly with her activity (see docs/PHYSICS.md).
    """

    def __init__(self, n_bits: int, rng: np.random.Generator, p_intercept: float = 1.0):
        self.rng = rng
        self.p_intercept = p_intercept
        self.bases = np.full(n_bits, "", dtype=object)
        self.results = np.full(n_bits, -1, dtype=int)

    def intercept(self, index: int, qubit: np.ndarray) -> np.ndarray:
        if self.rng.random() >= self.p_intercept:
            return qubit                       # let this one pass untouched
        basis = self.rng.choice(BASES)
        outcome, collapsed = measure(qubit, basis, self.rng)
        self.bases[index] = basis
        self.results[index] = outcome
        return collapsed                       # resend the collapsed state
