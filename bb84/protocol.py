"""End-to-end BB84 run: transmission -> sifting -> QBER estimation."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .parties import Alice, Bob, Eve


@dataclass
class BB84Result:
    """Everything produced by one protocol run, for inspection and grading."""

    n_bits: int
    alice_bits: np.ndarray
    alice_bases: np.ndarray
    bob_bases: np.ndarray
    bob_results: np.ndarray
    sift_mask: np.ndarray            # True where Alice & Bob used the same basis
    sifted_alice: np.ndarray
    sifted_bob: np.ndarray
    qber: float
    eve_present: bool
    p_eve: float

    @property
    def n_sifted(self) -> int:
        return int(self.sift_mask.sum())

    @property
    def sift_ratio(self) -> float:
        return float(self.sift_mask.mean()) if self.n_bits else 0.0

    @property
    def theoretical_qber(self) -> float:
        """Ideal-channel prediction: QBER = p_eve / 4 (0 without Eve)."""
        return (self.p_eve / 4.0) if self.eve_present else 0.0


def run_bb84(
    n_bits: int = 2048,
    eve_present: bool = False,
    p_eve: float = 1.0,
    seed: int | None = None,
) -> BB84Result:
    """Simulate one full BB84 exchange and return a :class:`BB84Result`.

    Parameters
    ----------
    n_bits      : number of qubits Alice sends.
    eve_present : whether an eavesdropper sits on the quantum channel.
    p_eve       : fraction of qubits Eve intercepts (1.0 = every qubit).
    seed        : RNG seed for reproducibility.
    """
    rng = np.random.default_rng(seed)
    alice = Alice(n_bits, rng)
    bob = Bob(n_bits, rng)
    eve = Eve(n_bits, rng, p_eve) if eve_present else None

    # --- Quantum transmission over the channel ---------------------------
    for i, qubit in enumerate(alice.transmit()):
        if eve is not None:
            qubit = eve.intercept(i, qubit)    # measure-and-resend
        bob.measure(i, qubit)

    # --- Sifting: keep only positions where the two bases agree ----------
    # (bases are compared over a public classical channel; bit values stay secret)
    sift_mask = alice.bases == bob.bases
    sifted_alice = alice.bits[sift_mask]
    sifted_bob = bob.results[sift_mask]

    # --- QBER: mismatch fraction on the sifted key -----------------------
    qber = float(np.mean(sifted_alice != sifted_bob)) if sifted_alice.size else 0.0

    return BB84Result(
        n_bits=n_bits,
        alice_bits=alice.bits,
        alice_bases=alice.bases,
        bob_bases=bob.bases,
        bob_results=bob.results,
        sift_mask=sift_mask,
        sifted_alice=sifted_alice,
        sifted_bob=sifted_bob,
        qber=qber,
        eve_present=eve_present,
        p_eve=p_eve if eve_present else 0.0,
    )
